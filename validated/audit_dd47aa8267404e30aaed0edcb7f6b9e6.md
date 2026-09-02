### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, then hands the caller a `WebhookMetadata` struct whose `shop` field is read directly from the `X-Shopify-Shop-Domain` header, which is never covered by the HMAC signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` accepts the request as authentic once `Utils::HmacValidator.validate(request)` passes on that body [2](#0-1) . However, the `shop` used to build the trusted `WebhookMetadata` that is passed to the host app's handler is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header [3](#0-2) , a value that is completely outside the HMAC's signed content. The binding the gem should enforce is: `shop authenticated == shop the HMAC signature covers`. Instead, the gem enforces `body authenticated == raw_body signed`, while `shop trusted-and-forwarded-to-handler == shop header value (unauthenticated)`.

The HMAC secret (`Context.api_secret_key`, the app's client secret) is shared across every merchant/tenant using the app - it is not per-shop. That means any merchant who has installed the app can trigger a legitimate webhook delivery to their own endpoint (e.g., by creating an order in their own store), capture the resulting `(raw_body, hmac)` pair that is valid under the app-wide secret, and then resend that exact body+HMAC to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. `Registry.process` will still call `Utils::HmacValidator.validate` successfully (it only checks the body), and will pass `request.shop` — now the victim's domain — into `WebhookMetadata`, which downstream application code uses to attribute the payload to a tenant (e.g., to look up which merchant/session the webhook data belongs to).

### Impact Explanation
This breaks the shop/tenant identity binding a multi-tenant Shopify app relies on for webhook processing: data or an event legitimately generated in one tenant's store can be replayed and misattributed to a different tenant merely by changing an unauthenticated header, because the value the host application trusts as the shop is never part of the cryptographically verified content. Depending on how the host app uses `WebhookMetadata#shop` (e.g., loading the corresponding merchant/session record and applying the (attacker-controlled) event body to it), this enables cross-tenant data injection/corruption using only a shared secret every installed merchant is capable of exercising through normal use of the app - qualifying as cross-tenant access.

### Likelihood Explanation
Requires the attacker to be a merchant who has installed the app (an "unprivileged" party relative to other tenants, not requiring the app's `client_secret` or the platform's private credentials), plus the ability to intercept/replay their own webhook deliveries and re-POST to the public webhook endpoint with a modified header. No special access to Shopify's or the app's secrets is needed beyond what a legitimate merchant already receives from Shopify webhook deliveries to their own endpoint.

### Recommendation
Bind `shop` into the authenticated material, e.g. include the shop domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or require the host application to independently verify that the `shop` header matches a shop domain associated with the specific webhook subscription/session before trusting `WebhookMetadata#shop`. At minimum, document prominently that `Webhooks::Request#shop` is unauthenticated and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) for their own store, capturing the raw POST body and the valid `X-Shopify-Hmac-Sha256` header sent by Shopify (both computed with the app-wide client secret).
2. Attacker replays the exact same body and HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [4](#0-3) , which succeeds because it only checks `raw_body` against the shared secret.
4. `request.shop` returns `"victim-shop.myshopify.com"` from the header [3](#0-2) , and this value is placed into `WebhookMetadata` passed to the app's handler [5](#0-4) , causing the attacker-originated (but validly-signed) payload to be processed as if it belonged to the victim shop.

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
