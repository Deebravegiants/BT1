Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates the HMAC of only the body and then dispatches the handler using the unvalidated `request.shop` and `request.topic` values [3](#0-2) . This is enough to answer.

### Title
Webhook shop/topic identity spoofing via HMAC that covers only the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers that are never covered by the HMAC signature check. `ShopifyAPI::Utils::HmacValidator.validate` only verifies the raw request body against `Context.api_secret_key`, so an attacker who possesses one genuine (body, HMAC) pair signed by Shopify for the app's own shared `client_secret` can replay that body with arbitrary `shopify-shop-domain` / `shopify-topic` header values and it will still pass validation.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from attacker-controllable HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC using `verifiable_query.to_signable_string`, i.e. the body alone: [4](#0-3) 

`Registry.process` gates on this HMAC check and then hands the *unauthenticated* `request.shop` and `request.topic` straight to the app's handler as trusted identity metadata: [3](#0-2) 

Because the app's Shopify `client_secret` (`Context.api_secret_key`) is shared across all shops/tenants of the app, any tenant that installs the app can trigger a webhook for their own store, capture the legitimate `(body, x-shopify-hmac-sha256)` pair Shopify sends them, and then replay that exact body/HMAC pair while substituting a different `shopify-shop-domain` header (and/or `shopify-topic`) value. `HmacValidator.validate` will still return `true` because it only checks the body bytes — the equality the code implicitly assumes, "shop header == shop that produced this signed body", is never enforced. This breaks the tenant-identity binding that `Registry.process` relies on to route webhook data to the correct shop's handler logic.

### Impact Explanation
This crosses a tenant boundary: an attacker (any shop that installs the app) can cause the app to process webhook payloads under an arbitrary victim `shop-domain` value it does not control, using a body that is only guaranteed authentic-from-Shopify in general (HMAC signed with the app's secret) but not authentic-for-that-shop. Depending on how the host app's registered handler uses `WebhookMetadata#shop` (e.g. `app/uninstalled`, `shop/redact`, `customers/redact`, or subscription/billing topics), this can lead to cross-tenant state corruption — e.g. deactivating, deleting, or mutating data belonging to a shop the attacker never installed the app on. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even free/trial) installer of the app on their own shop — no `api_secret_key`, access token, or privileged account is needed, since the attacker leverages a real webhook Shopify sends to their own installation. Constructing the replay only requires resending the captured body with a modified header, which any unprivileged internet user capable of installing the target app can do.

### Recommendation
Include the shop domain (and ideally the topic/webhook id) in the HMAC-covered signable string, or otherwise cryptographically bind the header-derived identity fields to the signed payload before trusting them in `Registry.process`. At minimum, cross-check `request.shop` against a shop the app has an active, previously-established session/installation for before dispatching the handler.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify sends a genuine webhook to the app with headers `x-shopify-hmac-sha256: <valid-hmac>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, and some `raw_body`.
2. Capture `raw_body` and the valid `x-shopify-hmac-sha256` value.
3. Replay a request to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim.myshopify.com` (and/or change `x-shopify-topic` to a more impactful topic the attacker also has legitimate access to, e.g. `app/uninstalled`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against `Context.api_secret_key`: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim.myshopify.com", ...)` and performs whatever tenant-scoped action the app implements for that topic, against `victim.myshopify.com`, despite the attacker never having installed on/authorized for that shop.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
