Confirmed: found a concrete, in-scope identity-binding gap in the webhook request handling.

### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are trusted from unauthenticated headers while only the raw body is covered by the HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes a webhook purely by validating the HMAC over the request body, then dispatches to a handler using `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which are covered by that HMAC.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with `to_signable_string` returning only `@raw_body`: [1](#0-0) 
Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, `shopify-webhook-id`) via `shopify_header`, with no cryptographic binding to those header values: [2](#0-1) 
`Registry.process` validates only the HMAC (over the body) and then immediately trusts `request.topic` and `request.shop` to route the payload to the app's handler: [3](#0-2) 
The binding this breaks, stated as an equality that should hold but doesn't:
`shop_used_for_handler_dispatch == shop_bound_by_hmac`
Before the request: attacker (any unprivileged internet user who can reach the app's webhook endpoint, since the endpoint has no other authentication) crafts a POST with a legitimate/replayed body+HMAC pair (e.g., captured from their own shop's webhook, or any webhook they can trigger against their own store) but substitutes the `shopify-shop-domain` and/or `shopify-topic` headers for a different value. After the request: `Utils::HmacValidator.validate(request)` still returns true (it only recomputes over `@raw_body`), but `handler.handle` is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` carrying the attacker-controlled header values — i.e. the "verified" bytes (body) and the "acted-on" identity fields (shop/topic) are disjoint.

### Impact Explanation
Any app whose webhook handlers use `data.shop` or `data.topic` (from `WebhookMetadata`) to decide behavior — e.g., looking up per-shop session/access tokens, gating mandatory GDPR topics (`shop/redact`, `customers/redact`, `customers/data_request`), or branching logic per topic — can be tricked into acting on a shop or topic that was never actually associated with the HMAC-signed payload. This crosses the tenant boundary the HMAC is supposed to enforce: an attacker who has (or can obtain) any valid body/HMAC pair from Shopify (including from their own store's legitimate webhook deliveries) can relabel it as belonging to a different shop or a different topic when it reaches the app's handler, producing cross-tenant data processing/exposure. This satisfies the High-severity "scope or expiry check bypass"/credential-tenant boundary criteria in scope.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker needs a valid `(raw_body, hmac)` pair, which they can obtain from any webhook delivered to a shop they control (Shopify signs webhooks per-app with the app's `client_secret`, not per-shop, so a body/HMAC pair valid for the attacker's own shop remains HMAC-valid regardless of which headers are attached). No access token, `api_secret_key`, or privileged account is required — only the ability to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers, which any unprivileged internet user can do.

### Recommendation
Include the identity-bearing fields in the signed payload validation path, or otherwise cryptographically bind `shop`, `topic`, and `webhook_id` to the HMAC before they are trusted. At minimum, `Registry.process` (or the host app via documentation) should be required to independently verify that `request.shop` corresponds to a shop that actually has this app installed (e.g., cross-check against a known session/shop record) rather than trusting the header value implicitly once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g., `orders/create`) to the app's endpoint, capturing the raw body `B` and header `shopify-hmac-sha256: H` (valid because Shopify computed `H = HMAC-SHA256(client_secret, B)`).
2. Attacker resends a POST to the app's webhook endpoint with the same body `B` and the same `H`, but sets `shopify-shop-domain: victim-shop.myshopify.com` and/or `shopify-topic: shop/redact`.
3. In `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})`, `to_signable_string` returns `B` only [1](#0-0) , so `Utils::HmacValidator.validate(request)` succeeds since it recomputes HMAC over `B` with the same secret [4](#0-3) .
4. `Registry.process` passes the check and calls `handler.handle` with `shop: request.shop` == `"victim-shop.myshopify.com"` (attacker-supplied header, never verified) [5](#0-4) , causing the app's handler logic to run as though the payload legitimately originated from and pertains to the victim shop.

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
