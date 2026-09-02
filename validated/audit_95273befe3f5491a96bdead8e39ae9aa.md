### Title
Webhook shop/topic identity spoofing via HMAC scope mismatch — HMAC covers only the raw body, not the `X-Shopify-Shop-Domain` header (`Registry.process` / `Webhooks::Request` bypass) - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but binds the HMAC only to `@raw_body`, while the shop identity, topic, api-version and webhook-id are all taken from unauthenticated HTTP headers that are never included in the signed bytes.

### Finding Description
`Registry.process` accepts a `Request` and only checks: [1](#0-0) 

The HMAC check itself is delegated to `Utils::HmacValidator.validate`, which computes the signature purely over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — it does not include `shop`, `topic`, `api_version`, or `webhook_id`: [3](#0-2) 

Compare this with `Auth::Oauth::AuthQuery`, which is the same `VerifiableQuery` interface but correctly folds `shop` (and other identity-bearing fields) into the signed string, so a shop substitution there would break the signature: [4](#0-3) 

For webhooks, `shop` is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header with no cryptographic binding to the body it accompanies: [5](#0-4) 

This breaks the equality that the design implicitly assumes: `hmac(raw_body, api_secret_key) == hmac_header` should imply `shop_header == shop_that_actually_produced(raw_body)`. In reality, the HMAC only proves "this body was signed by our api_secret_key at some point for some webhook"; it says nothing about which shop, topic, or webhook-id it belongs to. Any two headers can be freely substituted onto a validly-signed body without invalidating the signature check in `HmacValidator.validate`.

`Registry.process` then forwards the attacker-controlled `shop` (and `topic`/`api_version`/`webhook_id`) straight to the host app's handler as trusted metadata: [6](#0-5) 

### Impact Explanation
An unauthenticated party who is able to obtain one valid `(raw_body, hmac)` pair for any topic sent by the app's own Shopify HMAC key (e.g. from a webhook the attacker's own store legitimately received, from logs, or a replayed request) can resubmit it to the app's public webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header. Because `to_signable_string` never includes the shop, the HMAC still validates, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event came from a different (victim) shop with attacker-controlled `topic`/`webhook_id`/`api_version` values. Any host-app handler logic that keys off `data.shop` to load a merchant session, write to per-shop storage, or make trust decisions is exposed to cross-tenant data confusion — matching the "cross-tenant access" / identity-binding-break class called out in the rules, analogous to the Rocket.Chat report's core lesson that a value used for a security decision (there: destination host; here: shop identity) must be bound to what was actually verified (there: the resolved IP at fetch time; here: the bytes that were HMAC'd).

### Likelihood Explanation
Exploitation only requires possession of a single genuine `(body, hmac)` pair signed with the app's `api_secret_key` for the target app — which an attacker can obtain trivially by running their own trial/dev store, installing the app, and letting Shopify send it any webhook. No access token, `api_secret_key`, or privileged account is needed; the attacker only replays already-observed public-looking header/body content with a substituted shop header. It does not require TLS interception, DNS control, or any host-application misconfiguration — it works purely because the gem's own `to_signable_string` omits the identity headers from the signed scope.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the signable string for `Webhooks::Request`, or otherwise cryptographically bind the header values to the body before trusting them, mirroring what `Auth::Oauth::AuthQuery#to_signable_string` already does for OAuth callback parameters.

### Proof of Concept
1. Attacker installs the target app on their own (attacker-owned) shop `attacker-shop.myshopify.com` and triggers any subscribed webhook topic, capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify sends (valid because both are computed from the real `api_secret_key`).
2. Attacker replays the request to the app's public webhook endpoint, keeping `raw_body = B` and `x-shopify-hmac-sha256 = H`, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`).
3. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `B` only and it matches `H`, so `Registry.process` in `lib/shopify_api/webhooks/registry.rb:190` does not raise `InvalidWebhookError`.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied `shop` value and invokes the host app's handler, which believes the event legitimately originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
