Based on my analysis, I've confirmed a valid analog to the bug class described in the report.

### Title
Webhook `shop-domain` header is trusted for tenant attribution without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity using only an HMAC over the raw body, then trusts the unauthenticated `shop-domain`/`x-shopify-shop-domain` header as the tenant identity passed to the app's handler. This is exactly the bug class in the report: a field ("shop") that is acted upon (used to attribute the event to a tenant) is not covered by the cryptographic verification (the HMAC only signs the body).

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read directly from an HTTP header with no cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` verifies the HMAC (which only covers the body) and then unconditionally forwards `request.shop` to the app's handler as the tenant identity: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no verification, and the gem's own documentation instructs apps to key their tenant-scoped work (e.g. `shop_domain: data.shop`) directly off this value: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop header value == shop that generated/authorized the signed body`. Because only `@raw_body` is HMAC'd, this equality is never checked. Any unprivileged internet user who can install the same public app on their own shop (a normal merchant onboarding flow, not a privileged action) receives legitimately-signed webhook deliveries for their own shop — bodies signed with the app's `client_secret`, which is shared across all shops using that app. That attacker can capture one such delivery (body + valid `hmac`) and replay it to the app's public webhook endpoint with the `shop-domain`/`x-shopify-shop-domain` header rewritten to a victim shop's domain. The HMAC check in `HmacValidator.validate` still passes (it only recomputes the signature over the untouched raw body), so `Registry.process` invokes the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain while `body` is still the attacker's own (or attacker-crafted, if `fields` filtering is used to constrain it) data.

### Impact Explanation
This crosses a tenant boundary: an app relying on `WebhookMetadata.shop` (as the docs recommend) to look up per-shop state, dispatch background jobs (`shop_domain: data.shop`), write to shop-scoped storage, or trigger a shop-scoped action will attribute attacker-controlled data to a shop the attacker doesn't control. This matches the "cross-tenant access" Critical-impact category, since the confidentiality/integrity of a victim shop's app state can be affected by data the attacker fully controls, without possessing the victim's credentials or access token.

### Likelihood Explanation
Likelihood is high for any app: exploitation requires only (1) that the attacker install the target app on their own store (a normal, unprivileged merchant action available to any internet user for public apps), (2) capture a legitimately-signed webhook delivery for their own shop, and (3) replay it to the app's endpoint with a modified `shop-domain` header — all doable with basic HTTP tooling, no secrets or credentials of the victim required.

### Recommendation
Bind the `shop` value to the signed payload instead of trusting the header verbatim:
- Include the `shop-domain` value (and ideally `topic`, `api_version`, `webhook_id`) in the HMAC-signed material, mirroring how `AuthQuery#to_signable_string` includes `shop` in the OAuth callback signature, or
- Cross-check the header's `shop` against an independently trusted source (e.g., the shop associated with the registered webhook subscription id) before dispatching to the handler, and
- Document prominently that `WebhookMetadata.shop` is currently unauthenticated and must not be trusted for tenant attribution until fixed.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` (normal onboarding, no privileged access needed).
2. Attacker triggers an event on their own store causing Shopify to deliver a webhook to the app: body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker replays this exact request to the app's public webhook endpoint but rewrites the header to `X-Shopify-Shop-Domain: victim-shop.myshopify.com`. `B` and `H` are unchanged.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)` — the check passes because it never inspects `shop`: [6](#0-5) 
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: B, ...)`, and the app performs shop-scoped work for `victim-shop.myshopify.com` using attacker-supplied `B`.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
