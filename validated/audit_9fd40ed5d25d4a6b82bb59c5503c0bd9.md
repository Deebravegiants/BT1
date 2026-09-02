### Title
Webhook `shop`/`topic` fields are not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body [1](#0-0) . However, the `shop`, `topic`, `webhook_id` and `api_version` values that the handler actually acts on are taken from HTTP headers that are never included in the signed material [2](#0-1) . Because the signing key (`api_secret_key`) is a single app-level secret shared by every shop that installs the app (not a per-shop secret), any user who installs the app on their own shop can obtain a genuinely-signed webhook body/HMAC pair, then replay that exact body+signature while substituting the `X-Shopify-Shop-Domain` (and/or topic) header for a victim shop. `Utils::HmacValidator.validate` only checks the body against the secret and has no way to detect the header substitution, so the forged request passes verification and is dispatched to the handler tagged with the attacker-chosen shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 
while `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are parsed straight from headers that are excluded from that signable string: [4](#0-3) 

`Registry.process` verifies only the HMAC over the body, then immediately trusts `request.shop` and `request.topic` to route and tag the payload for the handler: [5](#0-4) 

The identity binding broken is: `HMAC-verified(bytes) == raw_body` but the code treats it as `HMAC-verified(bytes) == (shop, topic, raw_body)`. Since `api_secret_key` is one value per app (shared across every shop that installs it, per `HmacValidator.validate` using `Context.api_secret_key`/`Context.old_api_secret_key` globally, not per-shop) [6](#0-5) , any unprivileged user who installs the target app on their own store can obtain a legitimately-signed `(body, hmac)` pair for their own shop, then POST that same body to the app's webhook endpoint with the `shop-domain` header changed to a different, victim shop. The gem's verification passes because it never checks that the claimed shop is bound to the signed bytes.

### Impact Explanation
This breaks the tenant isolation the HMAC is meant to provide: an attacker with only a normal, self-service app installation (no special privileges, no access to `api_secret_key`) can make the host application process attacker-controlled webhook data (body, topic) under a victim shop's identity. Depending on how the host application's webhook handler uses `WebhookMetadata#shop` (e.g., to look up/update per-shop data, deprovision resources, or trigger shop-scoped side effects), this enables cross-tenant data manipulation — matching the Critical "cross-tenant access" bar.

### Likelihood Explanation
Any user can trigger this by installing the target app on a shop they control (a normal, unprivileged action for public apps), capturing one legitimately delivered webhook, and replaying its body with a spoofed `shop-domain`/`topic` header. No secrets, credentials, or elevated access are required beyond what a standard app install already grants.

### Recommendation
Bind the header-derived identity fields (`shop`, `topic`, and ideally `webhook_id`/`api_version`) into the signed material verified by `HmacValidator`, or have `Registry.process` independently verify that `request.shop` matches an expected/allow-listed shop (e.g., a shop with an active session) before dispatching, rather than trusting an unauthenticated header alongside a body-only HMAC.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop (`attacker.myshopify.com`), triggering a real webhook, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because it's signed with the shared `api_secret_key`).
2. Capture `B` and `H` (e.g., attacker's own server logs, since it's delivered to their own configured endpoint).
3. Replay a POST to the app's webhook endpoint with body `B`, `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Topic: orders/create`, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses shop as `victim.myshopify.com`; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `B` and succeeds, since `H` was computed the same way [7](#0-6) .
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-controlled body, even though Shopify never sent this webhook for `victim.myshopify.com`.

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
