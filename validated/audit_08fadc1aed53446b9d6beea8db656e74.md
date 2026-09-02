### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) straight from the unauthenticated `X-Shopify-Shop-Domain` header, while `Utils::HmacValidator` only verifies the raw request body. The HMAC therefore proves the payload was signed by the app's shared `client_secret`, but never binds that payload to the shop-domain header the app trusts and forwards to the webhook handler.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`: [1](#0-0) 

`to_signable_string` for `ShopifyAPI::Webhooks::Request` is simply the raw body — no header, including the shop domain, is part of the signed data: [2](#0-1) 

`shop` is read straight off the (attacker-influenceable, in a replay scenario) `shopify-shop-domain` / `x-shopify-shop-domain` header and passed unchanged into the handler after HMAC validation succeeds: [3](#0-2) [1](#0-0) 

The identity binding broken is:
`shop authenticated by the HMAC` ≠ `shop stored/acted upon as the tenant identifier delivered to the handler`.

Because a single app's `client_secret` is shared across **every** shop that has installed the public app, any merchant who installs the app can legitimately obtain a validly HMAC-signed `(body, hmac)` pair for content they control (e.g. by naming a product/order field with attacker-chosen text and triggering a real webhook to their own endpoint). That signature depends only on `raw_body` and the shared secret — never on which shop it was issued for. An attacker can then replay that exact `(raw_body, hmac)` pair to the target app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `HmacValidator.validate` will pass (body+secret still match), and `Registry.process` will invoke the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` pointing at the victim tenant while `body` is attacker-controlled content.

This is the same bug class as the referenced report: a value that is *acted upon* (there: the reward token address in `distributeEx`; here: the `shop` tenant identifier used to route webhook data) is not covered by the authenticity check (there: no validation against the canonical reward token; here: no HMAC coverage of the shop-domain header), letting an authenticated-but-wrong-scope actor redirect the effect of a signed operation onto another tenant.

### Impact Explanation
This allows cross-tenant confusion: an attacker who is a legitimate (even free-tier) installer of the app can craft webhook deliveries whose HMAC validates, but whose `shop` value is that of a different, victim merchant. Any app logic keyed off `data.shop` (billing, plan-gating, order/customer record association, GDPR data-request/erasure webhooks, per-tenant caches, etc.) can be corrupted with attacker-supplied data attributed to another tenant. This matches "Critical – cross-tenant access" since it crosses the tenant boundary the gem is otherwise supposed to enforce via `WebhookMetadata#shop`.

### Likelihood Explanation
Requires only that the attacker be able to install the app on a shop they control (a normal, low-privilege action for public apps) and be able to replay/forge an HTTP POST to the app's public webhook endpoint with a modified header — no access token, `client_secret`, or leaked credential is needed. The gem performs no additional binding of `shop` to the signed payload, so likelihood is moderate-to-high wherever the host app trusts `WebhookMetadata#shop` for tenant-sensitive logic.

### Recommendation
Include the shop domain (and/or webhook id/topic) as part of the HMAC-signable material, or otherwise cryptographically bind the header value to the signed payload, e.g. by re-deriving/validating `shop` from a per-installation secret/session rather than trusting the raw header once the body HMAC passes.

### Proof of Concept
1. App "MyApp" is a public app; shop `attacker.myshopify.com` installs it and triggers a webhook (e.g. `products/update`) with a product title crafted by the attacker.
2. Shopify sends the app a POST with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <hmac(body, client_secret)>`, and the attacker-controlled body.
3. Attacker captures this request, then re-sends it to the same webhook endpoint, only replacing `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC over the unchanged raw body and it matches (per `lib/shopify_api/utils/hmac_validator.rb` lines 26-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38).
5. `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker's body — the app now processes attacker data as if it originated from the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
