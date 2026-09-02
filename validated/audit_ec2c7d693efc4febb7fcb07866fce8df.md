Confirmed: `to_signable_string` for `Webhooks::Request` only signs `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read from HTTP headers that are never fed into the HMAC computation [2](#0-1) . `Registry.process` only calls `Utils::HmacValidator.validate(request)`, which checks the body's HMAC, then dispatches the handler using the unauthenticated `request.shop` and `request.topic` values [3](#0-2) .

### Title
Webhook shop/topic attribution not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature that `Utils::HmacValidator.validate` checks in `Registry.process` binds solely to the body bytes. The `shop`, `topic`, `api_version`, and `webhook_id` values, all consumed by `Registry.process` to route and attribute the webhook, come exclusively from HTTP headers that are excluded from the signed content.

### Finding Description
The intended identity binding is: `hmac == HMAC(secret, shop || topic || body)` (or equivalent), so that the shop attribution of a webhook cannot be forged. Instead, the actual binding enforced is `hmac == HMAC(secret, body)` only [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors read from headers via `shopify_header`, which are never part of the signed string [2](#0-1) [4](#0-3) .

`Registry.process` validates only the HMAC of the object (i.e., only the body) and then immediately hands `request.shop` and other header-derived fields to the app's handler as trusted metadata [5](#0-4) . Because a body with a given content and a given HMAC remains valid regardless of what shop/topic headers accompany it, any entity capable of obtaining one genuine `(body, hmac)` pair signed with the app's `api_secret_key` (for example, by installing the app on their own test store and receiving one legitimate webhook) can resend that exact body with a *different* `shopify-shop-domain` (and/or `shopify-topic`) header value. The HMAC check still passes because it only ever re-derives the digest from the body, so the request is processed as if it genuinely originated from the spoofed shop.

### Impact Explanation
This breaks the equality the host application relies on for tenant isolation: `authenticated_body_signature == binds(shop_claimed_in_metadata)`. An attacker-controlled shop (a shop the attacker legitimately installed the app on) can forge webhook deliveries that are attributed to an arbitrary victim shop domain, since `shop` is never covered by the HMAC. Any host application that uses `WebhookMetadata#shop` to look up per-tenant records, trigger per-tenant side effects, or otherwise trust the shop attribution without independent verification is exposed to cross-tenant data injection/impersonation via forged webhook payloads. This matches the Critical-tier "cross-tenant access" impact category, since it lets one tenant inject events attributed to a different tenant.

### Likelihood Explanation
The `shopify-shop-domain`, `shopify-topic`, `api-version` and `webhook-id` headers are ordinary, unauthenticated HTTP headers under the sender's control at the transport layer; nothing in `ShopifyAPI::Webhooks::Request` or `Registry.process` ties them to the signed body. An attacker only needs one legitimately-signed webhook body (trivially obtainable by installing the app on their own store, which is an unprivileged action) to then replay it with swapped headers against the same webhook endpoint, so exploitation likelihood is high wherever the host relies on this gem's own HMAC check as the sole authenticity/attribution guarantee.

### Recommendation
Include the shop domain (and ideally topic) in the value that `to_signable_string` signs, or have `Registry.process`/`Utils::HmacValidator.validate` cross-check that the `X-Shopify-Shop-Domain` header matches an out-of-band expected value (e.g., a per-tenant secret or session lookup) before dispatching to the handler, rather than trusting header-derived `shop`/`topic` purely because the body's HMAC validated.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and configures a webhook (e.g., `orders/create`).
2. Shopify sends a legitimate webhook: body `B`, headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker captures `(B, HMAC(secret, B))` and resends the exact same POST to the app's webhook endpoint, but with `shopify-shop-domain: victim.myshopify.com` (and any desired `shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` from `to_signable_string` (the body only) and finds it matches — passing validation [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop` is `"victim.myshopify.com"`, even though the request never actually originated from or was signed on behalf of that shop [7](#0-6) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
