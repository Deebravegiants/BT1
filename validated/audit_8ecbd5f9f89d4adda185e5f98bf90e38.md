### Title
Webhook shop-domain header is trusted for tenant identification but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then unconditionally trusts the `shop` value taken from the `x-shopify-shop-domain` header (which is not part of the signed material) to identify which merchant/tenant the payload belongs to.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string`, and for webhooks that string is exactly the raw request body: [1](#0-0) [2](#0-1) 

The signable string returned by `to_signable_string` is only `@raw_body`, meaning the `shop` header (`shopify-shop-domain` / `x-shopify-shop-domain`) is never included in the bytes that are HMAC-verified: [1](#0-0) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using `request.shop`, handing it to the app's handler as the authoritative tenant identity, with no cross-check that this shop is bound to the verified body: [3](#0-2) 

This breaks the intended identity binding: `hmac_verified(body) == true` is treated as equivalent to `hmac_verified(body, shop) == true`, but the `shop` field is parsed from an unauthenticated header, not covered by the signature. Since the HMAC secret (`api_secret_key`) is shared across every shop that installs the app, any unprivileged user who installs the app on their own store receives legitimate webhooks correctly signed with the app's secret for their own shop. Such a user can capture one `(raw_body, hmac)` pair from their own store's webhook deliveries and replay it to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value (e.g., a victim's shop). The HMAC still validates because the header is not part of the signed content, so `Registry.process` invokes the handler with `WebhookMetadata.shop` set to the attacker-chosen value, while the actual signed body content originated from the attacker's own store.

### Impact Explanation
Because `data.shop` is documented and expected to be used by the host application to select/scope tenant records (per `docs/usage/webhooks.md`, `data.shop` is "The shop domain of the webhook"), an attacker-controlled shop value combined with a validly-signed body allows spoofed cross-tenant webhook events to be injected into a target shop's data pipeline — an cross-tenant access/injection vulnerability using only a legitimate app-install by the attacker, no theft of credentials or `api_secret_key` required.

### Likelihood Explanation
Any user can install a public app on their own store (unprivileged), which routinely triggers real webhook deliveries validly signed with the shared `api_secret_key`. Forging the `shop`-domain header on an HTTP POST to the app's public webhook endpoint requires no special access — only knowledge of the endpoint path, which is typically fixed and discoverable. This makes exploitation straightforward for anyone who can install the target app.

### Recommendation
Bind the `shop` identity to the HMAC-verified content instead of trusting an unauthenticated header value in isolation — e.g., include the shop domain in the signable material, or require the caller of `Registry.process` to supply/verify the expected shop out-of-band (such as matching against a known, previously-registered shop/session) before dispatching to the handler. At minimum, document prominently that `data.shop` is unauthenticated and must not be trusted for tenant-scoped writes without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`; the app registers webhooks for `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook to the app for `attacker.myshopify.com`'s data, signed with the app's shared `api_secret_key`: headers include `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `raw_body` and `x-shopify-hmac-sha256`.
4. Attacker POSTs the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the signature — the spoofed shop header is never checked.
6. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(... shop: "victim.myshopify.com" ...))`, causing the app to process attacker-controlled webhook content as if it belonged to `victim.myshopify.com`.

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
