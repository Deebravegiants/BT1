Confirmed: `Registry.process` passes `request.shop` (from the unsigned header) directly into `WebhookMetadata` at [1](#0-0) , and `WebhookMetadata.shop` is a trusted `const :shop, String` field [2](#0-1)  that host applications use to identify which merchant/tenant the webhook data belongs to. The `hmac` field is computed from the `hmac-sha256` header while the shop identity comes from a separate, unauthenticated `shop-domain` header — and the signable string covers only the raw body [3](#0-2) .

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant shop-spoofing on replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from the `x-shopify-shop-domain` (or `shopify-shop-domain`) HTTP header, but the HMAC signature that `Registry.process` validates is computed only over the raw request body [4](#0-3) . The `shop` header is never included in `to_signable_string`, so it is not bound by the signature at all.

### Finding Description
`Utils::HmacValidator.validate` checks that `computed_signature = HMAC(secret, verifiable_query.to_signable_string)` matches the `hmac` header [5](#0-4) . For webhooks, `to_signable_string` returns only `@raw_body` [4](#0-3) , while `shop` is read straight from the `shop-domain` header with no cryptographic binding to that body [6](#0-5) .

`Registry.process` validates the HMAC and then forwards `request.shop` unchanged into `WebhookMetadata`, which the host app's `WebhookHandler#handle` uses to attribute the webhook body to a merchant/tenant [1](#0-0) .

This is precisely the "field acted on but not covered by the HMAC" identity-binding gap: the equality the code implicitly assumes is `shop_header == shop_that_produced(raw_body)`, but nothing enforces it — `hmac` proves only `raw_body` is untampered under the shared `client_secret`, not that `shop_header` is the shop that actually generated it.

Because the `client_secret` (and therefore the HMAC key) is shared across every merchant install of a given app, any unprivileged user who installs the app on their own store receives genuinely-signed webhooks for their own shop. They can capture one such webhook (valid `hmac-sha256` for a given raw body) and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header swapped to a victim shop's domain. The signature still validates (it only covers the body), yet `WebhookMetadata.shop` now claims to be the victim shop.

### Impact Explanation
This crosses a tenant boundary using only the attacker's own legitimately-signed data: the app's webhook handler will process attacker-controlled body content as if it originated from a different, victim merchant, since `shop` is trusted as an authenticated identity without being part of the signed payload. Depending on how the host app's handler uses `data.shop` (e.g., to look up per-shop session/config or to write per-shop records), this enables cross-tenant data confusion/injection — matching the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Any user can install the target app on a shop they control (unprivileged, no special access needed), which is enough to obtain a validly HMAC-signed webhook body under the app's shared secret. No `api_secret_key`, access token, or credential theft is required — only replaying a header value that was never protected by the signature in the first place.

### Recommendation
Include the `shop` (and ideally `topic`, `api_version`, `webhook_id`) header values in the HMAC-signable string, or otherwise cryptographically bind the shop domain to the signed payload, so `Utils::HmacValidator.validate` cannot pass when the `shop-domain` header has been altered independently of the body it was issued with. At minimum, document that `WebhookMetadata.shop` is unauthenticated header data and must not be trusted for cross-tenant identification without an out-of-band check (e.g., cross-referencing against the shop associated with the caller's own stored session/webhook registration).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook, e.g. `orders/create`, receiving a POST with headers `x-shopify-hmac-sha256: <valid hmac>`, `x-shopify-shop-domain: attacker.myshopify.com`, and some `raw_body`.
2. Attacker resends the identical request to the app's webhook endpoint, only changing `x-shopify-shop-domain` to `victim.myshopify.com`, keeping `raw_body` and `x-shopify-hmac-sha256` unchanged.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (i.e., `raw_body` only) and finds it matches [7](#0-6) .
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)` and processes attacker data under the victim's tenant identity [8](#0-7) .

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

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
