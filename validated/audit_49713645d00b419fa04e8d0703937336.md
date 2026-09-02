This confirms the design: the docs explicitly promise `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and that `data.shop` is meant to be trusted as "The shop domain of the webhook" [2](#0-1) , yet the HMAC signature only covers the raw body, not the shop-domain header.

### Title
HMAC verification excludes the `shop` (tenant) identity header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives its HMAC-signable content solely from the raw request body, while the shop identity (`x-shopify-shop-domain`) is read from an unauthenticated header. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body/HMAC pair is valid, then hands the handler a `WebhookMetadata` whose `shop` field is taken directly from that unsigned header. This breaks the identity binding `HMAC-verified data == data trusted by handler`, because the `shop` value used by the host app to scope tenant data is not one of the values verified by the HMAC.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, and for webhook requests `to_signable_string` returns only `@raw_body` [3](#0-2) . The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to that HMAC [4](#0-3) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [5](#0-4) . Because the webhook secret (`api_secret_key`) is a single, app-wide secret shared across every shop that installs the app (not a per-shop secret), any tenant that has installed the app can legitimately receive webhooks with a valid HMAC for a given body. That same merchant can replay that body+HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain — the HMAC check still passes because the header is not part of the signed content, yet `request.shop` (and thus `data.shop` delivered to the app's handler) now falsely identifies the victim tenant.

The library's own documentation reinforces that host apps are meant to rely on `Registry.process` to fully "verify the request did indeed come from Shopify" [1](#0-0)  and to trust `data.shop` as "The shop domain of the webhook" [2](#0-1) , so this is a documented API contract, not host-app misuse.

### Impact Explanation
This allows cross-tenant data injection/impersonation in any multi-tenant app relying on this gem's webhook verification: a malicious (but otherwise legitimate) installer of the app can forge webhook deliveries that the app attributes to a different, victim shop, since `shop` is not bound by the HMAC that the gem asserts as its verification boundary. This maps to the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged party who can install the app on their own store (a normal, unprivileged action for any Shopify app) can capture a genuine webhook body+HMAC from their own shop and replay it with a forged shop-domain header — no access token, `client_secret`, or privileged account is required, only observation of their own webhook traffic.

### Recommendation
Include the shop domain (and other identity-relevant headers such as `topic`/`api-version`/`webhook-id`) in the HMAC-signed material, or otherwise cryptographically bind `shop` to the verified payload (e.g., validate that the shop belongs to a known, previously-registered session before trusting `data.shop`), analogous to how `verifyAndInsertForecastsFromTopForecasters` should have persisted the filtered/accepted set rather than trusting unfiltered input.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, a legitimate, unprivileged action.
2. Shopify sends a real webhook: body `B`, headers include `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays this exact request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` from `to_signable_string` (body only) and it matches, since the body `B` is untouched.
5. `Registry.process` calls the handler with `WebhookMetadata` where `shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop, causing the host app to process/store attacker-controlled data under the victim tenant.

### Citations

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
