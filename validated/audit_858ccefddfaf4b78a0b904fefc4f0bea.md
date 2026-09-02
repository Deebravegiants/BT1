### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once its HMAC validates, and then forwards `request.shop` to the app's handler as the trusted tenant identifier. However, the HMAC is computed only over the raw request body, not over the `shop-domain` header. Any unprivileged actor who can obtain one genuinely-signed webhook (e.g., by installing the app on their own store) can replay that exact body/HMAC pair while substituting the `shop-domain` header for a victim shop, and the library will report it as valid and hand the attacker-chosen tenant to the app.

### Finding Description
The binding that should hold is:
`shop_attributed_to_event == shop_that_the_HMAC_actually_authenticates`

In this gem, that equality is broken:
- `Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the received `hmac` [1](#0-0) .
- For webhooks, `Webhooks::Request#to_signable_string` returns only `@raw_body`, and `shop` is read from a separate, unsigned header (`shopify-shop-domain` / `x-shopify-shop-domain`) [2](#0-1) .
- `Registry.process` validates the HMAC and, once it passes, immediately builds `WebhookMetadata` using `request.shop` — the unauthenticated header value — and dispatches it to the app's handler as the identified tenant [3](#0-2) .

Because the app's `client_secret`/HMAC key is shared across every shop that installs the app, an attacker who installs the app on their own store legitimately receives a webhook with a valid `(raw_body, hmac)` pair signed with that shared secret. Nothing in `raw_body` or the HMAC ties the payload to the attacker's own shop domain — that link exists only in the unauthenticated header. The attacker can therefore resend the identical body/HMAC to the app's webhook endpoint with the `shop-domain` header changed to any victim shop, and `Registry.process` will accept it as a validly-authenticated event for the victim tenant.

### Impact Explanation
This breaks the tenant boundary the HMAC check is supposed to enforce: an app relying on `Webhooks::Registry.process`/`WebhookMetadata#shop` to route data per-shop (e.g., updating shop-scoped records, triggering shop-scoped side effects, or handling mandatory compliance topics like `shop/redact`) can be made to attribute attacker-controlled webhook content to a shop the attacker does not control. This is a cross-tenant confusion vulnerability stemming directly from the library's authentication guarantee not covering the field it hands off as the authenticated tenant identifier.

### Likelihood Explanation
Exploitation only requires the attacker to be able to install the app on any shop (an ordinary, unprivileged action any merchant can take) and to control an HTTP client capable of replaying a captured request with a modified header — no access to `api_secret_key`, tokens, or privileged accounts is needed.

### Recommendation
Bind the shop (and other identity-relevant headers such as `webhook-id`/`api-version`) into the signed material, or otherwise cryptographically tie the header-derived `shop` value to the HMAC before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, the library should document and/or enforce that `request.shop` must not be treated as authenticated by the HMAC alone.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggering a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(app_secret, B)`).
2. Attacker resends the exact same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H`, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers [4](#0-3) ; `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` [5](#0-4) .
4. `Registry.process` calls the app's handler with `shop: "victim.myshopify.com"` even though the HMAC never authenticated that value [3](#0-2) , letting the attacker inject data attributed to a shop they do not own.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
