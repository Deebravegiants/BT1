Based on my analysis, this confirms the vulnerability. The `WebhookMetadata.shop` field, which host applications use to identify the tenant for a webhook, comes directly from the unauthenticated `x-shopify-shop-domain` header, while the HMAC only covers the raw body.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC only over the raw request body via `to_signable_string`, while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers with no cryptographic binding to that HMAC. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then passes the unauthenticated `shop` header straight to the host app's handler as `WebhookMetadata#shop`.

### Finding Description
`Request#hmac` decodes the `x-shopify-hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The HMAC secret (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that has installed the app, so a valid HMAC for a given body is not shop-specific — it is a function only of the body bytes and the app secret.

`Registry.process` validates that HMAC and, if valid, immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, etc., taken from headers that are never included in the signed data: [2](#0-1) .

The intended equality the protocol needs is: `shop that authorized/sent this webhook == shop the app processes the payload for`. Because only the body is signed, an attacker who has legitimate access to their own shop (an ordinary, unprivileged merchant/installer of the app — not a privileged account) can:
1. Trigger a real webhook from their own shop (e.g. `orders/create`), capturing a body + valid `x-shopify-hmac-sha256` for that body under the app's shared secret.
2. Replay that exact body and HMAC to the app's public webhook endpoint, but with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header rewritten to name a victim shop.
3. `Utils::HmacValidator.validate` still succeeds (body/HMAC pair is untouched), and the handler receives `WebhookMetadata` claiming the payload belongs to the victim shop.

This breaks the binding `shop authenticated (via HMAC) == shop acted upon (used to route/store data)`, since the HMAC authenticates only the byte content, not the header that host applications use to select the tenant record.

### Impact Explanation
Any host application built on this gem that uses `WebhookMetadata#shop` to look up or mutate shop-scoped records (the documented, expected usage pattern in `docs/usage/webhooks.md`) can be made to attribute attacker-controlled webhook data to a different tenant than the one that actually sent it. This is a cross-tenant data-integrity/access issue: an unprivileged app installer can inject or corrupt data associated with another merchant's shop record purely by controlling headers on a replayed request, without possessing any of the victim's credentials.

### Likelihood Explanation
Exploitation requires only: (a) installing the app on an attacker-controlled shop (trivial, self-service), (b) triggering an event that fires a webhook to the app (trivial, e.g. placing/cancelling an order in the attacker's own store), and (c) sending an HTTP POST with a substituted header value to the app's public webhook endpoint. No secrets, tokens, or elevated access are required — the `client_secret` is never exposed to the attacker, but it isn't needed since the HMAC already exists for the captured body.

### Recommendation
Bind the tenant identity into the signed payload verification path rather than trusting header values: either (a) include `shop`, `topic`, and `webhook_id` in the HMAC-covered signable string (this would require Shopify's own signing scheme to change, so is not gem-side feasible alone), or (b) have `Registry.process`/`HmacValidator` cross-check that the shop domain in the header matches an expected/registered shop before invoking the handler, and document clearly that `WebhookMetadata#shop` is not itself authenticated by the HMAC and must be validated by the host app against its own shop registry before being trusted for tenant-scoped operations.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the app.
# 1. Attacker triggers orders/create on their own shop, Shopify sends:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => "<valid HMAC of body under shared app client_secret>",
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
  "x-shopify-webhook-id" => "real-id",
  "x-shopify-api-version" => "2024-01",
}
body = '{"id": 1, "malicious": "payload"}'

# 2. Attacker replays the identical body+hmac but swaps the shop header:
spoofed_headers = headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: spoofed_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate succeeds (only body is checked) -> handler.handle
# receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker's payload)
``` [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
