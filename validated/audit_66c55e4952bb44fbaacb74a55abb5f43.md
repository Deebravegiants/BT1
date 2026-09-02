### Title
Webhook shop identity spoofing via HMAC that only signs the body, not the `shop-domain` header - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's webhook handler come from HTTP headers that are never covered by that HMAC, so any party who can obtain one valid `(raw_body, hmac)` pair can replay it with a forged `shop-domain` header and make the app process the body as if it belongs to an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` computes its signable value strictly from the body: [1](#0-0) [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers with no cross-check against the signed content: [3](#0-2) 

`Utils::HmacValidator.validate` verifies only `to_signable_string` (the raw body) against the secret — it never touches headers: [4](#0-3) 

`Registry.process` uses this HMAC check as the sole authentication gate, then immediately trusts `request.shop` (header-derived) to build the `WebhookMetadata` passed to the app's handler: [5](#0-4) 

The broken identity binding, expressed as an equality that the gem fails to enforce:
`shop_bound_by_hmac (∅, not present in to_signable_string) ≠ shop_delivered_to_handler (request.shop, taken from the unauthenticated x-shopify-shop-domain header)`.

Because `Context.api_secret_key` is the app's single `client_secret` shared across every shop that has installed the app (not a per-shop key), a valid `(body, hmac)` pair computed for one tenant's webhook delivery remains cryptographically valid for that same body regardless of which shop header accompanies it. An attacker who is a legitimate merchant of the app (an "unprivileged internet user" relative to any other tenant) will naturally receive real webhook deliveries for their own shop with valid HMACs over bodies whose content they can influence (e.g. by editing an order, customer, or product before the webhook fires). They can then resend that exact `raw_body` + `x-shopify-hmac-sha256` value to the app's webhook endpoint while substituting `x-shopify-shop-domain` (or `shopify-shop-domain`) with a victim shop's domain. `HmacValidator.validate` still passes because it only checks the body, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: request.shop, ...)` where `shop` is the attacker's forged header value.

### Impact Explanation
This breaks the tenant boundary that `Registry.process` is documented to enforce ("verify the request did indeed come from Shopify" — implicitly for the claimed shop). An app that keys its persistence/business logic off `WebhookMetadata#shop` (the pattern shown in the gem's own webhook docs and tests) will apply attacker-partially-controlled webhook content to another merchant's tenant data, which is cross-tenant access/injection — a Critical-severity outcome per the scope's impact list.

### Likelihood Explanation
Exploitation requires only that the attacker (1) operate a shop that has the app installed (an ordinary merchant, not a privileged party) and (2) be able to POST to the app's public webhook endpoint, both of which are normal, low-privilege capabilities for any app using this gem. No access token, `api_secret_key`, or other Shopify credential needs to be stolen — only observation of one's own legitimately-received webhook deliveries, which the attacker already receives as part of using the app.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-covered signable content, or otherwise require the caller to cross-verify `request.shop` against an out-of-band trusted identifier (e.g. reconcile against the shop associated with the specific webhook subscription/registration ID) before invoking the handler. At minimum, `Utils::VerifiableQuery#to_signable_string` for `Webhooks::Request` should incorporate the shop-domain header so a body/HMAC pair cannot be replayed under a different tenant's identity.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and edits an order/customer such that Shopify sends a real webhook whose JSON body contains attacker-chosen field values (e.g. a note or metafield holding a script/marker), which arrives with `x-shopify-hmac-sha256` valid for that body under the shared `client_secret`.
2. Attacker captures `raw_body` and the `x-shopify-hmac-sha256` header from this legitimate delivery.
3. Attacker POSTs to the app's webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`/`x-shopify-webhook-id`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [6](#0-5) , which returns `true` because only the body is checked [7](#0-6) .
5. The registered handler is invoked with `WebhookMetadata` whose `shop` is `victim-shop.myshopify.com`, even though the body actually originated from and was signed for `attacker-shop.myshopify.com` [8](#0-7) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
