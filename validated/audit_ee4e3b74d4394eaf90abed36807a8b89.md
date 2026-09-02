This confirms the vulnerability: the webhook HMAC signs only the raw body, while `shop`, `topic`, `api_version`, and `webhook_id` come from unauthenticated HTTP headers and are never covered by the signature.This confirms `WebhookMetadata` carries the unauthenticated `shop` field straight from the header into the handler, so the app's business logic (tenant attribution, data storage keyed by shop, mandatory redact webhooks, etc.) trusts a value that the HMAC never covers.### Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by the HMAC signature, allowing cross-tenant webhook forgery via replay - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body via `Utils::HmacValidator.validate(request)` [1](#0-0) . The `Request#to_signable_string` method, which supplies the bytes that are actually HMAC-verified, returns only `@raw_body` [2](#0-1) . Meanwhile `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are read directly from unauthenticated HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) and are never part of the signed bytes [3](#0-2) . These unverified fields are then passed straight into the handler via `WebhookMetadata`, which the host application uses to attribute the webhook to a tenant [4](#0-3) [5](#0-4) .

This is structurally the same bug class as the H-1 report: a downstream operation (there, `_addKeysAndLoansInfo()`; here, `handler.handle()`) uses an identifier (`borrowingKey` there, `shop`/`webhook_id` here) that was not the one actually bound/verified by the authoritative check (the new borrowing key there; the HMAC signature here) — breaking the intended identity binding `verified_bytes == acted_on_bytes`.

### Finding Description
`HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac` [6](#0-5) . For webhooks, `to_signable_string` is exactly `@raw_body`, i.e. the JSON payload bytes — nothing else [2](#0-1) . This means Shopify's HMAC only proves "this body was signed with the app's secret"; it says nothing about which shop, topic, or webhook-id it was intended for. The binding that should hold is:

`HMAC_verified(body) ⇒ (shop, topic, webhook_id) as delivered are authentic`

but the actual binding is only:

`HMAC_verified(body)` — with `(shop, topic, webhook_id)` supplied unauthenticated from headers.

Because `Request#shop`/`#topic`/`#webhook_id` come from `shopify_header(...)` reading straight off attacker-controllable HTTP headers [7](#0-6) , and `Registry.process` never cross-checks these against anything derived from the signed body, any entity that has ever observed one legitimately-signed webhook body (e.g., their own store's webhook, which is delivered to the app's public endpoint and thus observable by that same unprivileged merchant/tenant) can replay that exact body while substituting a different `shopify-shop-domain` (and/or `shopify-webhook-id`) header. The HMAC still validates because it only checks the body, and `Registry.process` will dispatch the handler with the attacker-chosen `shop` value.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce for webhook delivery: an app relying on `WebhookMetadata#shop` to select which merchant's data to update (a very common integration pattern, since this is the only per-request tenant identifier the gem exposes to `WebhookHandler#handle`) can be made to apply another shop's webhook payload under an attacker-chosen shop identity. For high-value topics such as the mandatory `shop/redact`, `customers/redact`, or `customers/data_request` webhooks, or any topic whose handler writes to a shop-scoped store keyed by `data.shop`, this enables cross-tenant data corruption/deletion or a redaction request being forged against a shop that never requested it — a cross-tenant integrity issue rooted in the gem's own signature-verification API. Per the rules, this maps to **High** (an authentication/binding boundary — the value trusted to key per-tenant operations — is not covered by the credential-backed check that is supposed to authenticate it).

### Likelihood Explanation
Likelihood is bounded by the requirement that the attacker must first obtain one validly-signed raw body (e.g. by being a merchant who installs the app and receives their own genuine webhook, which is delivered over plain HTTP to the app's public webhook endpoint and is not tied to a nonce or shop-bound claim inside the signed bytes). This is realistic for any multi-tenant app, since every installing merchant automatically becomes a source of one or more validly-signed bodies. No possession of `api_secret_key` or any credential belonging to the target tenant is required — only re-sending previously-observed bytes with a substituted header, which is well within an "unprivileged internet user" capability once they are a customer/installer of the same app.

### Recommendation
Bind the fields the application relies on into the signed payload verification, or otherwise refuse to trust header-only fields for identity decisions:
- Include `shop`, `topic`, and `webhook_id` in the signable string used by `HmacValidator` for webhook requests (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`, `host`, `state`, etc. into its own HMAC check) [8](#0-7) , or
- Document/enforce that `WebhookMetadata#shop` must never be used as the sole tenant key without an independent binding (e.g., requiring the app to confirm the shop against a previously-registered webhook_id/shop pair before trusting `data.shop`), and add idempotency/replay protection keyed by `webhook_id` scoped per verified body.

### Proof of Concept
1. App registers a webhook handler for topic `orders/create` that persists `data.body` under `Shop.find(data.shop)`.
2. Merchant A (attacker, an "unprivileged" tenant of the multi-tenant app) installs the app; Shopify delivers a legitimately HMAC-signed webhook to the app's public endpoint with body `B` and headers `shopify-shop-domain: shop-a.myshopify.com`, `shopify-hmac-sha256: H` where `H = HMAC(secret, B)`.
3. Attacker captures `B` and `H` (they own this delivery — no secret needed).
4. Attacker replays a POST to the same public webhook endpoint with the same body `B`, the same `shopify-hmac-sha256: H` header, but `shopify-shop-domain: shop-b.myshopify.com` (target victim shop).
5. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches `H` — validation passes, because `shop` was never part of `to_signable_string` [9](#0-8) [2](#0-1) .
6. `handler.handle(data: WebhookMetadata.new(..., shop: "shop-b.myshopify.com", ...))` is invoked, and the app applies attacker-controlled body content under victim shop `shop-b`'s tenant scope [5](#0-4) .

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
