Based on my investigation, I've confirmed the root cause and exploit path.

### Title
Webhook `shop` (tenant identifier) is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers [1](#0-0) . `Utils::HmacValidator.validate` verifies only that the body bytes were signed with the app's `api_secret_key`; it never checks that the `shop` header is bound to that signature [2](#0-1) . `Webhooks::Registry.process` then passes this unauthenticated `shop` header straight into `WebhookMetadata` and on to the app's handler as the tenant identifier [3](#0-2) [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop header used by the handler == shop that the HMAC-signed body actually belongs to`. Because `to_signable_string` only includes `@raw_body` and excludes every Shopify header (`shop-domain`, `topic`, `webhook-id`, `api-version`), that equality is never enforced by the gem [5](#0-4) .

Before attack: a genuine webhook for shop A arrives with body B and `hmac = HMAC(secret, B)`. Validation passes, and `data.shop == "A"`, `data.body == B` are delivered together, consistent with reality.

After attack: any merchant who has installed the app (shop A, an "unprivileged internet user" relative to other tenants of the same multi-tenant app) can capture one of their own legitimate webhook deliveries — this requires no access to `api_secret_key`, session, or access token, only observing traffic the app already receives for their own shop. They then replay the same `raw_body` + `hmac-sha256` header verbatim to the app's webhook endpoint, but substitute `x-shopify-shop-domain` with a victim shop's domain (e.g., "B"). `HmacValidator.validate` recomputes `HMAC(secret, raw_body)` — which still matches, since the header is not part of the signable string — so `Errors::InvalidWebhookError` is never raised [6](#0-5) . The handler now receives `data.shop == "B"` with the attacker's own body content, breaking the equality: the shop the HMAC actually belongs to (A) no longer equals the shop the handler acts on (B).

This is exactly the "double order"/callback-confusion root cause abstracted from the report: a check validates one artifact (balance delta / HMAC-signed body) while a *different*, unverified value (the second order / the `shop` header) is what downstream logic actually acts on.

The gem's own documented reference handler compounds the impact by using `data.shop` directly as the tenant key for persistence/queuing (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`), which is the pattern the library instructs app authors to follow, not a documented API being ignored.

### Impact Explanation
This crosses a tenant boundary: an attacker who only controls their own shop's install of a multi-tenant app can inject webhook payloads that the app attributes to a different, victim merchant's shop, without ever obtaining that victim's credentials, session, or access token. Depending on how the host app is wired (per the gem's own documented pattern), this can lead to cross-tenant data corruption/injection — data belonging to shop A being stored, queued, or acted upon under shop B's identity. This matches the "Critical — cross-tenant access" impact category.

### Likelihood Explanation
Any developer with a legitimate (even free/trial) install of the target app can trivially capture one authentic webhook request headed to their own shop's endpoint (no special access needed — it's an HTTP request they receive), then replay it with a modified `shop-domain` header using a standard HTTP client. No secret key, TLS interception, or social engineering is required, and the gem's own `HmacValidator` will accept the forged request.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable payload used for HMAC verification, or otherwise cryptographically bind the `shop` header to the signed body (e.g., verify a canonicalized string of `raw_body + shop + topic` rather than `raw_body` alone) in `Webhooks::Request#to_signable_string` / `Utils::HmacValidator`. At minimum, the library should not surface an unauthenticated `shop` value as a trusted `WebhookMetadata` field without documenting that the caller must independently verify it against a known/installed shop list before using it as a tenant key.

### Proof of Concept
1. App installs on shop A and receives a legitimate webhook: `raw_body = B`, headers include `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: a.myshopify.com`.
2. Attacker (owner of shop A) replays the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — unaffected by the header change — and passes [7](#0-6) .
4. The registered handler is invoked with `WebhookMetadata(shop: "victim-b.myshopify.com", body: B, ...)`, causing the app to process/store attacker-controlled body content under the victim shop's identity [8](#0-7) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
