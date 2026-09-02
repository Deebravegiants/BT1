This confirms the finding. Here is the analog vulnerability.

### Title
Webhook `shop-domain` Header Not Bound to HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` identity used to route and label the delivered data to the app's handler is read from a separate HTTP header that is never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` accessor, however, is read independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely outside the HMAC-covered payload: [2](#0-1) .

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` (the body only) and compares it against `request.hmac` (also from a header): [3](#0-2) . After this check passes, the code immediately forwards `request.shop` — the unauthenticated header value — to the app's handler as the tenant identifier in `WebhookMetadata`: [4](#0-3) .

This is exactly the pattern flagged in the source report: a field (`shop`) that is acted upon (used to attribute/tenant-scope the webhook payload) but not covered by the HMAC that is supposed to authenticate the request. The binding that should hold is:

`HMAC-verified bytes == bytes that determine the tenant (shop) the payload is attributed to`

but the implementation instead verifies `HMAC(body)` while trusting `shop` from an independent, unauthenticated header — breaking that equality.

Because the app's documented `WebhookHandler#handle` interface receives `data.shop` as the trusted tenant identifier (see `docs/usage/webhooks.md` and `lib/shopify_api/webhooks/webhook_handler.rb` — `WebhookMetadata` struct) [5](#0-4) , any application that uses `shop` from `WebhookMetadata` to route webhook data to per-shop storage/queues (as the documentation explicitly recommends, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process the request under the shop domain the attacker supplies in the header, not the shop domain Shopify actually signed for.

### Impact Explanation
An attacker who legitimately owns/controls one Shopify store can trigger any webhook topic on their own store to obtain a genuinely-signed `(raw_body, hmac)` pair from Shopify. Because `shop` is not part of the signed content, the attacker can replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body bytes and secret), and the gem passes the forged `shop` value straight through to the handler. This enables cross-tenant data injection/confusion: the victim shop's webhook processing pipeline in the host application receives attacker-controlled body content attributed to the victim's tenant. Per the given scope, this qualifies as Critical — cross-tenant access, since the tenant boundary (`shop`) enforced by this gem's webhook API is not actually authenticated.

### Likelihood Explanation
Likelihood is high for any attacker who can install the same app on their own (attacker-owned) shop — a normal, unprivileged action requiring no special access to Shopify or the victim. No secrets, tokens, or the app's `client_secret`/`api_secret_key` need to be known; the attacker only needs a shop of their own to legitimately receive a validly-signed webhook to replay with a forged header.

### Recommendation
Include the `shop` domain in `to_signable_string`/the HMAC-verified material, or otherwise cryptographically bind the shop the webhook is attributed to (e.g. verify that the shop header matches a shop for which the app holds an active, previously-installed session/webhook registration, and reject any shop value not corroborated by app-side state) before constructing `WebhookMetadata` and invoking the handler. At minimum, document/require that the `shop` header alone must never be trusted for tenant attribution without an out-of-band verification step.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` and has the app installed there.
2. Attacker triggers any subscribed webhook (e.g. `orders/create`) on their own shop, capturing the exact raw POST body and the `X-Shopify-Hmac-Sha256` value Shopify sends — both valid, since Shopify signs the request with the app's real `api_secret_key`.
3. Attacker resends the same raw body and same `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but replaces `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate(request)` recomputes the HMAC solely over `@raw_body` and it matches, so `Registry.process` proceeds: [3](#0-2) .
5. The handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` with attacker-controlled `body`, causing the host application to process/store forged data under the victim shop's tenant.

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
