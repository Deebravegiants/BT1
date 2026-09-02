### Title
Webhook `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies nothing but body integrity. The `shop`, `topic`, `webhook_id`, and `api_version` values, which are read straight from unauthenticated HTTP headers and handed to the webhook handler as trusted identity fields, are never bound to that signature. This mirrors the reported bug class: a field is *acted on* (used to attribute the event to a tenant and to select the handler) but is not *covered* by the cryptographic check meant to authenticate the request.

### Finding Description
`Request#hmac`/`#to_signable_string` compute/verify HMAC over `@raw_body` alone: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are pulled from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e., only the body), then dispatches based on the unauthenticated `topic` header and forwards the unauthenticated `shop` header straight into the handler payload: [3](#0-2) 

Because the app's `api_secret_key` is shared across every tenant installation (it's not per-shop), any body+HMAC pair that Shopify legitimately signed for **one** installation (e.g., the attacker's own shop, if the app is public) remains a numerically valid signature for that exact body regardless of which shop, topic, or webhook-id headers accompany it. The binding that should hold is: `shop header used by handler == shop that Shopify actually generated this webhook for`. Before the attack, both sides are equal (Shopify sends `shop-domain: attacker-shop.myshopify.com` alongside a body it also HMAC's for that event). After the attacker replays the same raw body/HMAC with a modified `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) header, the HMAC check still passes, but the shop/topic used by the handler no longer match the tenant Shopify actually originated the event for — the equality is broken while `HmacValidator.validate` still returns `true`.

### Impact Explanation
An attacker who can get any legitimate webhook delivered to the app's endpoint (trivially achievable if the app is a public/multi-tenant app the attacker can install on their own store, or if the attacker's own store triggers ordinary events like `orders/create`) can capture a valid `(raw_body, hmac)` pair and replay it with an arbitrary victim `shop-domain` header and/or a different `topic` header. The registry's HMAC check still succeeds because it only checks the body, so the forged event is processed and handed to the host application's handler as `WebhookMetadata.new(topic: <attacker-chosen>, shop: <victim-shop>, ...)`. Depending on how the host app's webhook handlers act on this data (create/update/delete records keyed by `shop`), this is a cross-tenant data injection/spoofing primitive — the impact category explicitly listed as Critical ("cross-tenant access").

### Likelihood Explanation
Likelihood is moderate-to-high for any app that is installable by unprivileged internet users (most public Shopify apps): all that's required is capturing one's own legitimately-delivered webhook request (body + HMAC header), then replaying it with modified `shop-domain`/`topic` headers to the same publicly reachable webhook endpoint. No access to `api_secret_key`, tokens, or another merchant's credentials is required.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed/verified payload, or otherwise cryptographically bind them to the body before dispatch — e.g., verify that the `shop-domain` header matches the shop associated with the session/registration expected for that HMAC, or require the host application to independently confirm the shop identity (as Shopify's own webhook verification guidance intends the HMAC to cover the full raw body per delivery, but the *headers* still need to be trusted only when TLS+source is otherwise validated). At minimum, document that the `shop`/`topic` headers are unauthenticated in this gem and must not be trusted for tenant attribution without additional out-of-band verification (e.g., checking the shop exists in the app's own registered/installed-shops list rather than blindly trusting the header).

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker-shop.myshopify.com` and triggers a real webhook event (e.g. `orders/create`), capturing the exact raw POST body `B` and the `X-Shopify-Hmac-Sha256: H` header Shopify sent to the app's webhook endpoint.
2. Attacker resends an HTTP POST to the same webhook endpoint with the identical body `B` and identical `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only [4](#0-3)  — validation succeeds because the body/HMAC pair is untouched.
4. The handler set for `request.topic` is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [3](#0-2) , using the attacker-controlled `shop`/`topic` values as if Shopify itself had generated this event for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
