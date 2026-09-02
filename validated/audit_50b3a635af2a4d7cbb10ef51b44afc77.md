Based on my analysis, this gem's webhook HMAC binds only the raw body, while the `shop`, `topic`, and `webhook_id` fields consumed downstream are read straight from unauthenticated HTTP headers.

### Title
Webhook `shop`/`topic`/`webhook_id` fields are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so `Utils::HmacValidator.validate` verifies solely that the body bytes are unmodified. The `shop`, `topic`, and `webhook_id` values that `Registry.process` hands to the host app's handler are read directly from HTTP headers that are never part of the signed content, breaking the binding: `hmac(raw_body) == valid` should imply `shop/topic/webhook_id == authentic`, but it does not.

### Finding Description
`Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string`. That method is implemented to return `@raw_body` alone: [1](#0-0) 
Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from headers with no cryptographic linkage to the signature: [2](#0-1) 
`Registry.process` then trusts these header-derived values wholesale when dispatching to the handler: [3](#0-2) 

Because only the body bytes are authenticated, an unprivileged attacker who legitimately receives one real webhook delivery for a shop they control (e.g., by installing the app on their own store, which requires no special credential or privilege) obtains a raw body + valid HMAC pair. They can then replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` header. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` forwards the attacker-chosen `shop`/`topic`/`webhook_id` to the handler as if authentic — a cross-tenant identity confusion (`request.shop` used by the host app to key data is not the shop that actually produced the signed bytes).

### Impact Explanation
This satisfies the "Critical - cross-tenant access" category: a host application that uses `WebhookMetadata.shop` to look up or mutate per-tenant data (a standard pattern recommended in this gem's own docs) can be made to apply a replayed, validly-signed payload to a different, victim tenant, or to misclassify the topic/webhook id used for idempotency/dedup, all without possessing the app's `client_secret` or any merchant token — only a self-service install and interception of one's own webhook traffic is required.

### Likelihood Explanation
Likelihood is High: webhook endpoints are public HTTP endpoints by design, `api_secret_key` is never needed by the attacker (they only need one legitimately signed body from their own shop), and the vulnerable code path (`HmacValidator.validate` computing over body-only, `Registry.process` trusting headers) is exercised on every default webhook flow using this gem.

### Recommendation
- Short term: Document that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are not authenticated by the HMAC and that host apps must independently verify `shop` against their own tenant/session store before acting on a webhook.
- Long term: Include `shop`, `topic`, and `webhook_id` (or a canonical representation of all Shopify-controlled headers) inside the signable string used by `HmacValidator`, or otherwise cryptographically bind them to the signature, so `Registry.process` can reject payloads whose header metadata was altered post-signing.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-service, no special privilege).
2. Attacker's own store triggers a webhook; attacker's server (or a proxy they control) captures the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B`), plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`.
3. Attacker resends the identical `B`/`H` to the same app endpoint but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Request.new` parses these headers unchanged; `HmacValidator.validate` recomputes HMAC over `B` only and succeeds (`lib/shopify_api/webhooks/request.rb:35-43`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's parsed body>, ...)` — the host app now processes attacker-controlled data under the victim shop's identity.

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
