## Analysis

The identity-binding break here is in Shopify webhook verification: **the shop identity used to route/act on a webhook is not covered by the HMAC that authenticates the request.**

### Root cause

`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, but its `to_signable_string` only returns the raw JSON body — none of the HTTP headers (including the shop domain) are part of the signed payload: [1](#0-0) 

`HmacValidator.validate` computes the HMAC purely over `to_signable_string`, i.e. the raw body bytes, and compares it to the `hmac` extracted from the `shopify-hmac-sha256` header: [2](#0-1) 

`Registry.process` gates only on that HMAC check, then unconditionally trusts `request.shop` (sourced from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is *not* part of the signed bytes) and forwards it to the handler as the tenant identity: [3](#0-2) 

### Why this is exploitable by an unprivileged actor

The webhook signing secret is the app's `api_secret_key`, which is **shared across every shop that installs the app** — it is not shop-specific. Any merchant who installs the app is, by definition, an unprivileged internet user relative to other tenants of that same app, yet they can:

1. Trigger a webhook event in their own store (e.g. `orders/create`) and capture the resulting `(raw_body, hmac)` pair — a fully valid signature computed with the shared secret.
2. Replay that exact byte-identical body to the app's webhook endpoint, but forge the `shopify-shop-domain` header to name a *different* victim shop.
3. `HmacValidator.validate` still returns `true`, because the header is never part of `to_signable_string`.
4. `Registry.process` calls `handler.handle` with `WebhookMetadata.new(... shop: request.shop ...)` set to the attacker-chosen victim shop, so the host app's data model attributes the payload/action to the wrong tenant.

This breaks the binding: `shop authenticated-by-HMAC` (none — the shop is never signed) vs. `shop trusted for tenant lookup` (`request.shop`, taken from an unauthenticated header). This is exactly the "field acted on but not covered by the HMAC" analog to the Blend report's pattern of checking one thing but acting on another.

## Impact

Cross-tenant confusion: a webhook consumer built on this gem's `Webhooks::Registry.process` will process a validly-signed payload under an attacker-supplied `shop` value, letting one installed (unprivileged) merchant spoof events as belonging to a different shop that also uses the same app. This is a cross-tenant identity-binding failure rooted entirely in this gem's webhook verification API (`Request#shop`/`Request#to_signable_string`/`HmacValidator`/`Registry.process`), independent of how the host app implements its handler.

### Title
Webhook `shop` identity is not covered by HMAC signature, enabling cross-tenant spoofing — (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body, never the `shopify-shop-domain` header. `Registry.process` validates the HMAC over the body but then trusts the unauthenticated `shop` header value to identify the tenant for the handler.

### Finding Description
`Request#shop` reads `shopify-shop-domain`/`x-shopify-shop-domain` [4](#0-3) , while `to_signable_string` only returns `@raw_body` [5](#0-4) . `HmacValidator.validate` therefore authenticates the body only [6](#0-5) , and `Registry.process` uses that unauthenticated `shop` value directly in `WebhookMetadata` handed to the handler [7](#0-6) . Because the signing secret (`api_secret_key`) is shared by all shops of a given app, any installed merchant can produce a validly-signed body and relabel it as coming from a different shop.

### Impact Explanation
Cross-tenant identity confusion (High/Critical category per rules: "cross-tenant access") — the app's webhook handling layer cannot distinguish which shop a signed payload truly originated from, since shop identity is outside the authenticated envelope.

### Likelihood Explanation
Any merchant who installs an app built on this gem can trigger benign webhook events in their own store to obtain a genuinely-signed body/HMAC pair, then replay it with a modified shop header — no special privilege, secret, or credential is required beyond normal app installation.

### Recommendation
Include the shop domain (and other identity-relevant headers like `topic`/`webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind `request.shop` to the verified body (e.g., verify body against a per-shop expectation, or require callers to have already authenticated the shop via a trusted, tamper-evident channel) before `Registry.process` forwards it to handlers.

### Proof of Concept
1. Merchant A installs the app and triggers `orders/create` in their own store, capturing the resulting raw body `B` and header `shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Merchant A sends a POST to the app's webhook endpoint with body `B`, `shopify-hmac-sha256: H`, `shopify-topic: orders/create`, but `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `B` [8](#0-7) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from Merchant A's store.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
