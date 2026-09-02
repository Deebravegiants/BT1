### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are trusted for tenant attribution despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `ShopifyAPI::Utils::HmacValidator.validate` (used in `ShopifyAPI::Webhooks::Registry.process`) only proves that *some* body was HMAC-signed with the app's secret — it proves nothing about the `shop-domain`, `topic`, or `webhook-id` headers. Those unauthenticated headers are nonetheless used directly to build the `WebhookMetadata` struct that is handed to the app's handler as the tenant/topic identity for the event, exactly the "field acted on but not covered by the HMAC" pattern described in the reference report.

### Finding Description
`Request#hmac` reads the `hmac-sha256` header, and `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Registry.process` validates the HMAC over that signable string and, if valid, immediately trusts the *other*, unsigned headers (`topic`, `shop`, `webhook_id`, `api_version`) to build `WebhookMetadata` for the handler: [2](#0-1) 

`WebhookMetadata.shop` is a plain, unauthenticated struct field: [3](#0-2) 

The binding that should hold is:
`HMAC(secret, signed_bytes) == received_hmac` **AND** `signed_bytes ⊇ {shop, topic, webhook_id}` (the identity fields the handler acts on).

What actually holds is:
`HMAC(secret, raw_body) == received_hmac`, while `shop`, `topic`, and `webhook_id` come from headers that are outside `signed_bytes` entirely — i.e. `bytes verified ⊊ fields acted on`.

Because only the body is signed, anyone who has ever received one legitimate webhook delivery for **any** shop (e.g. their own store, or any shop that installed the same multi-tenant app) possesses a `(raw_body, hmac)` pair that will always pass `HmacValidator.validate`, regardless of which `shop-domain` / `topic` / `webhook-id` headers are attached to the replayed POST. The attacker can freely swap the `x-shopify-shop-domain` header to a victim shop and/or the `x-shopify-topic` header to any topic registered by the app, and `Registry.process` will still accept it and dispatch it to the app's handler tagged as belonging to the victim shop/topic.

### Impact Explanation
This breaks the cross-tenant identity boundary the HMAC check is supposed to enforce: a party who is not authorized for shop B (only ever received a webhook for shop A, which they control) can cause the app's webhook pipeline to process attacker-chosen body content under shop B's identity and an attacker-chosen topic. In a typical multi-tenant Shopify app, `WebhookMetadata.shop`/`topic` are used to select the tenant record/session and the business logic branch to execute (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`), so this allows cross-tenant data confusion/injection into another merchant's account context — matching the "Critical: cross-tenant access" impact bucket, since the identity binding the HMAC is meant to guarantee (this exact body belongs to this exact shop/topic) does not actually hold.

### Likelihood Explanation
Exploitation only requires possessing one legitimate `(body, hmac)` pair for the shared app secret — trivial for any merchant who has installed the app (a normal, unprivileged user relative to other tenants of the same app) or for anyone who can otherwise observe one webhook delivery. No access to `api_secret_key`, access tokens, or privileged accounts is needed beyond what any regular installer already has. This is a design-level gap in the gem's own `Request`/`Registry` code (`lib/shopify_api/webhooks/**`), not a misuse of a documented contract by the host app — the gem's documented `WebhookMetadata.shop`/`topic` fields are presented as validated/trustworthy once `Registry.process` succeeds.

### Recommendation
Bind the identity-bearing headers into the HMAC-verified surface (or otherwise cryptographically/tenant-scope them) before dispatch:
- Include `shop`, `topic`, and `webhook_id` in the signed material verified by `HmacValidator`, or
- Require callers to pass the expected shop/topic (from the already-authenticated session/tenant context) and assert equality against `request.shop`/`request.topic` before invoking the handler, or
- Document loudly, and enforce in `Registry.process`, that `WebhookMetadata.shop`/`topic` are unauthenticated hints that MUST be independently corroborated by the host app (e.g. against `Session` records) rather than treated as verified once HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives one legitimate webhook delivery, e.g.:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`
   - Body: `{"id": 1, ...}`
2. Attacker replays the exact same `raw_body` and `hmac-sha256` value, but changes the headers to:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic: <any topic the app has registered a handler for>`
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` accepts it (all required headers present) and `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which only re-computes HMAC over `raw_body` — it succeeds because the body/hmac pair is unchanged: [4](#0-3) 
4. The registered handler is invoked with `WebhookMetadata.new(topic: "<attacker-chosen>", shop: "victim.myshopify.com", body: <attacker's original body>, ...)`, so the app processes attacker-supplied data as an authentic event for `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
