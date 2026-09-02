### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` authenticates an inbound webhook via `Utils::HmacValidator.validate(request)`, but the HMAC only ever covers the raw request body. The `shop` value that is later used as the tenant identifier for the webhook (`WebhookMetadata#shop`, passed straight to the app's `WebhookHandler`) comes from an HTTP header that is completely outside the signed payload. This breaks the identity binding `authenticated(request) == shop-that-owns(request)`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `Webhooks::Request#shop` is read from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates the HMAC once, over the body, and then trusts `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version` — also all header-derived and unsigned) when constructing the `WebhookMetadata` object that is handed to the app's handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain struct field with no independent verification: [4](#0-3) 

This is exactly the class of bug described by the rules: a field (`shop`) that is *acted on* (used by the host app as the tenant/session key to route or persist data) but is *not covered by the HMAC* that the gem uses to assert authenticity of the message. `HmacValidator.validate` only proves "this body was signed with our client secret" — it proves nothing about which shop the body belongs to, because `shop` is never part of `to_signable_string`.

### Impact Explanation
Any actor who can obtain one legitimately-signed webhook payload (e.g., by installing the app on their own store and receiving webhooks for it) can replay that exact body+HMAC pair while substituting an arbitrary `shopify-shop-domain` header for a different (victim) shop. `HmacValidator.validate` will still succeed because the header is not part of the signed string, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim shop as the source. Any host application that uses `data.shop` from the gem to look up per-tenant state (e.g., to know which merchant's data/session to update) can be tricked into attributing attacker-controlled data to another tenant — a cross-tenant confusion/spoofing primitive delivered entirely through the gem's own "authenticated" webhook API.

### Likelihood Explanation
The only precondition is having one valid HMAC-signed webhook body, which any developer/merchant can obtain by installing the app on a store they control (a normal, unprivileged action, not requiring the app's `client_secret` or a leaked token). From there, forging the `shop-domain` header on a replayed request is trivial since the gem's `validate_signature` check never inspects it.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the material the app is expected to trust only after independent verification, and document/require that host apps cross-check `request.shop` against a known, previously-established tenant record (e.g., an existing offline session for that shop) before acting on webhook data — the gem should not present `WebhookMetadata.shop` as if it were authenticated by the HMAC check performed in `Registry.process`.

### Proof of Concept
1. Install the app on attacker-owned store `attacker.myshopify.com`; capture one webhook delivery, e.g. `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid signature over raw_body>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-topic: orders/create`
2. Replay the identical `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC — the shop header is not part of `to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`).
4. The handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` and processes/stores data as if it originated from `victim.myshopify.com`, even though the payload actually came from the attacker's own store.

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
