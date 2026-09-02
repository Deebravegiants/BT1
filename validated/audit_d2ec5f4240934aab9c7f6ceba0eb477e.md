### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header is trusted for tenant identity without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to route and attribute the webhook are all read from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` and compares its HMAC against the `hmac-sha256` header: [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

But the tenant-identifying `shop` field (and `topic`, `webhook_id`, `api_version`) that gets forwarded to the app's handler come straight from HTTP headers, never included in the signed bytes: [3](#0-2) 

The equality the gem should be enforcing is:
`hmac_signed_bytes == (raw_body + shop + topic)` — i.e., the tenant/shop claim should be bound to the signature.
What it actually enforces is:
`hmac_signed_bytes == raw_body` while `shop` (used for tenant attribution) is taken from an out-of-band, unsigned header.

Because `OpenSSL::HMAC` only ever signs `raw_body`, the same `(raw_body, hmac)` pair remains valid under `HmacValidator.validate` no matter what `shop-domain`/`x-shopify-shop-domain` header value accompanies it (same `api_secret_key` is shared by the app across every shop that installs it). `Registry.process` then passes that attacker-controlled `shop` straight into the handler: [4](#0-3) 

### Impact Explanation
This breaks the tenant-isolation binding the HMAC is supposed to enforce: any correctly-signed body (e.g., one legitimately generated for the attacker's own shop, which any Shopify user can freely obtain by installing/testing the app on a dev store) can be replayed against the same endpoint with the `shop-domain` header rewritten to any victim shop. The webhook registry has no independent check that the header-derived `shop` actually corresponds to the shop the signature was generated for, so the handler executes tenant-scoped logic (e.g., data updates, uninstall/GDPR handling, order/customer processing) under a victim tenant's identity supplied by an untrusted header — a cross-tenant access vulnerability.

### Likelihood Explanation
Exploitation requires only possession of one legitimately-signed `(raw_body, hmac)` pair for the shared app secret (trivially obtainable by installing the app on any store or via Shopify's webhook test-delivery tooling) plus the ability to send an HTTP request to the app's public webhook endpoint with a forged `shop-domain` header — no access token, `client_secret`, or privileged account is needed.

### Recommendation
Bind the `shop` (and ideally `topic`) claim to the HMAC verification: derive shop identity either from a value included in the signed payload, or cross-validate the header-derived `shop` against a shop known to be currently registered/owning that webhook subscription (e.g., via `webhook_id` looked up against Shopify) before dispatching to the handler. At minimum, document and enforce that `Registry.process` must not attribute a webhook to a `shop` value that isn't itself covered by the signature.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; trigger any webhook topic so Shopify sends `{raw_body, x-shopify-hmac-sha256}` to the app's endpoint (or capture identical bytes via Shopify's Partner Dashboard "send test webhook" feature).
2. Resend the exact same `raw_body` and `hmac-sha256` value to the app's webhook endpoint, but replace the `x-shopify-shop-domain` header with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the shared secret (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb`).
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` and dispatched to the app's handler, which now executes shop-scoped logic under the victim's identity despite the payload never having been signed for that shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
