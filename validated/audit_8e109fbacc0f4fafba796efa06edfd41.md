Confirmed: for OAuth callbacks, `AuthQuery#to_signable_string` (`lib/shopify_api/auth/oauth/auth_query.rb:34-43`) includes `shop` inside the HMAC-signed payload, so `shop` is cryptographically bound there. But for webhooks, `Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers (`shopify_header`, lines 15-33) that are **not** covered by the HMAC computation at all.

`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates only `Utils::HmacValidator.validate(request)` (which validates `hmac(raw_body)`), then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata` passed to the handler — with no cross-check that the `shop-domain` header actually matches the tenant whose secret validated the body.### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header not covered by HMAC allows cross-tenant spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts the `shop`, `topic`, and `webhook_id` values taken from unauthenticated HTTP headers when dispatching to the registered handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed by an entity holding `Context.api_secret_key` [2](#0-1) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to that signature [3](#0-2) .

`Registry.process` then does:
```
raise ... unless Utils::HmacValidator.validate(request)
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [4](#0-3) 

The intended binding is: `hmac_valid(raw_body)` should imply the tuple `(shop, topic, webhook_id)` reported to the handler is authentic *for that exact body*. In this implementation that equality does not hold — only `hmac_valid(raw_body) == true` is enforced, while `(shop, topic, webhook_id)` are arbitrary attacker-controlled header values that travel to the handler unchecked.

Contrast this with the OAuth callback path, where `AuthQuery#to_signable_string` explicitly includes `shop` inside the signed payload [5](#0-4) , correctly binding shop to the HMAC. The webhook path lacks this equivalent binding for `shop`.

### Impact Explanation
An attacker who is themselves a legitimate installed merchant (any unprivileged Shopify store owner) can capture a genuine `(raw_body, hmac)` pair sent to the app's webhook endpoint for their own shop, then replay that exact body+hmac pair while substituting an arbitrary `shopify-shop-domain` header value. Since `shop` is not part of the signed bytes, the HMAC check still passes, and the handler receives `WebhookMetadata` claiming the payload originated from a different, victim tenant. Any app logic that uses `data.shop` to select which tenant's session/store/data to update (e.g., writing order/customer data keyed by `shop`) can be tricked into cross-tenant data injection — an attacker-controlled payload being attributed to and acted upon for a shop they do not own. This matches the "cross-tenant access" class of Critical impact in the rules.

### Likelihood Explanation
Requires only an unprivileged internet-accessible actor that has legitimate access to at least one valid webhook signature for their own tenant (any merchant who installs the app receives real webhooks with valid HMACs signed with the app's shared `api_secret_key`, which is the same secret for all tenants of that app). No leaked credentials, no TLS interception, and no access to the app's `client_secret` are required — only observing one's own webhook traffic and re-posting it with a modified header to the app's public webhook endpoint. This is entirely reachable through the gem's documented `Registry.process` API and does not require the host app to violate any documented usage.

### Recommendation
- **Short term:** Have the app additionally verify that `request.shop` matches an expected/installed shop domain (e.g., via `Utils::ShopValidator.sanitize!`) and cross-check it against the tenant context before acting on webhook data; document this requirement prominently.
- **Long term:** Extend `Webhooks::Request#to_signable_string` (or add a secondary check) so the HMAC/signature scheme binds `shop`, `topic`, and `webhook_id` to the payload, or otherwise cryptographically tie header-derived tenant identity to the verified body, matching the pattern already used for `AuthQuery`.

### Proof of Concept
1. App has two merchants installed: `victim.myshopify.com` and `attacker.myshopify.com`, sharing the same app `api_secret_key`.
2. Attacker's own store legitimately triggers a webhook; attacker captures the raw POST: `raw_body` and the resulting `x-shopify-hmac-sha256` value, plus other headers.
3. Attacker resends this exact `raw_body`/`hmac` pair to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally different `x-shopify-topic`/`x-shopify-webhook-id` values consistent with what they want to spoof).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates HMAC over `raw_body` only [1](#0-0)  — validation succeeds because the body/hmac pair is genuinely valid (just for a different shop).
5. `handler.handle` is invoked with `WebhookMetadata` reporting `shop: "victim.myshopify.com"` [6](#0-5) , and the app processes attacker-supplied payload data as if it belongs to the victim tenant.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L34-43)
```ruby
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
