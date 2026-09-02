### Title
Webhook `shop` (and `topic`) Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the shop identity used to dispatch the webhook to application handlers is read from an unrelated, unsigned header. Any attacker who can produce one valid `(body, hmac)` pair for a webhook (e.g., a legitimate merchant who has installed the app on their own store) can replay that pair while substituting the `shop-domain` header for a different tenant, and the gem will pass the attacker-chosen shop identity through to the handler as authenticated.

### Finding Description
`Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, which in turn calls `request.to_signable_string`: [1](#0-0) 

This returns only `@raw_body`, so the HMAC signature never covers the `shop`, `topic`, `webhook_id`, or `api_version` header values: [2](#0-1) 

Yet `Registry.process` uses these unauthenticated header values directly to build the `WebhookMetadata` struct that is handed to the app's `WebhookHandler`, without any check that the `shop` header actually matches the tenant to whom the signed body belongs: [3](#0-2) 

The identity-binding equality that should hold is:
`shop_that_produced_signed(body, hmac) == shop_passed_to_handler(data.shop)`

Because the HMAC only proves "this body was signed by the app's secret key at some point," and not "this body belongs to the shop named in this specific header," the equality can be broken. The gem's own documentation confirms `data.shop` is treated as a trusted tenant key by downstream code, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`: [4](#0-3) 

### Impact Explanation
A single shared webhook HTTP endpoint typically receives webhooks for every shop that has installed the app, differentiated only by the `shop-domain` header. Since this header is outside the HMAC's protection, an attacker (any merchant who has legitimately installed the app on their own store, and thus can trigger real webhooks with genuine `(body, hmac)` pairs) can re-post a captured payload against the same endpoint with a forged `shop-domain` header pointing at a victim shop. The gem will pass HMAC validation and dispatch the (attacker-controlled) body to the handler labeled as belonging to the victim shop, resulting in cross-tenant data injection/corruption in any app that keys stored webhook data by `data.shop` — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own legitimate app installation and (2) the ability to POST an HTTP request with custom headers to the app's public webhook endpoint — both trivially available to any unprivileged internet user/merchant. No access to `api_secret_key`, access tokens, or privileged accounts is required, since the attacker uses their own genuinely-issued, valid webhook payload and simply changes an unauthenticated header value.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the header values to the payload, before trusting them:
- Prefer verifying the webhook against a specific expected shop (e.g., require callers of `Registry.process` to supply the expected shop/session and assert it against `request.shop`), rather than trusting the header unconditionally.
- At minimum, document prominently that `data.shop`/`data.topic`/`data.webhook_id` are NOT covered by the HMAC and must not be treated as authenticated identifiers on their own; require host applications to cross-check `data.shop` against known installed shops before persisting/attributing webhook data.

### Proof of Concept
1. Install the app normally on attacker-controlled store `attacker.myshopify.com`, then trigger a real event (e.g., `orders/create`) so Shopify sends a legitimate webhook with a valid `X-Shopify-Hmac-Sha256` value computed over the JSON body using the app's `api_secret_key`.
2. Capture the raw body and its valid HMAC value.
3. Re-POST the identical body and HMAC header to the same webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) body against the (unchanged) HMAC — see `lib/shopify_api/webhooks/request.rb` `to_signable_string`/`hmac` and `lib/shopify_api/webhooks/registry.rb` `process`.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: <attacker's order data> ...)`, causing the application to attribute attacker-controlled data to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
