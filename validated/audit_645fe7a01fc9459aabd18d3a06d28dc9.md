### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw request body, then dispatches the handler using a `shop` value that is taken from an HTTP header that is never included in that HMAC computation. An attacker who can obtain any single genuine `(raw_body, hmac)` pair signed with the app's `client_secret` (e.g., from their own store's installation of the app, which is unprivileged and freely obtainable) can replay that exact body/HMAC pair while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop domain. The signature check still passes because the shop identity is never part of the signed material, so the handler is invoked believing the payload belongs to the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` — the value that is HMAC-verified — returns only the raw body: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is completely outside the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC over the request (i.e., over the body) and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The documented contract tells app authors that `data.shop` is "The shop domain of the webhook" without qualifying that it is unauthenticated: [4](#0-3) 

This is the same bug class as the external report: a field that is *acted upon* (here, `shop`, used for per-tenant attribution/dispatch) is not *covered by* the cryptographic check that is supposed to establish trust (the HMAC). The equality that should hold is:
`hmac_signed(shop, body) == received(shop, body)`
but what is actually implemented is:
`hmac_signed(body) == received(body)`, with `shop` taken unconditionally from the request regardless of the outcome.

### Impact Explanation
Because the app's `client_secret` is shared across every shop that installs the app, any unprivileged attacker can install the app on their own (attacker-controlled) store, capture one legitimate `(raw_body, x-shopify-hmac-sha256)` pair from a real webhook delivery, and then POST that identical body+HMAC to the app's webhook endpoint with `x-shopify-shop-domain` set to any other installed (victim) shop. `HmacValidator.validate` succeeds since it only checks the body, and the app's handler receives `WebhookMetadata` claiming the event belongs to the victim shop. Depending on how the host app keys its state off `data.shop` (order sync, entitlement changes, data writes, background job dispatch, etc.), this allows cross-tenant data injection/corruption — the attacker effectively forges events attributed to a shop they do not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The only prerequisite is the ability to install the app once (which any unprivileged Shopify user/developer can do — no privileged credentials, tokens, or secrets are required from the gem's perspective) and the ability to send arbitrary HTTP headers to the app's public webhook endpoint, both of which are always available to an external attacker of an app built on this gem.

### Recommendation
Bind the `shop` identity into the value that is HMAC-verified (e.g., include the shop domain and/or webhook id in the signable string, or require host apps to look up the session/shop from their own trusted registration state rather than from an unauthenticated header) before dispatching to handlers. At minimum, `docs/usage/webhooks.md` and `WebhookMetadata` should clearly state that `shop` is unauthenticated header data and must be cross-checked against the app's own known-installed-shops list before being trusted for any privileged or tenant-scoped operation.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (legitimate, unprivileged action) and registers a webhook, e.g. `orders/create`.
2. Shopify delivers a webhook to the app with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker captures `(B, H)` (e.g., via their own request logs — no secret needed).
4. Attacker sends:
```
POST /callback/orders/create HTTP/1.1
x-shopify-topic: orders/create
x-shopify-hmac-sha256: H
x-shopify-shop-domain: victim-shop.myshopify.com
Content-Type: application/json

B
```
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only (`Request#to_signable_string`) and succeeds, since `B` and `H` are unchanged.
6. The app's handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
