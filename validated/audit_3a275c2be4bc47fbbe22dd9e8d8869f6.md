### Title
Webhook shop-domain header is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw request body only, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` verifies only that the body's HMAC is valid for the app's shared `client_secret`, then trusts the header-derived `shop` value when invoking the app's webhook handler. Because the signing secret (`api_secret_key`) is the same for every shop that installs a given public app, any merchant with the app installed can capture one of their own genuine (body, HMAC) pairs and replay it with a forged shop-domain header claiming to be a different, victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which internally calls `to_signable_string` (i.e., the raw body) against `Context.api_secret_key`: [3](#0-2) [4](#0-3) 

Once the signature check on the body passes, `request.shop` (the header value) is forwarded unchecked into `WebhookMetadata`, which the app's registered handler consumes as the authoritative tenant identifier: [5](#0-4) 

The binding that should hold is:
`HMAC_valid(body, secret) == true` should imply `shop_header == shop_that_Shopify_actually_sent_this_for`.

In reality the equality that actually holds is only:
`HMAC_valid(body, secret) == true` implies `body was HMAC-signed by an app using this secret` — nothing about the `shop` header is covered.

Since `api_secret_key` is a single value shared by the app across *all* shops that install it (it's the client_secret for the app, not a per-shop secret), an unprivileged merchant who installs the app receives legitimate webhooks (body + valid HMAC) for their *own* shop. Nothing prevents them from replaying that same body+HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header with an arbitrary (e.g., victim) shop domain. `HmacValidator.validate` will still succeed because it only checks the body, and `Registry.process` will hand the forged shop identity straight to the app's handler.

### Impact Explanation
This breaks the tenant isolation the HMAC check is supposed to provide: it allows a low-privilege user (any merchant who has installed the app) to make the host application believe a webhook payload originated from a different shop, resulting in cross-tenant data confusion/manipulation (e.g., the app writing/deleting/processing data attributed to the wrong shop's tenant record, or triggering mandatory-compliance webhooks like `customers/redact` against an unrelated shop). This matches the Critical "cross-tenant access" impact category, since the gem's own API (`Registry.process`) is the mechanism that fails to bind the verified content to the claimed tenant.

### Likelihood Explanation
Likelihood is high for any public (non-custom) app: the attacker only needs to be a legitimate, unprivileged installer of the target application to obtain one authentic (body, HMAC) pair, then simply resend it with a different `shop-domain` header value to the app's public webhook endpoint. No access token, `api_secret_key`, or other privileged credential is required — this is exactly the kind of "field acted on but not covered by the HMAC" pattern called out as in-scope.

### Recommendation
- Include the `shop` (and ideally `topic`, `api_version`) header values in the material that is HMAC-verified, or otherwise cryptographically bind them to the payload before trusting them.
- Short of that, document/enforce that consuming applications must independently correlate `request.shop` against the shop associated with the specific webhook subscription/session that they expect to have registered, rather than trusting the header as self-authenticating.
- Consider using unique per-shop secrets or verifying against known session/shop mappings maintained by the host application before invoking handlers.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com` and registers/receives any webhook (e.g., `orders/create`) — Shopify sends a real request such as:
   ```
   POST /webhooks
   shopify-topic: orders/create
   shopify-hmac-sha256: <valid-hmac-of-body>
   shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id": 1, ...}
   ```
2. Attacker captures this exact `body` and `shopify-hmac-sha256` value.
3. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but swaps the shop header:
   ```
   POST /webhooks
   shopify-topic: orders/create
   shopify-hmac-sha256: <same-valid-hmac-of-body>
   shopify-shop-domain: victim-shop.myshopify.com
   Body: {"id": 1, ...}
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this successfully (all required headers present) [6](#0-5) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (the raw body only) and finds it matches — validation succeeds despite the shop header being forged [7](#0-6) .
6. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and the host application processes/persists the webhook as though it legitimately came from `victim-shop.myshopify.com`.

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
