### Title
Webhook `topic`, `shop-domain`, `api-version` and `webhook-id` are trusted from unauthenticated HTTP headers while only the raw body is HMAC-verified - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable material solely from the raw request body [1](#0-0) , while the `topic`, `shop`, `api_version`, and `webhook_id` fields consumed by `Registry.process` are read directly from HTTP headers that are never included in the signed payload [2](#0-1) . `Registry.process` validates only the HMAC and then dispatches the handler using these unauthenticated header values as tenant/topic identity [3](#0-2) .

### Finding Description
The identity binding that should hold is: `hmac_covers(shop, topic, body) == fields_used_by_handler(shop, topic, body)`. In this gem, the HMAC is computed only over `@raw_body` [4](#0-3) , but `Registry.process` builds the `WebhookMetadata` passed to the app's handler from `request.topic`, `request.shop`, `request.api_version`, and `request.webhook_id`, all sourced from headers outside the HMAC's scope [5](#0-4) .

Because Shopify webhook HMACs are computed with the app's single `client_secret`/`api_secret_key`, which is identical for every shop that has installed the app, any shop that legitimately installs the app can capture a fully valid `(body, hmac)` pair from its own genuine webhook deliveries. That attacker-controlled merchant (an "unprivileged" party with respect to any *other* tenant of the same app) can then replay the exact same body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`Webhook-Id`) header with a different shop's domain. `Utils::HmacValidator.validate(request)` in `Registry.process` [6](#0-5)  will still pass, because the HMAC only ever checked the body, and the forged `shop` header will flow straight into the handler's `WebhookMetadata`, breaking the equality `shop_authenticated == shop_used_by_handler`.

Before the attack: the app's stored belief is that a webhook with `shop == "victim.myshopify.com"` can only be produced by Shopify sending data that originated from the victim shop. After the attack: an attacker who only controls their own shop's install can produce a `(body, hmac)` pair that the library reports as valid for `shop == "victim.myshopify.com"`, since the shop field was never bound to the signature.

Any host application that trusts `WebhookMetadata#shop` (e.g., to look up which merchant/session the payload belongs to, without re-validating shop against its own webhook subscription mapping) is exposed to cross-tenant data confusion — e.g., processing/crediting a webhook body (order, GDPR redact request, app-uninstall, etc.) against the wrong tenant's session/store data.

### Impact Explanation
This crosses a tenant boundary without needing the app's `client_secret` or any privileged credential — only a standard install of the target app on the attacker's own shop is required, which is available to any unprivileged merchant/internet user who installs a public app. If the host application (following this gem's documented pattern in `docs/usage/webhooks.md`) keys any authorization or data-association decision off `WebhookMetadata#shop`, an attacker can cause the library to report a forged shop identity for an otherwise-legitimate signed payload, resulting in cross-tenant data confusion/access. This satisfies the "cross-tenant access" Critical-impact category since it is a genuine identity-binding break, not merely a design choice the host app must additionally validate — the vulnerable binding lives entirely inside this gem's `Request`/`Registry` code.

### Likelihood Explanation
Likelihood is high for any multi-tenant app using this library's webhook processing exactly as documented (`ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(...))`, per `docs/usage/webhooks.md`). The attacker only needs their own legitimate install to harvest a valid `(body, hmac)` pair and can then freely modify unauthenticated headers before replaying to the shared webhook endpoint.

### Recommendation
Bind the HMAC to the values actually used for tenant/topic dispatch. Either:
- Extend `to_signable_string` (or introduce a separate integrity check) to include `shop`, `topic`, and `webhook_id`/`api_version` alongside the raw body, or
- Require the host application (and document explicitly) that `WebhookMetadata#shop`/`#topic` must never be trusted as an identity boundary and must instead be cross-checked against the shop's own registered webhook subscription/session before acting on the payload.

At minimum, the library should not silently hand out `shop`/`topic`/`webhook_id` fields sourced from unauthenticated headers as if they were part of the verified payload in `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a legitimate webhook (e.g., `orders/create`) and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header sent to their app's webhook endpoint — this is a valid `(body, hmac)` pair under the app's shared `api_secret_key`.
3. Attacker resends the identical body and `X-Shopify-Hmac-Sha256` header to the same webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (unmodified) body against the HMAC [6](#0-5) .
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` [5](#0-4) , with the library reporting the forged shop as authenticated, even though the body's content and HMAC prove nothing about which shop it actually pertains to.

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
