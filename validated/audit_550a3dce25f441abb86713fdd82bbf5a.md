### Title
Webhook shop identity spoofing via unsigned `shop-domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-validating the raw request body, then dispatches the request to the app's handler using the `topic` and `shop` values taken from HTTP headers that are **not** part of the signed content. This breaks the binding `shop authenticated == shop acted upon`: the HMAC only covers `@raw_body`, while `request.shop` (read from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is trusted and forwarded to the handler unauthenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers and are never included in the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (i.e., the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` then raises only if this body-only HMAC fails, and afterwards uses the **unsigned** `request.topic` and `request.shop` to look up the handler and build the payload passed to the app's business logic: [4](#0-3) 

Because the HMAC never binds `shop-domain` to the body, any party in possession of one valid `(body, hmac)` pair for the app's shared secret — most simply, a legitimate merchant of the app who receives real webhooks for their own store — can resend that identical body+HMAC pair to the app's webhook endpoint while substituting a different `shop-domain` header value. `HmacValidator.validate` will still return `true` because the signature check never inspects the header. `Registry.process` will then invoke the handler with `WebhookMetadata` carrying the attacker-chosen `shop`, `topic`/`webhook_id`, and the original body — i.e., data that is falsely attributed to a shop other than the one that actually produced it.

This is the exact bug class from the reference report: a value (`shop`) that is "acted on" (used to route/attribute webhook data) is not covered by the integrity check (`HMAC`) that is supposed to authenticate the whole message, allowing the identity binding `hmac-authenticated body == shop-domain header` to be forged.

### Impact Explanation
This crosses a tenant boundary: it allows one shop (a merchant/user of the multi-tenant app built on this gem) to have webhook events falsely attributed to a different shop, corrupting per-tenant data attribution and letting one tenant inject/associate events into another tenant's record purely by re-sending a body they legitimately received, with a forged header. This matches the "cross-tenant access" high-impact category — the app's webhook processing pipeline can be made to believe events for shop A originated from shop B, without needing the app's `api_secret_key` (the attacker never needs the secret; they just need one legitimately-received signed body from their own shop).

### Likelihood Explanation
Medium-to-High: any onboarded merchant of the app already receives fully valid `(body, hmac-sha256)` pairs for their own shop as part of normal webhook delivery. Replaying that pair to the app's own public webhook endpoint with a modified `shop-domain` header is a simple, unauthenticated HTTP request — no cryptographic material or privileged access is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api-version) inside the HMAC-covered signable content, or otherwise cryptographically bind the `shop-domain` header to the verified payload before trusting it, e.g., by having `to_signable_string` incorporate `shopify_header("shop-domain")` (and other dispatch-critical headers) alongside the body, and rejecting requests where these headers cannot be verified. At minimum, document/enforce that consumers must cross-check `request.shop` against an existing, independently-established tenant record before trusting it for attribution, and consider validating `request.shop` with `Utils::ShopValidator.sanitize!` to reduce spoofing to only real Shopify domains (though this alone will not stop a shop from claiming to be a *different* real Shopify domain).

### Proof of Concept
1. App merchant "attacker-shop.myshopify.com" installs the app and receives a legitimate webhook, e.g.:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body-for-attacker-shop>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: abc-123

   {"id": 1, "total_price": "9.99", ...}
   ```
2. The merchant captures this exact `body` and `x-shopify-hmac-sha256` value (both valid, since HMAC is computed only over the body using the shared `api_secret_key`).
3. The merchant crafts a new request to the app's webhook endpoint, keeping the body and HMAC identical, but changes the header:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `body` against `hmac-sha256`, per:
   `lib/shopify_api/utils/hmac_validator.rb:12-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
5. `Registry.process` proceeds to invoke the registered handler with `shop: request.shop`, i.e., `"victim-shop.myshopify.com"`, per `lib/shopify_api/webhooks/registry.rb:188-200`, even though the body actually came from and was signed for "attacker-shop.myshopify.com". The app's handler now processes/stores the event as if it belonged to "victim-shop.myshopify.com".

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
