This confirms the asymmetry: `AuthQuery.to_signable_string` (`lib/shopify_api/auth/oauth/auth_query.rb:34-43`) explicitly folds `shop` into the HMAC-signed string for OAuth callbacks, but `Webhooks::Request.to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) only returns `@raw_body` — the `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are excluded from the signed content entirely, even though `Registry.process` trusts `request.shop` to build `WebhookMetadata` handed to the app's handler.

### Title
Webhook shop identity not bound to HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC solely against this raw body, so the `x-shopify-shop-domain` header is never checked against the signature. `Registry.process` then trusts `request.shop` unconditionally to build the `WebhookMetadata` passed to the app's registered handler.

### Finding Description
The identity binding that should hold is: `shop authenticated == shop delivered to handler`. In `hmac_validator.rb`, `validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it only to the received HMAC [1](#0-0) . For webhooks, `to_signable_string` is defined as just `@raw_body` [2](#0-1) , meaning the `shop`, `topic`, `api_version`, and `webhook_id` accessors — all sourced from headers — are outside the HMAC's coverage [3](#0-2) .

`Registry.process` raises unless `HmacValidator.validate(request)` succeeds, then immediately builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from the same unauthenticated headers and dispatches it to the app-registered handler [4](#0-3) .

Contrast this with `Auth::Oauth::AuthQuery`, used for the OAuth callback, where `to_signable_string` explicitly includes `shop` in the signed parameter set [5](#0-4) . The webhook path lacks this equivalent binding: anyone who can obtain one genuine `(raw_body, hmac)` pair signed by Shopify — trivially available to any merchant who installs the app on their own store and observes the webhook delivery to their own endpoint/logs — can replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The HMAC still validates (it only covers the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to a victim shop chosen by the attacker.

### Impact Explanation
This breaks the shop-authenticated vs. shop-delivered binding and enables cross-tenant confusion: an app's webhook handler — which typically keys persistence, side effects, or lookups (e.g., `Auth::Session`, database records) off `WebhookMetadata#shop` — can be made to attribute one merchant's event data to a completely different, arbitrary shop domain, without needing any credentials for that victim shop. Depending on how the host app uses `shop` from the webhook payload (e.g., to load/update a `Session`, write order data, or trigger downstream automation), this can lead to cross-tenant data corruption or unauthorized actions performed under another merchant's identity, satisfying the "cross-tenant access" impact criterion.

### Likelihood Explanation
The webhook endpoint is a public HTTP endpoint reachable by anyone. The only additional resource an attacker needs is one legitimate `(body, hmac)` pair, which is available to any unprivileged merchant who installs the app on a low-value/free development store they control and captures Shopify's real webhook delivery to their own server (no `api_secret_key`, TLS interception, or privileged account needed). Replaying that pair with a forged `shop-domain` header is a simple HTTP replay.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` (or at minimum `shop`) in the HMAC-signed content for webhook requests, mirroring the approach taken in `AuthQuery#to_signable_string`, or otherwise cryptographically bind the shop domain to the signature so a replayed body cannot be attributed to a different shop.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g., `orders/create`) and capture the real request Shopify sends: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for secret `api_secret_key`).
2. Replay to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [6](#0-5) .
4. `Registry.process` dispatches `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` to the handler [7](#0-6) , causing the app to process attacker-supplied data as if it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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
