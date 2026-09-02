Confirmed: `AuthQuery.to_signable_string` at `lib/shopify_api/auth/oauth/auth_query.rb:34-43` includes `shop` in the signed payload for OAuth callbacks, but `Webhooks::Request.to_signable_string` at `lib/shopify_api/webhooks/request.rb:36-38` returns only `@raw_body`, excluding the `shop`, `topic`, and `webhook_id` header values entirely from the HMAC computation.

### Title
Webhook shop-domain identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string as only the raw request body [1](#0-0) , while the `shop`, `topic`, and `webhook_id` values are read directly from unauthenticated HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks that the computed HMAC of `to_signable_string` (the body) matches the received HMAC, using the app's shared `api_secret_key` [3](#0-2) . This breaks the identity binding `shop header == shop covered by hmac`, since the header is never part of the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)` [4](#0-3) , then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` — all sourced from `shopify_header(...)` — to build the `WebhookMetadata` passed to the app's handler. Because `to_signable_string` for `Webhooks::Request` is just `@raw_body` [1](#0-0) , any request bearing a body+HMAC pair that is valid for the app's global `api_secret_key` will pass validation regardless of what `shop-domain`, `topic`, or `webhook-id` headers accompany it. Contrast this with `Auth::Oauth::AuthQuery`, where `shop` is explicitly folded into `to_signable_string` and therefore bound by the HMAC [5](#0-4) . The webhook path lacks this equivalent binding.

Since `api_secret_key` is shared across all shops that install the same app (it is not shop-specific), any unprivileged internet user who installs the app on their own store — a normal, unprivileged action — will receive genuine webhook deliveries with a valid HMAC computed over a body they fully control the shape of. That attacker can then replay the exact same `raw_body`/HMAC pair directly to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to name a victim shop. `HmacValidator.validate` still succeeds because it never inspects those headers, and the handler receives a `WebhookMetadata` claiming the victim shop's identity while carrying attacker-controlled body content.

### Impact Explanation
If the host application's webhook handler uses `data.shop` to look up that shop's stored session/access token and perform actions or persist data scoped to "the shop the webhook is for" (the documented and expected usage pattern per `docs/usage/webhooks.md`), an attacker can inject data attributed to, or trigger app-side actions scoped to, a victim tenant they do not control — a cross-tenant access issue reachable without needing the victim's credentials, TLS interception, or privileged access, since the "attacker" only needs to be another unprivileged merchant who installed the same app.

### Likelihood Explanation
Medium-to-High: no special credentials are required beyond installing the app on an attacker-controlled store (a normal, low-friction unprivileged action for any public/OAuth-installable app), then sending a direct HTTP POST to the app's public webhook endpoint with a substituted header — no interaction with Shopify's real delivery pipeline is required since the endpoint is a plain public HTTP handler validating only body+HMAC.

### Recommendation
Bind the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) into the HMAC-signable representation for webhooks, analogous to how `AuthQuery#to_signable_string` binds `shop` for OAuth callbacks, so a valid signature for one shop/topic cannot be replayed under a different shop or topic header. At minimum, document and/or enforce that `data.shop` must never be trusted for tenant-scoping decisions without corroboration against the shop that installed the app and is expected to receive that specific webhook topic/subscription.

### Proof of Concept
1. Attacker installs the target app on their own development/test store (`attacker.myshopify.com`), completing OAuth normally — no privileged access required.
2. The app subscribes to a webhook topic (e.g. `orders/create`) for `attacker.myshopify.com`; Shopify delivers a webhook to the app with a body `B` and header `x-shopify-hmac-sha256` computed as `HMAC-SHA256(api_secret_key, B)` — the attacker can capture `B` and the HMAC value from their own store's traffic (e.g. via a webhook proxy tool they run themselves).
3. Attacker crafts a direct HTTP POST to the app's public webhook endpoint using the exact same `raw_body = B` and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `Webhooks::Request#to_signable_string` returns only `@raw_body`, ignoring the substituted `shop-domain` header: [1](#0-0) .
5. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: attacker_controlled, ...)` [6](#0-5)  and performs shop-scoped processing using the victim's identity but the attacker's payload.

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
