### Title
Webhook shop-tenant identity not covered by HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies only covers the raw request body. `Registry.process` trusts this unauthenticated `shop` value to dispatch webhook data to the app's handler as if it were bound to the same identity that produced the valid signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from a request header with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC against `request` (i.e., against `to_signable_string` == raw body only) and, once that succeeds, immediately builds a `WebhookMetadata` object using `request.shop` — the header value — as the tenant identity handed to the app's handler: [3](#0-2) 

The identity binding the gem implicitly promises is: `shop that signed the body (via api_secret_key) == shop dispatched to the handler`. In reality the equality that holds is only `HMAC(api_secret_key, raw_body) == received_hmac`; the `shop` field is disjoint from that signed data. Because all shops installed under the same app share the same `api_secret_key`, a valid `(raw_body, hmac)` pair captured from one tenant (trivially obtainable — any unprivileged user can install a public app on their own store and trigger a webhook, e.g. `orders/create` or `app/uninstalled`) remains cryptographically valid HMAC-wise no matter which `shop-domain` header value is attached to the replayed HTTP request. An attacker can therefore resend the same body+hmac directly to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to point at a victim shop; `Utils::HmacValidator.validate` still returns `true` because it never inspects the header, and the app's `WebhookHandler` is invoked believing the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: attacker-controlled webhook data can be injected and attributed to an arbitrary victim shop, without needing the app's `client_secret` or any Shopify-issued credential for that victim. Depending on how the host app's `WebhookHandler` uses `data.shop` (e.g., looking up/mutating that shop's stored records, triggering shop-scoped side effects, or feeding it into session/storage lookups), this results in cross-tenant data confusion or state corruption — a High/Critical severity cross-tenant issue per the scope's impact bar.

### Likelihood Explanation
Requires only: (1) the ability to install the target public app on an attacker-controlled shop (or otherwise obtain one legitimate `(body, hmac)` pair for any topic), and (2) sending a raw HTTP POST directly to the app's public webhook endpoint with a forged `shop-domain` header — both are unprivileged-internet-user actions with no access token, secret key, or TLS interception needed. This is a realistic and low-effort attack path.

### Recommendation
Bind the shop identity into the verified material before it is trusted for dispatch — e.g., require the gem consumer/host app to cross-check `request.shop` against the shop associated with the session/install that the webhook claims to originate from (already-known shop-token mapping) rather than trusting the header value alone, or clearly document that `shop` is unauthenticated and must be independently verified by the host application before being used as a tenant key. At minimum, the gem should not silently offer `request.shop` inside `WebhookMetadata` without any accompanying warning that it is not covered by the HMAC.

### Proof of Concept
1. Attacker installs the target app to shop `attacker.myshopify.com` (self-service, no privileges needed) and triggers a webhook subscription event (e.g. `orders/create`), capturing the delivered HTTP request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC(api_secret_key, B)`.
2. Attacker crafts a new HTTP POST directly to the app's webhook endpoint with the exact same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares it to `H` — this succeeds since the shop header is never part of the signed string (`lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` then dispatches to the registered handler with `shop: request.shop` == `"victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198`), causing the host app to process attacker-controlled webhook content as if it belonged to the victim tenant.

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
