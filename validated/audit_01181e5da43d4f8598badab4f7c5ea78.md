### Title
Webhook `shop-domain` header is not covered by the HMAC, allowing shop-spoofing / cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are taken from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then hands `request.shop` straight to the app's handler as the tenant identifier. Because the shop field is never bound into the HMAC, a holder of one valid `(body, hmac)` pair can replay it with a different `shopify-shop-domain` header and have it accepted as authentic for an arbitrary shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read directly from an attacker-controllable header with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC over the `Request` object and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app-supplied handler: [3](#0-2) 

`HmacValidator.validate` only recomputes the signature over `to_signable_string` (i.e. the body) and compares it to the received `hmac`: [4](#0-3) 

This exactly matches the reported bug class: a field that is acted upon (`shop`, used by the app to attribute/target the webhook data) is not covered by the integrity check (`hmac` covers only `@raw_body`). The equality that should hold is:
`shop authenticated by HMAC == shop attributed to the webhook payload`
but the gem only proves `body authenticated by HMAC == body attributed to the payload`; `shop` is authenticated by neither.

The gem's own documentation instructs apps to trust `data.shop` directly as the tenant key returned from `Registry.process`, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`, so an app following the documented API is exposed, without any misuse on the app's part: [5](#0-4) 

### Impact Explanation
Any entity that can install the app on their own shop legitimately receives genuine Shopify webhooks, correctly HMAC-signed for their own shop's body content. Because the shop header is not part of the signed content, that same `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with a forged `shopify-shop-domain`/`x-shopify-shop-domain` header naming a victim shop. `Registry.process` will accept it (HMAC passes) and dispatch it to the handler as if it were data for the victim shop, i.e. cross-tenant data confusion/injection — data.body content controlled/known by the attacker (from their own shop's webhook) is delivered under a victim shop's identity. This can lead to state corruption, unauthorized actions, or data leakage/mixing across tenants in apps that key their persistence/business logic off `data.shop`, satisfying the "cross-tenant access" criticality bar.

### Likelihood Explanation
Requires only: (1) the attacker install the app on a shop they control (a normal, unprivileged interaction any merchant can perform), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a spoofed `shopify-shop-domain` header and the previously-observed valid body+hmac pair. No credential, access token, or `client_secret` of the victim is needed. This is fully reachable through the gem's documented `Webhooks::Request` / `Webhooks::Registry.process` flow.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the HMAC-verifiable material, or otherwise require the app to independently establish shop identity out-of-band (e.g., validate `shop` against a known/allow-listed set of installed shops, or include it in `to_signable_string` if Shopify's signature scheme is updated to support it). At minimum, document loudly that `data.shop` is not integrity-protected by the returned HMAC validation and must not be trusted as an authenticated tenant identifier without additional verification.

### Proof of Concept
1. App installs and receives a legitimate webhook for `attacker-shop.myshopify.com` with body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC(api_secret_key, B)`.
2. Attacker replays a POST to the app's webhook endpoint with the same raw body `B`, same `shopify-hmac-sha256: H`, but header `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts these headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (`to_signable_string`) — the forged shop header is never checked: [1](#0-0) 
4. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed body>, ...)`, causing the app to act on attacker-supplied data under the victim shop's identity. [6](#0-5)

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
