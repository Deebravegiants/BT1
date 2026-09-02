### Title
Webhook `shop`/`topic` fields are trusted for tenant dispatch despite being excluded from the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop-domain` header (and `topic`, `webhook-id`, `api-version`) are read directly from unauthenticated HTTP headers and forwarded to the app's webhook handler as trusted tenant-identifying metadata. Because the HMAC never covers these headers, any actor capable of producing one validly-signed webhook body/HMAC pair for the shared app `client_secret` (e.g. via their own legitimately installed store) can replay that exact body with a different `shop-domain` header and still pass `Utils::HmacValidator.validate`, causing `Registry.process` to invoke the merchant's webhook handler with an attacker-chosen `shop` value.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the signed payload: [2](#0-1) 

`HmacValidator.validate` only verifies `hmac` against `to_signable_string` (the raw body), so it never validates `shop`, `topic`, or the other headers: [3](#0-2) 

`Registry.process` trusts the unauthenticated `request.shop` and passes it straight into the handler's metadata after only checking the body HMAC: [4](#0-3) 

The equality this breaks: `shop_bound_by_hmac == shop_acted_on` is false — the HMAC binds `{secret, raw_body}`, but the identity used to route/act on the webhook (`data.shop`) comes from `request.shop`, a value entirely outside that signed set. Since the HMAC secret (`api_secret_key`/`client_secret`) is shared across every merchant/shop the app serves (it's not shop-specific), anyone who can obtain one valid `(raw_body, hmac)` pair — trivially available to any user who installs the app on their own store and lets Shopify deliver a real webhook to their endpoint — can resend that identical body/HMAC pair while substituting the `shop-domain` header to any other store name. `Utils::HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` dispatches to the handler with the forged shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: an unprivileged actor (any user who can install the app on a store they control, i.e. no `api_secret_key`, access token, or privileged account required) can cause the host application's webhook handler to process/act on data while believing it originates from an arbitrary victim shop. Depending on the handler logic (which the gem's documentation explicitly instructs developers to trust `WebhookMetadata#shop` for), this can lead to cross-tenant data corruption or unauthorized actions being attributed to another merchant's shop — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any app author following the library's documented pattern: the only prerequisite is capturing one legitimate webhook delivery (obtainable by installing the app on an attacker-owned test store) and replaying it with a modified `shop-domain` header to the app's public webhook endpoint. No secrets, tokens, or elevated privileges are needed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind them to the verified `raw_body`/session before dispatch. At minimum, `Registry.process` should cross-check `request.shop` against a shop that the app has an active, previously-established session/installation record for, rather than trusting the header value outright once the body HMAC passes.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com` and register (or simply receive) a webhook for a topic the app handles; capture the raw POST body `B` and its `x-shopify-hmac-sha256` header value `H` (valid because it's signed with the app's single shared `client_secret`).
2. Replay an HTTP POST to the app's webhook endpoint with the same body `B` and header `H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `Utils::HmacValidator.validate` succeeds (only `B`/`H` are checked), and `Registry.process` invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
