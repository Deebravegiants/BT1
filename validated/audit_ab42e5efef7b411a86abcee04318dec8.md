### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-attribution spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw body only, while the `shop` value the gem hands to the app's `WebhookHandler` is read straight from the `X-Shopify-Shop-Domain` header, which is never included in the signed material.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery`'s `hmac` against `to_signable_string`. For webhooks, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor used downstream is derived independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header, with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC (covering the body only) and then trusts `request.shop` as the tenant identifier passed into `WebhookMetadata`, which the app's handler uses to route/attribute the webhook to a specific shop: [3](#0-2) [4](#0-3) 

This exactly matches the bug class hinted by the report: "a field acted on but not covered by the HMAC." Here the equality the gem implicitly (and incorrectly) assumes is:

`shop used for tenant attribution (WebhookMetadata.shop, from header) == shop the HMAC actually authenticates (none — HMAC covers only raw_body)`

Because `shop` is outside the signed scope, any two values `(raw_body, hmac)` that are valid for shop A remain HMAC-valid when replayed with the `shop-domain` header changed to shop B — the signature check in `Utils::HmacValidator.validate` (via `OpenSSL.secure_compare`) still passes since it never inspects the header at all: [5](#0-4) 

### Impact Explanation
A party who legitimately owns/operates one shop (or who can otherwise obtain one genuine `(raw_body, hmac)` pair addressed to their own installation — which they control, since they are that shop's merchant and receive their own webhooks) can resend that same request to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. The HMAC check still succeeds (it only verifies the body was produced with the app's `client_secret`), and `Registry.process` forwards `WebhookMetadata.new(..., shop: request.shop, ...)` — now claiming to be the victim tenant — to the host application's handler. Any app that uses `data.shop` to select which tenant's records to create/update/delete (the pattern shown in the gem's own docs, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be tricked into writing or acting on another merchant's data. This is a cross-tenant identity-binding break, matching the Critical "cross-tenant access" impact category. [6](#0-5) 

### Likelihood Explanation
Requires only an unprivileged attacker who controls one shop (a normal, non-privileged Shopify merchant/app-install), no leaked secrets, no TLS interception, and no host-application misconfiguration — they only replay a webhook they legitimately received and edit one HTTP header before resending it to the app's public webhook endpoint. The `client_secret` itself is never needed. This is realistic and directly exploitable against any app that trusts `WebhookMetadata.shop` (the documented and expected usage pattern).

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the HMAC-signed material, or otherwise cryptographically bind the header-derived tenant identity to the verified payload (e.g., verify the header against a value embedded/signed in the body, or require the shop to be looked up via the account associated with the webhook subscription rather than trusted from an unauthenticated header) before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker's own shop `attacker.myshopify.com` has a webhook registered; Shopify delivers a genuine webhook to the app with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and some `raw_body`.
2. Attacker captures this raw HTTP request (they are the recipient/owner of that endpoint's traffic, or proxies it).
3. Attacker resends the identical `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only — it matches, since the body is unchanged.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)` and calls the host app's `handler.handle`, which now processes attacker-controlled data as if it belongs to `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
