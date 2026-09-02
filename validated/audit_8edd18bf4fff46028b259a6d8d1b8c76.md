This confirms the finding: in `AuthQuery` (OAuth callback), the `shop` field is explicitly included in `to_signable_string` and thus covered by the HMAC. But in `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , meaning the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are never part of the HMAC-signed content, while `HmacValidator.validate` only checks the `hmac` field derived from the (unsigned) `shop` header path [2](#0-1) . That request object's `shop` accessor is read directly and unauthenticatedly from the header [3](#0-2) , then handed straight to the handler as the tenant identity in `WebhookMetadata` inside `Registry.process` [4](#0-3) .

### Title
Webhook `shop` (tenant) identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies that body against the HMAC. None of the identity-bearing headers — `shop-domain`, `topic`, `webhook-id`, `api-version` — are included in the signed content, yet `Registry.process` trusts the unauthenticated `shop-domain` header value as the tenant identity passed to the app's webhook handler.

### Finding Description
The library's webhook verification binds the HMAC only to the JSON body:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`HmacValidator.validate_signature` computes the digest solely over that signable string and compares it to the `hmac` header [2](#0-1) . The `shop` accessor, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic binding to the verified signature [3](#0-2) .

`Registry.process` first calls `Utils::HmacValidator.validate(request)` and, once it passes, immediately constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from the same request object and dispatches it to the handler [4](#0-3) . The equality the gem implicitly promises — "the shop whose webhook body was HMAC-verified" == "the shop the handler is told to act on" — does not hold, because the `shop` header can be freely changed without invalidating the signature.

This is directly analogous to the report's bug class: a field (`shop`) is acted upon by downstream logic but is not covered by the integrity check (HMAC), exactly the "field acted on but not covered by the HMAC" pattern called out in the rules. Contrast this with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` is deliberately included in `to_signable_string` and thus properly bound to the signature [5](#0-4) . The webhook path lacks this same protection.

### Impact Explanation
Any actor who possesses one genuine HMAC-signed webhook body for their own installed shop (a routine, unprivileged occurrence — every shop that installs an app receives its own valid webhooks) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` value. Because the signature check never inspects the shop header, the forged request passes `HmacValidator.validate` and is delivered to the app's handler with `WebhookMetadata#shop` set to the attacker-chosen shop. If the host application (following this gem's documented API — using `data.shop` to identify the tenant, as the library's own `webhook_handler.rb` and tests do [6](#0-5) ) uses this value to select which merchant's session/store to update, this breaks tenant isolation: cross-tenant data confusion, where webhook data intended for/verified against shop A is processed under shop B's identity.

### Likelihood Explanation
Moderate-to-High. Any merchant with the app installed on their own shop legitimately receives valid HMAC-signed webhooks for benign topics (e.g., `app/uninstalled`, `shop/update`) with a body that carries little or no shop-specific secret data. That merchant is an "unprivileged internet user" relative to other tenants and can trivially replay the body with a modified shop header against the app's public webhook endpoint, since nothing else in the verification path depends on the shop value.

### Recommendation
Bind the shop (and ideally topic/webhook-id) identity into the HMAC verification path. This requires either changing the signable content, or having the gem/host application separately verify that the shop asserted in the header matches an install/session record obtained through the OAuth flow (not solely relying on the header/HMAC-body pairing) before treating `request.shop` as authenticated. At minimum, `Webhooks::Request#to_signable_string` should be documented as not covering `shop`, and `Registry.process` / `WebhookMetadata` should require callers to cross-check `shop` against a known, previously-authenticated install record.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook for topic `app/uninstalled` with body `{}` and header `x-shopify-shop-domain: attacker-shop.myshopify.com`, correctly HMAC-signed with the app's `client_secret`.
2. Attacker captures this request/response pair from their own shop (fully within their privilege as the shop owner).
3. Attacker resends the identical body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only (`{}`), which matches — validation succeeds [2](#0-1) .
5. `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and invokes the app's handler for that shop [4](#0-3) , causing the handler to act as though the (attacker-controlled) event originated from the victim shop.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-20)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
```
