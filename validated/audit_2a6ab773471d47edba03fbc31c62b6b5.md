This confirms the finding. In OAuth's `AuthQuery`, the `shop` field is explicitly included in `to_signable_string` (`lib/shopify_api/auth/oauth/auth_query.rb:34-43`), so HMAC binds shop to the signed payload there.

But in `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read directly from an unauthenticated HTTP header (`shopify-shop-domain`) [2](#0-1) . `Registry.process` validates only the HMAC over the raw body and then passes `request.shop` straight into `WebhookMetadata`, which is handed to the app's handler as the tenant identifier [3](#0-2) .

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body bytes, never the `shopify-shop-domain` (or legacy `x-shopify-shop-domain`) header. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` as the tenant identity after validating only that body-only HMAC.

### Finding Description
The HMAC validation performed by `Utils::HmacValidator.validate` for webhooks checks `computed_signature == received_signature` where `computed_signature` is derived exclusively from `verifiable_query.to_signable_string`, and for `Webhooks::Request` that string is just `@raw_body` [1](#0-0) [4](#0-3) . The `shop` accessor used downstream comes from a raw header value that is never part of the signed material [2](#0-1) .

Because all shops installed on a given app share the same `client_secret`/`api_secret_key` (this is an app-level, not per-shop, secret — see `Context.api_secret_key` usage in `HmacValidator.validate`), any merchant who has installed the app on their own store can obtain validly-signed `(raw_body, hmac)` pairs for webhooks triggered on their own shop. Since the shop identity is never part of what's signed, that attacker can replay the exact same body+HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Registry.process` only checks `Utils::HmacValidator.validate(request)` (body-only) and then forwards `request.shop` unchanged into `WebhookMetadata` for the app's handler [3](#0-2) .

This breaks the intended binding: `shop header trusted by the app == shop that actually produced/owns the signed payload`. Instead the equality that actually holds is only `HMAC(secret, raw_body) == received_hmac`, with `shop` unconstrained. This is directly analogous to the reported bug class of "a field acted on but not covered by the HMAC."

Contrast with `Auth::Oauth::AuthQuery`, where `shop` is explicitly included in the signed string [5](#0-4) , showing the library's own OAuth code already recognizes `shop` must be part of the signable material — but the webhook path does not apply the same protection.

### Impact Explanation
Any application built on this gem that keys per-tenant state (sessions, database records, deduplication, authorization decisions) off `WebhookMetadata#shop`/`request.shop` without independent verification is exposed to cross-tenant data poisoning: a low-privilege attacker who is merely a legitimate merchant of the app on their own store can forge webhook deliveries that the app believes originated from a different (victim) shop. Depending on how the host app trusts webhook `shop` values (e.g., updating billing/subscription state, order/inventory data, GDPR redact handling, or session-linked records), this can lead to cross-tenant data corruption or state confusion for another merchant's shop — a cross-tenant boundary violation.

### Likelihood Explanation
Exploitation requires the attacker to control their own real, installed shop instance of the app (unprivileged relative to other tenants) — they don't need any of the excluded privileged inputs (`api_secret_key`, access tokens, TLS interception, etc.). They only need to trigger a webhook-eligible action on their own store, capture the resulting `(raw_body, hmac)`, and re-POST it to the app's public webhook endpoint with a modified `shop` header. This requires no MITM and no secret material beyond what a normal merchant install already exposes to them.

### Recommendation
Bind the shop identity into the signed material for webhooks, or independently verify `request.shop` against a shop that is expected/known to the app (e.g., cross-check against the shop tied to the webhook subscription id via a GraphQL lookup, or maintain a registry of installed shop domains) before trusting it in `WebhookMetadata`. At minimum, document prominently that `request.shop` is not verified by the HMAC and must not be used as the sole tenant-resolution key without additional validation.

### Proof of Concept
1. App developer installs the app on Shop A (attacker-controlled) and Shop B (victim), both served by the same app instance sharing one `api_secret_key`.
2. Attacker triggers a webhook-eligible event on Shop A (e.g., `orders/create`), causing Shopify to POST a legitimately HMAC-signed body to the app's webhook endpoint with header `x-shopify-shop-domain: shop-a.myshopify.com`.
3. Attacker captures this raw body and HMAC value (e.g., via a proxy on requests reaching their own server/webhook path, which they legitimately control as the shop owner).
4. Attacker re-sends an HTTP POST to the same webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds (body+secret match) at `lib/shopify_api/webhooks/registry.rb:190`, and the handler executes with `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)` at `lib/shopify_api/webhooks/registry.rb:198-199`, despite the payload actually originating from Shop A.

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
