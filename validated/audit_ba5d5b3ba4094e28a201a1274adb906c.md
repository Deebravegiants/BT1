### Title
Webhook shop-domain is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verification performed by `ShopifyAPI::Utils::HmacValidator.validate` (called from `ShopifyAPI::Webhooks::Registry.process`) authenticates the body bytes only. The `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers and are never part of the signed payload, yet `Registry.process` forwards `request.shop` straight into the handler as the trusted tenant identifier.

### Finding Description
The binding that should hold is:
`hmac_valid(request) == true` implies `request.shop == the shop that actually produced this raw_body`.

In practice the code only proves:
`hmac_valid(request) == true` implies `request.body was produced by someone possessing Context.api_secret_key`.

Relevant code: [1](#0-0) [2](#0-1) 

Shopify signs webhook HMACs with the app's `client_secret` (`Context.api_secret_key`), which is shared across every shop that has the app installed — it is not per-shop. Because `shop` (from the `X-Shopify-Shop-Domain` header) is excluded from `to_signable_string`, any account that can install the app on their own store (an ordinary, unprivileged merchant) can:
1. Trigger a real event on their own shop and capture Shopify's genuine webhook `(raw_body, hmac)` pair.
2. Replay that exact `raw_body` and `hmac` to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header (and optionally `topic`/`webhook-id`) with a victim shop's domain.
3. `HmacValidator.validate` recomputes the HMAC over `raw_body` only — unaffected by the header change — so `Registry.process` treats the forged request as authentic and dispatches it with `request.shop` equal to the attacker-chosen victim domain: [3](#0-2) 

Compare with `Auth::Oauth::AuthQuery`, where every field acted upon (`code`, `host`, `shop`, `state`, `timestamp`) is explicitly included in `to_signable_string` before HMAC verification: [4](#0-3) 
The webhook `Request` class does not follow this same pattern for the identity-bearing `shop` field, breaking the equality that host applications legitimately assume holds once `Registry.process`/`HmacValidator.validate` returns true.

### Impact Explanation
Host applications built on this gem rely on the library's own documented flow — construct `ShopifyAPI::Webhooks::Request` from headers/body and call `Registry.process` — to authenticate the webhook and receive a trustworthy `shop` value via `WebhookMetadata#shop`. Because `shop` is not covered by the signature, a malicious but otherwise legitimate app-installer can forge webhook deliveries that the library reports as valid for a shop they do not control. Depending on what the host app does with the (falsely-authenticated) `shop` value in `WebhookMetadata` (e.g., looking up that shop's stored access token to perform follow-up API actions, updating that shop's data, or triggering shop-scoped business logic), this results in cross-tenant access/action performed against a victim shop using data supplied by an unrelated attacker. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that has more than one shop installed (the normal case for a multi-tenant Shopify app): the attacker only needs their own live installation to obtain one genuinely-signed `(body, hmac)` pair (client_secret is shared across all shops for a given app), then can freely relabel the `shop-domain` header on replay since it is excluded from the signed content. No secrets, tokens, or privileged access are required beyond normal, unprivileged installation of the target app on the attacker's own store.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the value returned by `Request#to_signable_string`, or otherwise cryptographically bind them to the raw body before computing/verifying the HMAC (mirroring what `AuthQuery#to_signable_string` does for OAuth). At minimum, document and/or enforce in `Registry.process` that `request.shop` must be independently checked against the shop that installed the app for the given webhook/session context before being trusted downstream.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and on victim `victim-shop.myshopify.com`.
2. Attacker triggers a webhook event on their own shop, capturing headers and raw body Shopify sent, including the real `X-Shopify-Hmac-Sha256` value (computed with the shared `client_secret`).
3. Attacker POSTs the identical `raw_body` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and, if desired, forges `topic`/`webhook-id` too — also unauthenticated).
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request object; `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which validates HMAC over `raw_body` only — this still passes because the body/HMAC pair is genuine.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`, causing the host app to process attacker-controlled data as if it originated from the victim shop. [2](#0-1)

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
