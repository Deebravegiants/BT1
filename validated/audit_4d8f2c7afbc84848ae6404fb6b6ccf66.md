### Title
Webhook HMAC only authenticates the raw body, not the `shop` domain — allows cross-tenant webhook spoofing ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` only proves the *body bytes* were signed by the app's `client_secret` — it never binds the `shop` value taken from the `X-Shopify-Shop-Domain` header. `Registry.process` nonetheless treats that unauthenticated header as the tenant identity and hands it straight to the host application's webhook handler.

### Finding Description
The HMAC signable string is defined as: [1](#0-0) 

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

while `shop` is read straight from an attacker-controlled HTTP header with no cryptographic binding to that body: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers `@raw_body`) and then immediately trusts `request.shop` as the tenant identity for the handler call: [3](#0-2) 

The equality this code implicitly assumes is:
`shop claimed in X-Shopify-Shop-Domain header == shop that the HMAC signature actually authenticates for`

But the HMAC secret (`Context.api_secret_key`, i.e. the app's `client_secret`) is identical for *every* shop that installs the app — it is not shop-specific. Consequently a valid `(body, hmac)` pair only proves "this body was sent by Shopify for some installation of this app," not "this body belongs to shop X." Any unprivileged user can install the app on their own store (a normal, unprivileged action), receive genuine Shopify-signed webhooks for that store, and replay the exact `(body, hmac)` bytes to the app's webhook endpoint while substituting an arbitrary victim `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` forwards the forged shop identity to the handler via `WebhookMetadata`: [4](#0-3) 

The documented usage pattern shows host apps use `data.shop` directly as the tenant key when enqueuing work: [5](#0-4) 

### Impact Explanation
This breaks the tenant/shop identity binding that the whole webhook subsystem relies on. An attacker who legitimately installs the app on their own store can forge webhook events (e.g. `app/uninstalled`, `orders/create`, `customers/data_request`, etc.) that appear — to the host application built on this gem — to originate from any other shop of the attacker's choosing, because the gem exposes `request.shop` as trustworthy once `HmacValidator.validate` passes. This is a cross-tenant identity confusion: data or state changes intended for the attacker's own shop get attributed to a victim tenant purely by header spoofing, with no need for the victim's or Shopify's credentials.

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on an attacker-controlled store (a normal, unprivileged action available to anyone), (2) capturing one genuine webhook `(raw_body, hmac)` pair sent to the attacker's own endpoint, and (3) POSTing those same bytes to the app's public webhook endpoint with a modified `X-Shopify-Shop-Domain` header. No secrets, tokens, or elevated access are required, and the gem performs no header-binding check that would prevent this.

### Recommendation
Include the shop domain (and other decision-relevant headers such as `topic`) in the HMAC-signable content, or otherwise cryptographically bind the claimed shop to the signed payload before trusting it. At minimum, document that `request.shop` from `Webhooks::Request` is not authenticated by the HMAC and must be independently verified (e.g., cross-checked against a known, previously-registered shop record) before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, a normal unprivileged install.
2. Shopify sends a legitimate webhook to the app's endpoint:
   - Headers: `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`
   - Body: `{"id":123,...}`
3. Attacker captures the raw body and the valid HMAC (both are visible to them since it's their own webhook).
4. Attacker sends a new POST to the same app endpoint with identical body and HMAC, but with header `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — it passes.
6. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: {...}, ...)` and the host app processes attacker-controlled data as if it came from the victim tenant. [3](#0-2) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
