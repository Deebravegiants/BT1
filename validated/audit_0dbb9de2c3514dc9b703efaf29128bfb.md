Confirmed: `ShopifyAPI::Webhooks::Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header [1](#0-0) , while `to_signable_string` (what the HMAC actually protects) is only the raw body [2](#0-1) . `Registry.process` validates the HMAC and then dispatches directly to the handler using `request.shop`, without ever binding shop to the signed content [3](#0-2) .

### Title
Webhook tenant identity (`shop-domain`) is not covered by the HMAC, allowing cross-tenant shop spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` authenticates a webhook by validating an HMAC computed only over the raw JSON body, but the `shop` value used to route/attribute the webhook to a specific merchant tenant is read from an HTTP header that is completely outside the HMAC's coverage. This breaks the identity binding `hmac_signed_bytes == bytes_the_app_trusts_for_tenant_identity`.

### Finding Description
`Utils::HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` and compares it against the `hmac` field [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [2](#0-1) , and `hmac` is derived from the `hmac-sha256` header [5](#0-4) . Neither of these covers the `shop` accessor, which is read straight from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header [1](#0-0) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` for body integrity, then immediately builds `WebhookMetadata.new(topic:, shop: request.shop, body:, ...)` and calls the app's handler with it [3](#0-2) . Because the header is never included in the signed bytes, any party who possesses one genuine, validly-signed webhook body/HMAC pair (trivially obtainable by installing the app on their own store and receiving a real webhook) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header value. `HmacValidator` will report the request as valid, and the handler will process the payload under the identity of the spoofed shop — i.e., the binding `authenticated_shop == signed_shop` does not hold; it is actually `authenticated_body == signed_body` while `trusted_shop == header_shop (unauthenticated)`.

### Impact Explanation
This allows cross-tenant confusion: an app that uses `WebhookMetadata#shop` to select which merchant's session/data to act on (e.g., to look up the store's `Session`/access token, update per-shop state, or trigger side effects) can be made to apply a validly-signed payload from Shop A to Shop B's account, since the gem provides no protection against header/body mismatch. This matches the High-impact category of cross-tenant access via an identity-binding bypass.

### Likelihood Explanation
Any unprivileged actor who can install the app on their own store (or otherwise obtain one legitimately-signed webhook delivery) can capture the raw body and its `hmac-sha256` value, then send a forged HTTP request directly to the app's public webhook endpoint with an attacker-chosen `shop-domain` header — no access token, `client_secret`, or privileged access is required.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind the header-derived `shop` to the signed body before it is passed to `WebhookMetadata`/handlers — e.g., reject/flag requests where the shop cannot be independently corroborated (such as against the shop associated with the app's own stored session for that webhook), rather than trusting the raw header value implicitly.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body `B` and header `X-Shopify-Hmac-Sha256: H` — this is a valid pair since `H = HMAC-SHA256(secret, B)`.
2. Craft a new HTTP POST to the app's webhook endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` and `X-Shopify-Topic`/`X-Shopify-Webhook-Id` as desired.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers [6](#0-5) ; `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [7](#0-6) .
4. `Registry.process` dispatches the handler with `shop: "victim.myshopify.com"` [3](#0-2) , causing the app to process attacker-controlled/attacker-triggered webhook content under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
