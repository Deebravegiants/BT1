Confirmed: the `shop` field passed into `WebhookMetadata` for the merchant/tenant identification is read directly from the `x-shopify-shop-domain` HTTP header and is **not** part of the HMAC-signed payload, which covers only the raw request body.This confirms the finding: `WebhookMetadata.shop` is a `const` field populated directly from `request.shop`, which the `Registry.process` handler trusts for tenant attribution ` [1](#0-0) `, while the HMAC signature only ever covers the raw body via `to_signable_string` ` [2](#0-1) `.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop`, `topic`, `api_version`, and `webhook_id` fields from raw, unauthenticated HTTP headers, while `Utils::HmacValidator.validate` only verifies the HMAC over the raw request body. The `shop` value is then trusted as-is and handed to the app's webhook handler as the tenant identity, without that value ever being covered by the cryptographic signature.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)` [1](#0-0) , which computes/compares the HMAC against `request.to_signable_string`. That method returns only `@raw_body` [2](#0-1) .

Meanwhile, `Request#shop` reads the `x-shopify-shop-domain` (or `shopify-shop-domain`) header verbatim [3](#0-2) , and this value is passed straight into `WebhookMetadata.shop`, which is delivered to the app's `WebhookHandler#handle` as the authoritative tenant identifier for the event [1](#0-0) [4](#0-3) .

This breaks the intended binding: `shop attributed to the event == shop that produced the signed body`. Because the `shop-domain` header sits entirely outside the HMAC-covered bytes, the same valid `(raw_body, hmac)` pair remains valid no matter what `shop-domain` header accompanies it. Any party who can obtain one genuine, correctly-signed webhook body for their own shop/topic (trivial for any merchant who installs the app, since Shopify sends real webhooks the merchant can observe) can resend that exact body/HMAC pair to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still succeed (it never inspects the header), and the handler will process the event as if it belongs to the attacker-chosen shop.

### Impact Explanation
This crosses a tenant boundary using only the app's own webhook secret (`Context.api_secret_key`), which is shared across all merchants of the app — no privileged credentials of the victim shop are required. An attacker-controlled or attacker-observed valid webhook can be replayed against the endpoint while claiming to originate from a different, victim shop. Any app logic that uses `WebhookMetadata.shop` to select which merchant's data/record to update, delete, or act upon (a very common webhook handler pattern, e.g. `customers/redact`, `orders/updated`, `app/uninstalled`) can be tricked into operating on the wrong tenant's data — a cross-tenant access/integrity issue, matching the Critical impact bar of "cross-tenant access."

### Likelihood Explanation
Exploitation requires only capturing or generating one legitimately HMAC-signed webhook body (any merchant installing the app receives real signed webhooks they can capture, since they control their own store's webhook deliveries), then replaying it with a forged `shop-domain` header. No secret material or privileged access to the victim shop is needed. The main constraint is that the replayed body's contents (e.g., resource IDs) must be meaningful in the context of the spoofed shop for handler logic to actually be harmed, which limits blast radius for some topics but not all (e.g., `app/uninstalled`, `shop/redact` carry shop-scoped semantics from the body itself and are less exploitable this way, but handlers keyed purely on `data.shop` for record lookups are exposed).

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the HMAC-signable representation (or otherwise cryptographically bind them, e.g. `to_signable_string` should combine header fields with the body before validation), so any tampering with the `shop-domain` header invalidates the signature. At minimum, document and enforce that `WebhookMetadata.shop` must never be trusted as an authenticated tenant identifier unless it is included in the signed bytes.

### Proof of Concept
1. Register a webhook handler that on `handle(data:)` looks up/updates a local record keyed by `data.shop` (a supported and common usage pattern per `docs/usage/webhooks.md`).
2. As a merchant with the app installed, capture one legitimate webhook delivery (raw body + `x-shopify-hmac-sha256` header) sent by Shopify to your own endpoint for shop `attacker-shop.myshopify.com`.
3. Replay the exact same raw body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the raw body against the HMAC [5](#0-4) .
5. The handler receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` and performs its action against the victim shop's data, even though the payload was never actually signed for that shop.

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
