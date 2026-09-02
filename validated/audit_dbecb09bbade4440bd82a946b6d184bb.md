This is a genuine finding: the webhook `shop` field used to identify the tenant is **not covered by the HMAC signature**.

### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the request body, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw body [1](#0-0) , but the `shop` value handed to the app's handler is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is excluded from the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` decodes the `hmac-sha256` header value [2](#0-1) . The `shop` attribute is read from `shopify_header("shop-domain")`, a plain unauthenticated HTTP header, and is never included in the HMAC-signed material [3](#0-2) . `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` — which only proves the *body bytes* were signed with the app's secret — and then immediately forwards `request.shop` to the handler as the tenant identifier without any additional binding check [1](#0-0) .

This breaks the intended binding: `shop_header == shop_that_produced_the_signed_body`. Since Shopify signs `HMAC-SHA256(secret, raw_body)` and the same secret is shared across all shops installed on an app, a party who can obtain one valid `(raw_body, hmac)` pair for shop A (e.g., by triggering an event on their own installed/test shop, or replaying a captured legitimate webhook) can resend that identical body+HMAC to the app's webhook endpoint with the `shop-domain` header changed to shop B. The signature still validates (it only checks the body), but the handler executes business logic (e.g., `customers/redact`, order/product updates, data deletion) believing it originates from shop B.

### Impact Explanation
This allows cross-tenant confusion: an attacker-controlled or legitimately-owned shop can produce validly-HMAC'd bodies and, by manipulating only the header (which travels over the same secret-less channel and is not part of the signed payload), have the app process the payload under a different, victim tenant's identity in `WebhookMetadata` — impacting apps that use `shop` from `WebhookMetadata` to determine which store's session/data to act on (e.g., mandatory `customers/redact` handlers, data-sync jobs). This satisfies "cross-tenant access" territory under the report's rules since the exploit forges the shop identity claim of a webhook that is only nominally authenticated for its body.

### Likelihood Explanation
Likelihood is Medium: the attacker needs at least one previously observed valid `(body, hmac)` pair signed with the shared app secret (obtainable from their own installed shop invoking a webhook, or from a captured/replayed webhook), and then only needs to alter the unauthenticated `shop-domain` header on the replay request — no possession of `api_secret_key` or an access token is required, matching the "shop authenticated versus shop stored as identity" analog called out in the rules.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) header values inside the HMAC-signed payload verification, or independently bind the `shop-domain` header to the raw body’s originating shop (e.g., verify that the shop asserted in the header matches metadata embedded in and covered by the signed body, or require the app layer to correlate `webhook_id`/idempotency with a shop-specific record) before dispatching to handlers.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com` (both under the same app / secret).
2. Trigger any webhook event on `shop-a` to capture a legitimate `(raw_body, x-shopify-hmac-sha256, x-shopify-shop-domain: shop-a...)` request.
3. Resend the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replace the header `x-shopify-shop-domain` with `shop-b.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` in `Registry.process` succeeds (body/hmac untouched) [4](#0-3) , and the handler is invoked with `WebhookMetadata` reporting `shop: "shop-b.myshopify.com"` [5](#0-4) , even though the payload actually originated from `shop-a`.

### Citations

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
