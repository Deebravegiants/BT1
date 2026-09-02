## Finding: Webhook `shop` (tenant) identifier is not covered by the HMAC signature

### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, but the `shop` value used downstream to identify which merchant/tenant the webhook belongs to is read from an HTTP header that is never included in that signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` (invoked in `Registry.process`) only proves that the *body bytes* were signed with the app's secret — it proves nothing about the accompanying headers. [1](#0-0) 

`Request#shop` is read directly from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates only the HMAC, then hands `request.shop` straight to the app's handler as the tenant identifier, with no cross-check against anything covered by the signature: [3](#0-2) 

This breaks the intended identity binding: `shop_that_signed(body) == shop_trusted_by(handler)`. The gem verifies `hmac == HMAC(secret, raw_body)`, but the `shop` field consumed by `WebhookMetadata` (and thus by every registered handler) is entirely outside that proof. Any party able to produce one valid `(raw_body, hmac)` pair for the app's shared secret — e.g., by installing the (often public) app on their own store and capturing a legitimate webhook delivery sent to a self-hosted/dev instance of the app — can replay that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header. `Registry.process` will accept it as authentic and dispatch it to the handler tagged with the victim shop's domain, since the header is never re-derived from, or checked against, the signed content.

### Impact Explanation
This is a cross-tenant integrity issue: an attacker-controlled webhook body can be attributed to any shop of the attacker's choosing. Depending on how a host application's handler uses `WebhookMetadata#shop` (e.g., to look up the tenant's session/store record and update state, such as `orders/create`, `app/uninstalled`, or shop data-sync handlers), this allows a low-privilege user (any merchant capable of installing the app on their own store) to inject or overwrite data attributed to a different, unrelated merchant — a cross-tenant access/data-integrity break, without needing the target's access token or credentials.

### Likelihood Explanation
The prerequisite is only the ability to obtain one valid `(body, hmac)` pair signed with the app's shared secret for *any* shop, plus a way to send an arbitrary HTTP POST with custom headers to the app's public webhook endpoint — both of which are within reach of any unprivileged user who installs the target app (many Shopify apps are public/installable, and self-hosted or dev instances of the app make interception straightforward). No merchant access token, refresh token, or `client_secret` for the target shop is required.

### Recommendation
Do not trust the `shop-domain` header as a tenant identifier unless it is cryptographically bound to the signed payload. Either:
- Include the shop/topic/webhook-id headers in the signable string used for HMAC verification (matching what Shopify actually signs, if broader coverage is available), or
- Require callers of `Registry.process` to independently authenticate/authorize the resolved `shop` (e.g., verify it corresponds to an existing installed session) before acting on the webhook payload, and document this requirement clearly since the gem currently implies HMAC validation alone is sufficient for `process`.

### Proof of Concept
1. Install the target app (self-hosted, dev store, or via a proxy under attacker's control) so that a legitimate webhook (e.g., `orders/create`) is delivered to an endpoint the attacker observes, capturing the raw body and its valid `x-shopify-hmac-sha256` value (both signed with the app's real, shared `api_secret_key`).
2. Replay that exact `raw_body` and `hmac` header to the app's public webhook endpoint, but replace `x-shopify-shop-domain` with the victim shop's domain.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, raw_body)` — this still matches, so validation passes. [4](#0-3) 
4. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` is the attacker-forged victim domain, causing the app to process/act on attacker-controlled data as if it originated from the victim's store.

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
