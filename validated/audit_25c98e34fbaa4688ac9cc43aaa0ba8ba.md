### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (and `topic`) values that the app relies on to identify the tenant are taken from unauthenticated HTTP headers. `Registry.process` validates only the body's HMAC and then forwards the header-derived `shop` value to the app's `WebhookHandler` as if it were verified. This mirrors the ERC-777 report's bug class: a value used to update per-tenant state ("shop") is not the value actually covered by the authentication check ("raw body"), so the two can be made to diverge.

### Finding Description
`to_signable_string` in `Webhooks::Request` returns only `@raw_body`: [1](#0-0) 

but `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the HMAC-covered string: [2](#0-1) 

`Registry.process` validates only this body HMAC, then trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` that is handed to the app's handler: [3](#0-2) 

`WebhookMetadata#shop` is documented/typed as the authoritative tenant identifier the handler acts on: [4](#0-3) 

The identity binding that should hold is:
`shop bytes verified by HMAC == shop bytes acted upon by the handler`

Here this equality does not hold — the HMAC only proves "this body was signed with `api_secret_key`"; it proves nothing about which shop the header claims to be. Because every shop installed under a given app shares the same `api_secret_key`, any body+HMAC pair genuinely produced by Shopify for *any* shop that has installed the app (including a shop the attacker controls, e.g. a free/dev install) is a valid signature for *that same body* regardless of which `shop-domain` header accompanies it. An unprivileged actor who operates their own shop instance of the app can capture one legitimate `(raw_body, hmac)` pair from their own installation, then replay it to the app's webhook endpoint with the `shopify-shop-domain` header swapped to a victim shop. `Utils::HmacValidator.validate` still succeeds, and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be the victim shop with attacker-chosen body content.

### Impact Explanation
Apps built on this gem commonly key per-tenant data lookups, cache writes, or business logic directly off `WebhookMetadata#shop` (e.g., "update `shop`'s subscription/order/inventory record from this payload"). Because the gem itself presents `shop` as verified alongside a validated HMAC, without a documented caveat that the field is unauthenticated, an attacker can inject fabricated webhook payloads attributed to a shop they do not control — a cross-tenant data-integrity/access issue.

### Likelihood Explanation
Exploitation only requires the attacker to install the app on any shop they control (a normal, unprivileged action for public apps) to obtain one valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key`, then replay it against the shared webhook endpoint with a forged `shop-domain` header. No access token, leaked secret, or privileged account is required.

### Recommendation
Do not treat `Webhooks::Request#shop` (or `#topic`/`#api_version`/`#webhook_id`) as verified. Either:
- Include `shop`, `topic`, `api_version`, and `webhook_id` in the HMAC-signable string (requires coordinating with Shopify's webhook signing scheme), or
- Clearly document that only the raw body is authenticated by the HMAC, and require host applications to independently corroborate the `shop-domain` header (e.g., against the expected callback path/shop registered for that webhook subscription) before trusting it for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic, capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify sends (both valid because they're signed with the app's single shared `api_secret_key`).
2. Attacker POSTs the exact same body `B` and header `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(api_secret_key, B) == H` — this passes. [5](#0-4) 
4. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-supplied content under the victim shop's identity.

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
