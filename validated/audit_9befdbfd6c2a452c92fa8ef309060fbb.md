This confirms the strongest analog: the webhook `shop` (and `topic`) fields are read directly from HTTP headers, while the HMAC only covers the raw body via `to_signable_string` returning `@raw_body` [1](#0-0) . `Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) unconditionally to dispatch the payload to the app's handler [2](#0-1) .

### Title
Webhook `shop` header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body (`to_signable_string` returns `@raw_body`), while `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers that are never included in the signed content [3](#0-2) . `HmacValidator.validate` only checks `verifiable_query.hmac` against `to_signable_string` computed over the body [4](#0-3) . This is analogous to the CKB bug class: a value used for a critical identity/routing decision (`shop`) is not actually covered by the same bytes that were cryptographically verified — the equality the code relies on (`hmac_verified_bytes == bytes_used_for_shop_identity`) does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates the webhook HMAC and then immediately trusts `request.shop` to build `WebhookMetadata`, which is handed to the app-supplied handler [5](#0-4) . Because `shop` (and `topic`) come from the `x-shopify-shop-domain`/`shopify-shop-domain` header rather than the HMAC-signed body, an attacker who possesses one genuine, validly-signed webhook payload (e.g., because they operate their own shop installed on the same app, and thus legitimately receive webhooks for their own body content) can resend that exact `raw_body`+`hmac` pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header value. Since `HmacValidator.validate` only checks the body against the HMAC — never the shop header — the forged request passes signature validation. `Registry.process` then dispatches to the handler believing the event originates from the spoofed shop, breaking the binding `hmac_verifies(body) == hmac_verifies(shop_that_the_app_will_act_on)`.

### Impact Explanation
This enables cross-tenant webhook injection: a handler that uses `WebhookMetadata#shop` to look up/act on the wrong merchant's session, data, or state (e.g., processing `shop/redact`, `customers/redact`, order or app-uninstall events) can be manipulated by an unprivileged internet user who controls at least one legitimate shop on the app, without needing the app's `client_secret` or any privileged credential. This matches the "cross-tenant access" high-severity criterion.

### Likelihood Explanation
Medium: the attacker needs one legitimate signed webhook body (achievable by installing the app on their own store, which is normal unprivileged usage), and the app's webhook endpoint must be reachable from the internet (true by design, since Shopify posts webhooks over HTTP). No secret, token, or privileged access is required — only replay of a body they already legitimately received, with a forged header.

### Recommendation
Incorporate `shop`, `topic`, `api_version`, and `webhook_id` into the HMAC-signable content (or otherwise cryptographically bind them, e.g., by validating them against a previously-established session/shop record) so that `to_signable_string` covers every field the handler acts on, not just the raw body.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook POST with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B`).
2. Attacker resends `POST /webhooks` with the same body `B` and the same `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` passes because it only checks `B` against `H` [4](#0-3) .
4. `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` [6](#0-5) , causing the app to process attacker-controlled event data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
