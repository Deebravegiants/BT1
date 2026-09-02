Based on my investigation, I found a genuine identity-binding gap in the webhook processing path.

### Title
Webhook HMAC signature does not bind the `shop`/`topic`/`webhook_id` headers, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `ShopifyAPI::Webhooks::Registry.process` validates that HMAC and then trusts `request.shop` (parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header) to construct `WebhookMetadata` passed to the app's handler [2](#0-1) . The shop-domain header is never covered by the HMAC signature.

### Finding Description
The identity binding that should hold is: `shop header == shop that the HMAC-signed body actually belongs to`. Instead, `HmacValidator.validate` only checks `OpenSSL.secure_compare(computed_signature, hmac)` where `computed_signature` is derived solely from `verifiable_query.to_signable_string`, which for `Webhooks::Request` is just the raw body [3](#0-2) [4](#0-3) . The `shop`, `topic`, and `webhook_id` accessors are read directly from unauthenticated headers [5](#0-4) .

Because every shop that installs the same app shares the same `api_secret_key`, any merchant who installs the app on their own store (an unprivileged, legitimately-authenticated actor with respect to their own tenant) can capture a genuinely Shopify-issued, validly-HMAC-signed webhook body+signature pair for their own shop, then resend that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a different, victim shop's domain (and optionally a different `webhook-id`/`topic` value that was valid for their own delivery). `HmacValidator.validate` will still succeed because it never inspects the shop/topic/webhook_id headers, and `Registry.process` will hand `WebhookMetadata.new(topic:, shop: request.shop, body:, ...)` to the handler as if it legitimately originated from the victim shop [2](#0-1) .

### Impact Explanation
Host applications are documented to key their webhook processing directly off `data.shop` (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [6](#0-5) . Because this gem provides no protection binding the shop identity to the signed payload, an attacker who controls one shop (obtained through the normal, unprivileged app-install flow) can make the host application attribute another shop's data mutation, deletion, or GDPR-style redact webhook (`shop/redact`, `customers/redact`, `customers/data_request`) to a victim tenant, resulting in cross-tenant data corruption/impersonation — satisfying the "cross-tenant access" Critical impact bucket.

### Likelihood Explanation
The attacker needs only to be a legitimate merchant/user of the app on their own store — no secret leakage, TLS interception, or privileged access is required. They passively receive a real webhook delivery for their own shop (which they are entitled to receive) and replay the identical body/HMAC bytes with a forged shop-domain header directly to the app's public webhook endpoint. This is straightforward to automate and repeat for arbitrary target shop domains that use the same app.

### Recommendation
Include the shop-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the HMAC-covered signable content, or otherwise cryptographically bind them (e.g., re-derive/validate `shop` from a source that is itself covered by the HMAC, or cross-check against the shop associated with the webhook subscription that was registered for a given `webhook_id`) before handing `WebhookMetadata` to the handler, rather than trusting the raw, unauthenticated `shopify-shop-domain` header as-is.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and subscribes to a webhook topic (e.g. `customers/redact`).
2. Shopify delivers a legitimate webhook to the app: body `B`, header `x-shopify-hmac-sha256: H` (where `H = HMAC-SHA256(api_secret_key, B)`), `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` and re-sends a POST directly to the app's public webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and finds it equal to `H`, so validation passes.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host application to process attacker-controlled data as if it belonged to the victim shop.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
