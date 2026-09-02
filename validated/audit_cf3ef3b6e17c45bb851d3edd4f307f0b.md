### Title
Webhook shop identity is taken from an unauthenticated HTTP header, not from the HMAC-covered body - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id` and `api_version` values taken from HTTP headers that are **not** covered by that HMAC. Because the app's `api_secret_key` is shared across every shop that installs the app, any merchant who installs the app on their own store legitimately receives genuine, validly-signed webhook deliveries. That attacker-controlled merchant can capture one such valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header swapped to a victim shop, producing a request that still passes `HmacValidator.validate` while the resulting `WebhookMetadata` reports the victim's shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers, entirely outside the signed material: [2](#0-1) 

`Registry.process` validates the request using exactly this HMAC-over-body check, then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to build the metadata handed to the host app's handler: [3](#0-2) 

The binding this breaks is: `shop used to route/authorize handler logic` should equal `shop cryptographically bound to the signed bytes`, but here `shop` is a bare header value that travels alongside — not inside — the HMAC-verified payload. `HmacValidator.validate` (shared by both OAuth and webhooks) only proves that `to_signable_string` was signed with the app secret; for webhooks that string is just the body, so the validator gives no guarantee at all about which shop or topic the signature is "for."

Because `api_secret_key`/`client_secret` is one value per app, shared across all merchants who install that app, an ordinary unprivileged internet user can install the target app on their own store (a normal, unprivileged action), and Shopify will deliver genuine webhooks signed with that same shared secret. The attacker can then take one legitimately-received `(raw_body, x-shopify-hmac-sha256)` pair and re-POST it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain (and, if the body shape matches, `x-shopify-topic` rewritten too). `HmacValidator.validate` still succeeds because it only checks the body bytes against the (correctly computed) HMAC; `Registry.process` then dispatches the handler with `shop: request.shop` equal to the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an unprivileged merchant of an app can cause the host application's webhook handler to execute with a shop identity of their choosing (any other shop's domain), rather than the shop that actually generated the signed payload. Depending on how the host app's `WebhookHandler#handle` implementation keys off `WebhookMetadata#shop` (e.g., to look up/update per-shop records, revoke access, or write redaction data), this can lead to cross-tenant data corruption or disclosure — the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is limited by the fact that a body must be re-shaped/matched for a chosen topic and that most webhook bodies also embed shop-identifying data (e.g., `myshopify_domain`) that a careful handler could cross-check — but the library itself provides no such cross-check and nothing in `lib/shopify_api/webhooks/**` binds the header-derived `shop`/`topic` to the signed bytes. Any app relying on the gem's documented `Registry.process` + `WebhookMetadata#shop` contract as an authenticity guarantee (as the gem's own docs and tests imply) is exposed. Obtaining one genuine signed webhook only requires installing the app once as an ordinary user.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) inside the HMAC-signed material, or otherwise cryptographically bind them to the body (e.g., derive an internal signable string from headers+body rather than body alone) so `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` actually authenticates the shop/topic the caller relies on, not just the byte content of the body.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` (normal, unprivileged flow) and triggers a webhook whose topic/body shape matches a sensitive topic the app registers (e.g., `customers/data_request`), receiving a genuine `x-shopify-hmac-sha256` value computed over that specific `raw_body` with the app's shared `client_secret`.
2. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes the HMAC over `@raw_body` (`to_signable_string`) — unaffected by the header change.
4. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))`, so the host application's handler now acts on behalf of `victim-shop.myshopify.com` using a payload the attacker fully controlled from their own installation.

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
