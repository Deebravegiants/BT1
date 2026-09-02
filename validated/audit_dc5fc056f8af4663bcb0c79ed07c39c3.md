### Title
Webhook `shop` Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (tenant) identity is read from an unsigned HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identifier passed to the app's handler, without that value ever being covered by the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is completely outside the signable string: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which checks `request.hmac` against `HMAC(secret, request.to_signable_string)` — i.e., only the body is authenticated — and then immediately forwards the *unauthenticated* `request.shop` value into `WebhookMetadata`, which is handed to the app's registered handler as the tenant identity: [3](#0-2) 

The HMAC secret (`api_secret_key`) is shared across *all* shops that install the same app — it is not per-tenant. This means the binding this code implicitly relies on is:

`shop value acted upon (used as tenant key by the handler) == shop value verified by the HMAC`

but in reality:

`shop value verified by HMAC == nothing (HMAC only covers raw_body)`

so the equality does not hold. Any entity that can obtain one genuine, Shopify-signed webhook delivery for *any* shop that has this app installed (e.g., by installing the app on their own store and triggering an event) possesses a valid `(raw_body, hmac)` pair. They can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` still succeeds because the header is never part of the signed content, and `Registry.process` passes the attacker-chosen `shop` straight through to the handler.

### Impact Explanation
This breaks the tenant/identity boundary the HMAC check is meant to enforce. An attacker who legitimately installs the app on their own store (an "unprivileged" party with respect to every other merchant) can forge webhook events that the app will process as belonging to a victim shop of their choosing, without needing that victim's credentials, `api_secret_key`, or an access token. Depending on how the host application's handlers use `data.shop` (e.g., looking up/deleting/mutating per-shop records, honoring `shop/redact` or `customers/redact` mandatory topics), this enables cross-tenant data corruption, spoofed compliance/redact events, or injection of fabricated order/customer data attributed to another merchant — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any user of the app who can install it on a shop they control (a normal, unprivileged flow for third-party apps) can generate a genuine `(body, hmac)` pair for arbitrary body content by triggering the corresponding Shopify event on their own store, then replay it with a rewritten shop header to the app's public webhook endpoint. No secret material or elevated access is required, and the library itself provides no mechanism to bind the shop header to the signature — the vulnerability is fully reachable through this gem's own `Webhooks::Request`/`Registry` code path as documented and used.

### Recommendation
Include the `shop-domain` (and ideally `webhook-id`/`topic`) header values in the HMAC-signed content that `Request#to_signable_string` verifies, or otherwise cryptographically bind the shop identity to the payload before trusting `request.shop` in `Registry.process`/`WebhookMetadata`. At minimum, document that host applications must independently verify `data.shop` corresponds to a shop with an active, valid session/installation before using it as a trust boundary, since the HMAC alone does not authenticate the shop field.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers/triggers a webhook (e.g., `orders/create`) so Shopify delivers a genuine request with body `B` and header `shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker captures this request and replays it to the app's public webhook endpoint, changing only the `shopify-shop-domain` header to `victim-shop.myshopify.com`, keeping `B` and the HMAC header untouched.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` — matching, since `shop-domain` isn't part of `to_signable_string` — and validation succeeds: [4](#0-3) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes the attacker's forged body as though it originated from the victim's store.

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
