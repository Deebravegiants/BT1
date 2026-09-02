### Title
Webhook `shop` domain used for tenant attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates only covers the raw request body, not the headers. This breaks the intended binding `hmac(secret, body) == authenticated(shop)`: a valid signature only proves the body was produced with the app's secret, it says nothing about which shop the body belongs to. Any party capable of triggering one legitimate webhook delivery for their own (unprivileged) shop can reuse that exact signed body while substituting an arbitrary `shop-domain` header, and the gem will pass the forged shop identity straight to the app's `WebhookHandler`.

### Finding Description
`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator` computes/compares the signature only against `to_signable_string`: [2](#0-1) 

For webhook requests, `to_signable_string` returns solely the raw body, while `shop` is read from a separate, unsigned header: [3](#0-2) [4](#0-3) 

Because `shop` is outside the signed material, `HmacValidator.validate` will return `true` for any `shop-domain` header value paired with a body/HMAC pair that was legitimately generated for a *different* shop. `Registry.process` then forwards this unauthenticated `shop` value directly into `WebhookMetadata`, which the documented handler pattern treats as the trusted tenant identifier for routing/storage: [5](#0-4) [6](#0-5) 

This is the binding the report's bug class describes: a field (`shop`) acted upon by the caller (tenant routing/storage) is not covered by the same HMAC that gates whether the request is accepted at all. `shop` used for tenant identity ≠ `shop` covered by the signature.

### Impact Explanation
An unprivileged owner of their own Shopify store (Shop A) is a legitimate webhook recipient for their own store and therefore possesses at least one validly-signed `(body, hmac)` pair. By replaying that pair to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header set to a victim shop (Shop B), the request still passes `HmacValidator.validate` (since only the body/secret matter), and the app's handler receives `WebhookMetadata` claiming the payload originated from Shop B. Any app that keys per-tenant storage, background jobs, or business logic off `data.shop` (exactly as the gem's own documentation recommends: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process attacker-controlled content under another tenant's identity — a cross-tenant data-integrity/confusion issue.

### Likelihood Explanation
Low-to-moderate: exploitation requires the attacker to already run/own a Shopify store using the vulnerable app (any merchant can install a public app), and requires the target app's webhook endpoint to be reachable without additional shop-scoped authentication and to trust `data.shop` as documented. No access to `api_secret_key`, tokens, or the victim's credentials is required — only the attacker's own legitimately delivered webhook, which is an action available to any unprivileged app user.

### Recommendation
Treat the header-derived `shop` as untrusted for tenant attribution unless corroborated: bind it into the signed material (e.g. Shopify already includes shop-scoped claims elsewhere, so cross-check `shop` against a value stored when the webhook was registered/known to the app for that specific `webhook_id`/topic), or require the consuming app to independently verify that the `shop` matches a shop with an active, known session/registration before trusting `data.body` as belonging to it. At minimum, the gem's documentation and `WebhookMetadata` should explicitly flag that `shop` is unauthenticated relative to the HMAC and must not be used as the sole tenant key without additional verification.

### Proof of Concept
1. Attacker owns `attacker.myshopify.com` and has the vulnerable app installed; Shopify delivers a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid for `B`), `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures `(B, H)` from their own inbox/proxy (no secret needed) and POSTs it directly to the app's public webhook endpoint, replacing the header with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim.myshopify.com", "x-shopify-hmac-sha256" => H})` is constructed.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only returns `B`, matching the header-declared shop only nominally — see `lib/shopify_api/webhooks/request.rb:20-38` and `lib/shopify_api/webhooks/registry.rb:188-200`.
5. The app's `WebhookHandler#handle` receives `WebhookMetadata(shop: "victim.myshopify.com", body: B, ...)` and processes attacker-controlled data under the victim's tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
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

**File:** docs/usage/webhooks.md (L19-30)
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
```
