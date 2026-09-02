## Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` (and `topic`/`webhook_id`) values that are handed to the app's handler come from unauthenticated HTTP headers that are never included in the signed content. Because the app's `api_secret_key` (used to compute the HMAC) is shared across every shop that installs the app, a valid `(body, hmac)` pair obtained from one shop's genuine webhook remains valid no matter which `shop-domain` header accompanies it.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhooks that string is defined as just the raw body: [1](#0-0) 

The shop domain is read straight from the (attacker-controllable) HTTP header and is never part of the signed payload: [2](#0-1) 

`Registry.process` only checks the HMAC of the body, then immediately trusts `request.shop` to build the `WebhookMetadata` object that is dispatched to the app-supplied handler: [3](#0-2) 

The identity binding that should hold is:
`hmac_valid(body, secret) == true` should imply `shop_header == shop_that_actually_produced(body)`.

That equality does not hold here, because `shop_header` is excluded from `to_signable_string`. Since the `api_secret_key` is identical for every shop that installs a given app (it's the app's client secret, not a per-shop secret), any legitimate merchant who installs the app can capture a genuinely-signed `(raw_body, hmac)` pair from a webhook Shopify sent them, and replay that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header for a different, victim shop. `Utils::HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the (attacker-controlled) body belongs to the victim shop.

### Impact Explanation
This breaks the shop-authenticated vs. shop-acted-upon binding and lets an unprivileged internet user (any merchant who can install the app once to obtain one valid signed payload) inject attacker-chosen webhook data under an arbitrary victim shop's identity into the host application's per-tenant processing/storage. Depending on how the app's registered webhook handler uses `WebhookMetadata#shop` (e.g., to look up/update the corresponding merchant's session, orders, customer records, or trigger app-side side effects), this results in cross-tenant data corruption/injection — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is realistic: obtaining one validly-signed `(body, hmac)` pair only requires installing the app on the attacker's own store (an ordinary, unprivileged action), and no secret, access token, or TLS interception is needed to forge the replay — only crafting an HTTP POST to the app's public webhook endpoint with a swapped `shop-domain` header.

### Recommendation
Bind the shop identity to the signed payload rather than trusting the header alone, e.g., by including the shop domain (and/or webhook id/topic) in the signable string used for HMAC verification, or by independently confirming that the `shop-domain` header corresponds to a shop for which the app currently holds a valid session/installation before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) so Shopify sends a POST with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker resends this POST to the app's webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(secret, B)` (per [1](#0-0) ), which still equals `H`, so validation passes.
4. `Registry.process` (per [3](#0-2) ) invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker's body content, causing the host app to process attacker-controlled data as belonging to the victim shop.

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
