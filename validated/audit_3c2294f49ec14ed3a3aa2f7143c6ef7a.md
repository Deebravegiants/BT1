### Title
Webhook `shop-domain` header is trusted by `Webhooks::Registry.process` without being bound to the HMAC signature - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body, then hands the caller-supplied `shop-domain` header straight through to the app's handler as the authenticated tenant identity. The HMAC never covers the `shop-domain` header, so the "shop" the app believes the event came from is not cryptographically bound to the signature that was checked.

### Finding Description
`Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body`: [2](#0-1) 

Meanwhile `request.shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed material at all: [3](#0-2) 

This is the exact pattern called out by the analog class: a field acted on ( `shop` ) that is not covered by the HMAC ( only `raw_body` is signed ). Because `Registry.process` raises before dispatching if `HmacValidator.validate` fails, developers reasonably read the code as "if `process` didn't raise, the whole request (including the shop) is authentic." In reality only the byte-identical body is authenticated; the shop header can be swapped for any value at will.

The equality this breaks is:
```
shop authenticated by the HMAC check  !=  shop delivered to the app's handler
```
Concretely: an attacker who controls (or trials with) their own Shopify store connected to the same app receives a legitimate webhook from Shopify — e.g. `orders/create` — with body `B` and a correctly computed `X-Shopify-Hmac-Sha256: H` (computed by Shopify using the shared `api_secret_key`). The attacker replays this exact `(B, H)` pair to the app's webhook endpoint, but substitutes `x-shopify-shop-domain: victim-shop.myshopify.com`. `Registry.process` recomputes the HMAC over `B`, finds it matches `H` (since the body bytes are unchanged), and proceeds to invoke the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the event/body content actually originated from the attacker's own shop.

### Impact Explanation
Any app whose webhook handler uses `data.shop` to select the merchant's stored access token, write to per-tenant records, or make trust decisions (which is exactly what the `WebhookMetadata#shop` field exists for) can be tricked into attributing attacker-controlled event data to a victim tenant, or into acting on a victim tenant's identity with attacker-chosen body content. This is cross-tenant access / cross-tenant data injection — one of the explicit "Critical" impact categories (cross-tenant access) since the boundary broken is the per-shop trust boundary that the HMAC check is supposed to enforce.

### Likelihood Explanation
High. Exploitation only requires that the attacker operate one legitimate Shopify store that has the target app installed (a normal, unprivileged merchant/developer action — no leaked secrets, no privileged account, no TLS interception required). The attacker only needs to capture one webhook delivery from their own store and replay it with a different `shop-domain` header value to any endpoint that calls `Registry.process`, which is the gem's documented/intended entry point for webhook handling.

### Recommendation
Bind the shop identity to the signed payload instead of trusting an unauthenticated header:
- Either fold `shop-domain` (and `topic`, `webhook-id`, `api-version`) into the HMAC-covered signable string (this requires coordination with Shopify's signing scheme, since Shopify currently signs body-only), or
- More practically within this gem: require callers of `Registry.process`/`WebhookMetadata` to independently verify that `request.shop` corresponds to a shop with a known, previously-established session/access token before trusting it, and document explicitly that `HmacValidator.validate` only authenticates the body, not the `shop`/`topic` headers, so integrators do not implicitly trust `data.shop` as a signature-verified value.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers an event that generates a real webhook, e.g. `orders/create`.
2. Attacker's endpoint (or a proxy they control) captures the delivered HTTP request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for body `B` under the app's `api_secret_key`), plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker crafts a new POST to the app's actual webhook endpoint with the identical body `B` and identical `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`. `Utils::HmacValidator.validate` recomputes HMAC over `B` (unchanged) and matches `H`, so no `InvalidWebhookError` is raised.
5. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` [4](#0-3)  — the app now processes attacker-controlled event content under the victim shop's identity.

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
