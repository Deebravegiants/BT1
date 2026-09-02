### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` (tenant) identifier used downstream is read from the unauthenticated `X-Shopify-Shop-Domain` header. This breaks the identity binding `shop authenticated by HMAC == shop passed to the handler`, allowing any merchant who legitimately receives a signed webhook from Shopify to relabel it as belonging to a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The shop identity is instead taken from a separate, un-signed header: [2](#0-1) 

`Registry.process` verifies only this body-only HMAC via `Utils::HmacValidator.validate(request)`, then forwards `request.shop` (the unauthenticated header value) straight to the application handler as the tenant context: [3](#0-2) 

Because Shopify apps sign **all** outbound webhooks for **all** installed shops with the single app-level `client_secret` (verified here via `Context.api_secret_key`, see `Utils::HmacValidator`), the HMAC over the body proves only "this body byte-for-byte was signed by Shopify for this app," not "this body belongs to shop X." Any merchant who installs the app on their own store (an unprivileged internet user with respect to other tenants) legitimately receives real webhook deliveries — valid `(raw_body, hmac)` pairs signed with the app's shared secret. That merchant can replay the exact same body and HMAC header to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `HmacValidator.validate` will still pass because it only checks the untouched body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop.

Binding broken (equality that should hold but doesn't):
`shop covered by HMAC == shop trusted by the handler` → in reality, `shop covered by HMAC == "" (nothing)` while `shop trusted by handler == request.shop` (attacker-controlled header).

### Impact Explanation
This is a cross-tenant integrity issue: an attacker-controlled shop identifier is passed to the host application's webhook handler with no cryptographic binding to the correct shop. Any host app that uses `WebhookMetadata#shop` to select which merchant's session/data record to update (a common, encouraged pattern) can be tricked into writing/mutating data under an incorrect (victim) shop's tenant using attacker-supplied body content — a cross-tenant access/data-integrity break, without ever needing the app's `client_secret` or an access token.

### Likelihood Explanation
Any developer who has installed the app on a legitimate store can capture one of their own genuine webhook deliveries (body + `X-Shopify-Hmac-Sha256` header) — no special access is required — and replay it against the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header. The check in `Registry.process` and `HmacValidator.validate` performs no comparison between the signed content and the shop header, so this requires no secret material and works reliably.

### Recommendation
Bind the shop identity to the signed payload instead of trusting a separate header:
- Include the `shop` value in the signable bytes (e.g., verify it against `parsed_body["shop_domain"]` / order-level shop fields present in most webhook payloads, since these fields are inside the HMAC-covered body), or
- Maintain a per-shop expected-domain check by cross-referencing the webhook `topic`/`webhook_id` against a previously stored subscription for that shop before invoking the handler, or
- At minimum, document prominently that `WebhookMetadata#shop` is derived from an unauthenticated header and must not be trusted for authorization decisions without additional binding.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and receives a real webhook, e.g.:
   - Headers: `X-Shopify-Hmac-Sha256: <valid-hmac>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`
   - Body: `{"id": 1, ...}` (their own order)
2. Attacker replays the identical body and `X-Shopify-Hmac-Sha256` header to the same app endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` — unchanged — so validation succeeds.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker's data>, ...)`, causing the application to process attacker-controlled data under the victim shop's tenant context.

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
