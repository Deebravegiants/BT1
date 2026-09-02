### Title
Webhook Shop/Topic Identity Spoofing via Header Forgery — HMAC Only Covers Body, Not Headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP *headers* of an incoming webhook request, but the HMAC signature verified by `Utils::HmacValidator.validate` only covers the raw request *body*. This breaks the identity binding: "bytes cryptographically verified" (the body) ≠ "bytes actually used to identify the tenant/topic" (the headers). An attacker who can obtain one validly-signed webhook body/HMAC pair for any shop can replay it to the app's public webhook endpoint with arbitrary `shop-domain`/`topic`/`webhook_id` headers, and the library will accept it as authentic and hand the forged shop/topic to the app's handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

None of `topic`, `shop`, `api_version`, or `webhook_id` — all read straight from HTTP headers — are part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC (which only attests to the body bytes) and then immediately trusts the header-derived `shop`/`topic`/`webhook_id`/`api_version` to build the `WebhookMetadata` passed to the app's handler, without any additional binding check tying those header values to the signed payload: [3](#0-2) 

Contrast this with the OAuth callback flow, where `shop`, `host`, `state`, `code`, and `timestamp` are all included in `AuthQuery#to_signable_string` and therefore covered by the HMAC: [4](#0-3) 

For webhooks, no such coverage exists for the identity-bearing headers, so `HmacValidator.validate(request)` returning `true` only proves "the body bytes were signed with `api_secret_key`" — it proves nothing about which shop or topic that body is attributed to. Because the app's client secret is shared across every shop that installs the app, any shop that installed the app (or that can obtain one signed body/HMAC pair through legitimate delivery-log/debugging tooling) can produce a byte sequence that keeps a valid signature under a completely different `shop-domain`/`topic` header, letting them impersonate another tenant's webhook to the app.

### Impact Explanation
This crosses the tenant boundary that the report's analog rules explicitly call out ("bytes verified versus bytes parsed"): the app's downstream logic (which typically looks up sessions/records keyed by `data.shop` from `WebhookMetadata`) can be made to act on behalf of, or attribute data to, a shop the attacker does not control — a cross-tenant forgery. This qualifies as Critical (cross-tenant access) under the stated impact categories, since the library itself hands unauthenticated header data to the handler as if it were verified.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one legitimately signed body+HMAC pair (e.g., from their own shop's webhook deliveries, which Shopify exposes to merchants/developers via delivery logs/test-notification tooling), then POST it directly to the app's known/public webhook endpoint with modified `shop-domain`/`topic` headers. This does not require the `api_secret_key`, an access token, or any privileged access — only that the attacker has (or can trigger) one valid webhook for a shop where the app is installed, which is achievable by any unprivileged user who installs the public app on their own store.

### Recommendation
Bind the identity-bearing headers into the HMAC-covered signable content (or otherwise cryptographically bind `shop`, `topic`, and `webhook_id` to the verified body) before trusting them in `Registry.process`, e.g., by including them in `to_signable_string`, or by re-validating them against Shopify out-of-band (e.g., confirming the `webhook_id` via the Admin API for the claimed shop) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, triggering a legitimate webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because it was signed with the shared `api_secret_key`), which the attacker can retrieve via Shopify's webhook delivery/test-notification tooling.
2. Attacker sends `POST /webhooks` to the app's endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or a different `X-Shopify-Topic`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` (see [1](#0-0) ).
4. `Registry.process` dispatches to the handler with `shop: "victim-shop.myshopify.com"` (attacker-controlled) and the attacker-chosen topic (see [5](#0-4) ), causing the app to process a forged event as if it legitimately originated from the victim shop.

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
