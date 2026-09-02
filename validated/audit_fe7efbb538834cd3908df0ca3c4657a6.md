## Finding: Webhook `shop` header is trusted for handler routing without being covered by the HMAC signature

### Title
Webhook `shop-domain` header is not covered by the HMAC signature but is trusted as an authenticated identity - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are read directly from unauthenticated HTTP headers and passed on to the registered webhook handler as trusted identity data.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` simply reads the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed payload [2](#0-1) . `Utils::HmacValidator.validate` verifies `request.hmac` against `HMAC(secret, request.to_signable_string)` [3](#0-2) , i.e. it authenticates the body bytes only. `Registry.process` then calls `Utils::HmacValidator.validate(request)` and, once it passes, forwards `request.shop` (and `topic`, `api_version`, `webhook_id`) straight into the handler as authenticated metadata: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

This breaks the intended binding `bytes_verified == bytes_used_for_identity`: the equality that should hold is `HMAC-covered content == shop identity used downstream`, but here `shop` comes from a header that is outside the signed content, so `HMAC-covered content ⊂ shop identity used downstream` — the shop value can be forged independently of the signature that only covers the JSON body.

Compare this to `Auth::Oauth::AuthQuery#to_signable_string`, which explicitly folds `shop` into the signed parameter set for the OAuth callback [5](#0-4) ; the webhook `Request` class does not follow the same pattern for `shop`, `topic`, `api_version`, or `webhook_id`.

### Impact Explanation
An attacker who can produce (or replay/observe) any valid `(body, hmac)` pair for their own shop/topic combination — e.g. from a webhook fired to their own development store, which is fully attacker-controlled and produces a Shopify-signed request — can resend that exact body+hmac to a merchant's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` and `x-shopify-topic` header. Because `HmacValidator.validate` only checks the raw body against the signature, the forged headers pass validation, and `Registry.process` dispatches to the handler with attacker-chosen `shop` and `topic` values while `Utils::HmacValidator.validate` reports success. Handlers written against this gem's documented contract (which implies `WebhookMetadata#shop`/`#topic` are authenticated, since HMAC validation gate is exactly what "validated" is supposed to mean) may use `shop` to select which tenant's data/session to update, leading to cross-tenant data confusion in the host application's webhook handler. This does not directly hand over a merchant's access token or `client_secret`, but it can enable cross-tenant behaviour driven by a value the gem itself asserts is verified.

### Likelihood Explanation
This requires the attacker to control or capture at least one validly-signed webhook body/hmac pair for the target's app (obtainable via the attacker's own store subscribed to that app, which is a normal, unprivileged flow for any public app), plus the ability to send an HTTP request to the app's webhook endpoint with custom headers — both are within reach of an unprivileged internet user for any app that installs on a store the attacker controls.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the HMAC-signed payload (or otherwise document clearly that only the body is authenticated and that `shop`/`topic` headers must not be trusted for tenant routing), mirroring the approach in `AuthQuery#to_signable_string`, which binds `shop` into the signed string.

### Proof of Concept
1. Attacker installs the victim's app on their own store `attacker-shop.myshopify.com` and registers/receives one legitimate webhook, capturing `raw_body`, and the `x-shopify-hmac-sha256` header — a validly signed `(body, hmac)` pair, computed as in `HmacValidator.compute_signature` [6](#0-5) .
2. Attacker POSTs this exact `raw_body` and `x-shopify-hmac-sha256` to the target app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: <different topic>`.
3. `Request.new` accepts the headers (only presence, not content, is checked) [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` [8](#0-7) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the signature never covered that value, so any handler logic keyed on `data.shop` operates on attacker-controlled shop identity despite “HMAC validated” being true.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
