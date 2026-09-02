### Title
Webhook shop identity spoofing — HMAC signs only the raw body, not the `shop-domain`/`topic`/`webhook-id` headers used for tenant attribution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` returns only `@raw_body`. The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from unauthenticated HTTP headers and are never included in the HMAC computation, yet they are trusted downstream to identify which tenant/shop a webhook event belongs to.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined as: [1](#0-0) 

`to_signable_string` returns only `@raw_body`. `Utils::HmacValidator.validate` computes the signature exclusively over this signable string and the app's `api_secret_key`: [2](#0-1) 

`Registry.process` verifies only this body HMAC, then dispatches the handler using `request.shop`, `request.topic`, and `request.webhook_id` — all pulled straight from headers with no cryptographic binding: [3](#0-2) 

The identity binding that should hold is:
`shop_that_HMAC_authenticates == shop_used_by_handler.handle(...)`

In this implementation, the left side is undefined — the HMAC never covers `shop`, so the equality is broken. The right side is populated entirely from the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header, which is attacker-controllable in a replay.

Because the same `(raw_body, hmac)` pair remains valid for any header combination, a valid, Shopify-signed webhook delivery obtained by an unprivileged actor for their *own* shop (e.g. a free development/partner test store, which requires no special privilege or leaked credential) can be replayed verbatim against the same app endpoint with the `shop-domain` header changed to an arbitrary target shop. `HmacValidator.validate` still passes because it checks only the body bytes, and `Registry.process` attributes the event to the attacker-chosen `shop` value, crossing the tenant boundary that the HMAC is supposed to enforce.

### Impact Explanation
This is a cross-tenant integrity failure: the app's webhook handlers key their business logic (e.g., session/data cleanup on `app/uninstalled`, GDPR data requests, order/customer processing) by `WebhookMetadata#shop`, which is fully forgeable independent of the valid HMAC. An attacker who owns any shop where the app is installed can inject events that the app believes originate from a different, victim shop, since the HMAC never binds shop identity. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any attacker able to install the app on a shop they control (no special privilege, leaked secret, or social engineering required) and capture one legitimate webhook delivery to replay with a modified header. No knowledge of `api_secret_key` is needed because the original signature is reused unmodified.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed payload used by `Request#to_signable_string`, or otherwise cryptographically bind the shop domain to the verified content before it is trusted by `Registry.process` / `WebhookMetadata`.

### Proof of Concept
1. Install the app on attacker-controlled Shop A (any unprivileged developer/partner test store).
2. Register a webhook topic (e.g., `orders/create`) and capture Shopify's legitimate delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Replay the exact same `B`/`H` pair to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and, if desired, `X-Shopify-Topic`/`X-Shopify-Webhook-Id` to match a different event).
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only checks `B` against `H`. `Registry.process` (`lib/shopify_api/webhooks/registry.rb#L188-199`) then calls the handler with `shop: "victim-shop.myshopify.com"`, even though that shop never sent this event.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
