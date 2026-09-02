### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` is computed only over the raw request body. The `shop` value is never included in the signed bytes, so it is fully attacker-controlled while the HMAC still validates successfully as long as the body matches a secret the attacker legitimately possesses (e.g. from their own shop's real webhook deliveries).

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate`/`validate_signature` compute and compare the HMAC exclusively against that signable string [2](#0-1) . However, `Request#shop` is read directly from the `shop-domain` header, completely independent of the signed payload [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity, forwarding it unchanged to the handler via `WebhookMetadata` [4](#0-3) . This is exactly the "field acted on but not covered by the HMAC" pattern: the equality the code implicitly relies on is `shop (used for tenant routing) == shop (cryptographically bound to the payload)`, but that equality is never enforced — only `body == body` is verified.

Because Shopify signs webhooks with a per-app shared secret (`api_secret_key`), not a per-shop secret, any shop that has installed the app can generate a validly-HMAC'd body (e.g. by triggering a real webhook event on their own store, which is "unprivileged" relative to other merchants using the same app). That attacker can then replay the identical raw body with a forged `shop-domain` header pointing at a victim shop. `HmacValidator.validate` will still return `true`, since it only checks `computed_signature == received_signature` derived purely from the body [5](#0-4) , and `Registry.process` will hand the handler a `WebhookMetadata` object claiming the (forged) victim shop's domain [6](#0-5) .

### Impact Explanation
Host applications built on this gem are documented/expected to use `WebhookMetadata#shop` as the tenant key to look up the correct merchant session, update per-shop records, or make authorization decisions in their webhook handler — this is the entire purpose of exposing `shop` on the metadata object. Since that field carries no cryptographic binding to the signed body, an attacker who controls one tenant (their own installed shop) can forge webhook deliveries attributed to a different tenant, achieving cross-tenant data confusion/access within the host app's webhook processing pipeline. This matches the Critical "cross-tenant access" impact category, since the trust boundary between shops sharing one app installation is broken purely within this gem's verification logic.

### Likelihood Explanation
Likelihood is high for any user of the gem's built-in `Webhooks::Request`/`Registry.process` verification flow: no access token, `client_secret`, or privileged credential is needed beyond installing the app as an ordinary merchant (which is the "unprivileged internet user" position relative to other tenants). The attacker only needs to capture one legitimately HMAC'd webhook body from their own shop and resend it with a modified `shop-domain` header to the app's webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind `shop` to the payload before trusting it, e.g. by having `to_signable_string` incorporate the shop header, or by re-deriving the shop identity from an out-of-band, per-shop-verified source rather than an unauthenticated header value.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a real webhook with raw body `B` and valid header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker resends a request to the app's webhook endpoint with the same body `B` and the same HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` accepts the forged headers [7](#0-6) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against the HMAC [8](#0-7) .
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` [6](#0-5)  and processes attacker-controlled data under the victim shop's identity.

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
