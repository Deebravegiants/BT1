Found the vulnerability: the webhook `shop` used to dispatch the handler is **not covered by the HMAC** signature.

### Title
Webhook `shop-domain` header is trusted for routing/dispatch without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read from unauthenticated HTTP headers. `Registry.process` validates the HMAC of the body but then passes the header-derived `shop` value straight into the app's webhook handler as trusted tenant identity, breaking the binding `bytes verified == bytes trusted for tenant identity`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`, `api_version`, `webhook_id`) are read directly from HTTP headers, which are never included in the HMAC computation: [2](#0-1) 

`Registry.process` validates only that the HMAC (computed over the body) is correct, then immediately trusts `request.shop` (a header value) as the tenant identifier passed to the app's `WebhookHandler`: [3](#0-2) 

Because Shopify signs `X-Shopify-Hmac-SHA256` over the raw body with the app's `client_secret`, an attacker who does not know the secret cannot forge an arbitrary body+signature pair. However, the identity binding the gem exposes to the host app is: *"HMAC verified over body" implies "shop header is authentic."* These are not the same equality — the equality that actually holds is `HMAC(body, secret) == received_hmac`, not `HMAC(body+shop, secret) == received_hmac`. The `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are parsed but never bound into the signed bytes, so this gem's `Request`/`Registry` API silently hands the host application a `shop` value that carries no cryptographic guarantee, despite being delivered alongside (and effectively "verified by") an HMAC check that gives the appearance of trustworthiness.

### Impact Explanation
If a host application relies on `WebhookMetadata#shop` returned by `Registry.process`/`WebhookHandler#handle` as the tenant key (a documented and expected usage pattern, since that's the only shop value the API surfaces from this call), and if any intermediary or misconfigured proxy/load balancer forwards attacker-controllable headers into this code path without shop-domain being independently pinned to the endpoint, cross-tenant data could be attributed to the wrong shop. This maps to "cross-tenant access" (Critical) if a host naively trusts the returned `shop` for tenant-scoped writes/lookups, because the only integrity check performed (`HmacValidator.validate(request)`) does not cover that field at all.

### Likelihood Explanation
Exploitability depends entirely on deployment/proxy behavior outside this gem's control (whether `shop-domain` header can be attacker-influenced on the path to the app), so this is a design/API weakness rather than a directly exploitable bug from an unprivileged internet user hitting the gem in isolation with a stock Shopify-to-app HTTPS webhook delivery — in that stock scenario the header is set by Shopify's edge and not attacker-reachable. This lowers likelihood significantly for the common deployment, but the root cause — an unauthenticated field silently exposed as if it were verified — matches the report's core "field acted on but not covered by the HMAC" class precisely.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the signable string alongside the raw body (or otherwise cryptographically verify them, e.g. against the `X-Shopify-Shop-Domain` used to establish the original session/registration), so `HmacValidator.validate` provides an integrity guarantee over every field the host application is expected to trust, not just the body.

### Proof of Concept
1. Construct a `ShopifyAPI::Webhooks::Request` with a legitimately-signed `raw_body` (HMAC valid for that body) but supply `headers` with an arbitrary/different `shop-domain` value (e.g. via a reverse proxy or header-injection point that forwards untrusted headers into the app).
2. Call `ShopifyAPI::Webhooks::Registry.process(request)`.
3. `Utils::HmacValidator.validate(request)` passes because it only checks `HMAC(raw_body)`, per [4](#0-3)  and [5](#0-4) .
4. The handler receives `WebhookMetadata` with the attacker-supplied `shop`, per [6](#0-5) , despite that value never having been part of the signed payload.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
