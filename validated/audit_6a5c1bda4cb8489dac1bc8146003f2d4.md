### Title
Webhook `shop-domain` header is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body, never the shop-domain header. Because a single app-level `api_secret_key` is shared across every shop that installs the app, any unprivileged internet user who installs the app on their own shop can capture a genuinely-signed webhook (valid body + valid HMAC), then replay it against the app's webhook endpoint with the `shop-domain` header rewritten to point at a victim shop. `ShopifyAPI::Webhooks::Registry.process` accepts this forged identity and dispatches it to the app's handler as if it originated from the victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: ` [1](#0-0) `. The `shop` accessor, however, is taken straight from an unauthenticated header with no cross-check against the signed payload: ` [2](#0-1) `.

`HmacValidator.validate` computes/compares the signature purely from `verifiable_query.to_signable_string` (the body) and the app secret — it has no knowledge of, and does not bind, the `shop` field: ` [3](#0-2) `.

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity forwarded to the app's handler, without any additional binding check: ` [4](#0-3) `.

Since `api_secret_key` is one value per app (not per shop) — used identically for every merchant's webhooks and for OAuth/JWT validation elsewhere in the gem (e.g. ` [5](#0-4) `) — any shop that installs the app can obtain a validly HMAC-signed webhook body signed with the same secret used for all other installs. Replaying that body with a different `shop-domain` header produces a `Request` object that passes `HmacValidator.validate` yet reports an arbitrary attacker-chosen `shop`. This breaks the identity binding: **shop authenticated by HMAC ≠ shop stored/used as the tenant key** by the handler.

### Impact Explanation
Any downstream logic keyed off `WebhookMetadata#shop` (session lookup, per-tenant data writes, billing/plan changes, uninstall handling, etc.) can be triggered by an attacker under a victim shop's identity while supplying attacker-chosen `topic`/body content limited only to whatever payload the attacker legitimately received from their own shop for that topic. This is a cross-tenant identity confusion at the gem level — the exact class of "shop authenticated versus shop used as identity key" called out as in-scope — and can lead to cross-tenant data corruption or unauthorized actions performed against a victim merchant's stored session/data.

### Likelihood Explanation
No credentials, tokens, or `api_secret_key` are required. An attacker only needs to be able to install the target app on their own store (or otherwise obtain a validly-signed webhook of a chosen topic/shape) and then send a plain HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header. This is entirely reachable by an unprivileged internet user through the gem's documented webhook processing path (`Registry.process` / `Webhooks::Request`).

### Recommendation
Bind the shop identity into the verified material: either include the shop domain in the signable string used for HMAC verification, or require the caller to supply the expected shop out-of-band (e.g., from the route/tenant context established independently of the request headers) and assert `request.shop == expected_shop` before dispatch in `Registry.process`. At minimum, document that `Request#shop` must never be trusted as an authenticated tenant identifier since it is not covered by the HMAC in `to_signable_string`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; Shopify sends a legitimate webhook with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body B computed with the app's shared api_secret_key>`, and body `B`.
2. Attacker captures this request and replays it to the app's public webhook endpoint, changing only the header to `x-shopify-shop-domain: victim.myshopify.com` (body `B` and HMAC unchanged).
3. `Webhooks::Request.new` parses the forged headers/body: ` [6](#0-5) `; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `body` + shared secret: ` [7](#0-6) `.
4. The handler is invoked with `WebhookMetadata` carrying `shop: "victim.myshopify.com"` even though the payload actually originated from the attacker's own shop: ` [8](#0-7) `.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-31)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end
```
