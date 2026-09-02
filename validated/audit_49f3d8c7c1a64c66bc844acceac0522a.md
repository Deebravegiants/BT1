This confirms the vulnerability. `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read from separate, unsigned HTTP headers [2](#0-1) . `Registry.process` validates only this body-only HMAC and then trusts `request.shop` to build `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Title
Webhook HMAC does not bind the `shop-domain` header, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content as the raw request body only, never including the `shop-domain` (or `topic`/`webhook-id`) header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to construct the `WebhookMetadata` delivered to the host app's webhook handler. Because the HMAC signature never binds the shop identity, any party who can obtain one validly-signed webhook body/HMAC pair (e.g., from their own shop's legitimate webhook delivery) can resubmit it with an arbitrary `shopify-shop-domain` header value, and it will still pass HMAC validation while being attributed to a different, attacker-chosen shop.

### Finding Description
The equality that should hold is: `shop authenticated by HMAC == shop used by the application to identify the tenant`. In this codebase that equality is broken:

- `to_signable_string` only returns `@raw_body`: [1](#0-0) 
- `shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic binding: [4](#0-3) 
- `HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and the shared `api_secret_key`: [5](#0-4) 
- `Registry.process` validates this body-only HMAC, then builds `WebhookMetadata` straight from the unauthenticated `request.shop`, and dispatches it to the host app's handler: [3](#0-2) 

Since the `api_secret_key` used to compute the HMAC is the same shared secret across every shop that installs the app, a legitimate, valid `(body, hmac)` pair generated from any one shop's webhook delivery remains cryptographically valid regardless of which `shop-domain` header accompanies it. An attacker who installs the app on their own shop (an ordinary, unprivileged merchant relative to other tenants of the same app) receives real webhook deliveries with valid HMACs computed over the body. They can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the victim shop's domain in the `shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because it never looks at the shop header, so `Registry.process` proceeds and calls the host application's `handle` with `WebhookMetadata#shop` set to the victim's domain, while the `body` is data belonging to the attacker's own shop.

### Impact Explanation
This breaks the tenant boundary the webhook mechanism is supposed to enforce: an app relying on this gem's webhook signature verification to determine "which merchant does this event belong to" can be made to associate attacker-controlled webhook content with a different, victim shop identifier. Depending on how the host application keys its data storage or triggers actions per-`shop`, this enables cross-tenant data confusion/injection under a victim's identity — matching the Critical "cross-tenant access" impact category, since the trust boundary between distinct app installations/tenants is bypassed via the gem's own verification primitive.

### Likelihood Explanation
Likelihood is high for any app that only relies on `ShopifyAPI::Utils::HmacValidator.validate(request)` as its authenticity check (as this gem's own `Registry.process` does) and trusts `request.shop`/`WebhookMetadata#shop` without a secondary check tying the header to the signed payload. Any unprivileged actor who can install the app onto a shop they control (a normal, low-privilege capability for any Shopify merchant/developer) can capture one legitimate webhook and replay it with a forged shop header — no access token, `client_secret`, or elevated privilege is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signable content, or otherwise cryptographically bind the `shopify-shop-domain` header value into the value validated by `HmacValidator`, so that `to_signable_string` cannot be satisfied by a body/HMAC pair captured from a different shop. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must be independently cross-checked (e.g., against a shop the app has an active session for) before being trusted as a tenant identifier.

### Proof of Concept
1. App has two installations: Shop A (attacker-controlled) and Shop B (victim), both handled by the same app instance sharing one `api_secret_key`.
2. Shopify sends a legitimate webhook to the app for Shop A: headers include `shopify-shop-domain: shop-a.myshopify.com`, body `B`, and `shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker (who legitimately receives this webhook, e.g., by triggering an event on their own shop, or intercepting/logging their own webhook deliveries) resends the same body `B` and the same `hmac-sha256` value to the app's webhook endpoint, but replaces the `shopify-shop-domain` header with `shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged request; `hmac` still decodes correctly, `shop` returns `"shop-b.myshopify.com"` per [4](#0-3) .
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` from `to_signable_string` (the raw body) and matches the supplied HMAC, returning `true` — see [6](#0-5) .
6. The host app's handler is invoked with `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: B, ...)` — Shop A's data is now processed under Shop B's identity, despite the signature check having "passed".

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
