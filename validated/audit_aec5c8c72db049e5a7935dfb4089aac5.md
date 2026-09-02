This confirms the finding. The `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read directly from unauthenticated HTTP headers via `shopify_header` [2](#0-1) . `Registry.process` validates only the HMAC over the request and then dispatches the handler using `request.shop` as the tenant identifier [3](#0-2) .

### Title
Webhook shop/topic identity not bound to HMAC signature allows cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, and `webhook_id` values that `Registry.process` uses to route and attribute the webhook are taken from HTTP headers that are never included in the signed bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors pull straight from `@headers` via `shopify_header`, with no cryptographic binding to the HMAC [4](#0-3) . `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only proves that `raw_body` was signed with `Context.api_secret_key` at some point [5](#0-4) ; it never verifies that the accompanying `shop`/`topic` headers were the ones originally sent by Shopify for that payload. After the check passes, the handler is invoked with `request.shop` as the tenant identity: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [6](#0-5) .

The broken identity binding, stated as an equality that should hold but does not:
`bytes_verified_by_HMAC (raw_body) == identity_used_downstream (shop header, topic header)` — these are actually independent inputs. The HMAC signature attests only to the body; the shop/topic values that determine *which merchant's data gets written or which redaction/topic logic fires* are unauthenticated.

Because the webhook endpoint is a public HTTP endpoint owned by the app developer (not a Shopify-internal channel enforced by the gem), any actor able to reach that URL can replay a **body+hmac pair that they legitimately received for their own shop** while substituting an arbitrary `shopify-shop-domain` header (and/or `shopify-topic` header) naming a different, victim shop. `Utils::HmacValidator.validate` will accept the request because the signed bytes (`raw_body`) are unchanged and genuinely match the secret; only the un-signed headers were altered.

### Impact Explanation
This crosses the tenant boundary the gem is documented to protect: a webhook payload legitimately generated for shop A can be attributed to shop B purely by forging a header, since the identity fields consumed by the host application (via `WebhookMetadata#shop`) are not covered by the same authenticity proof as the payload. If a host application uses `request.shop`/`WebhookMetadata#shop` to select which merchant's session/record to update (the documented and expected usage pattern), this enables cross-tenant data confusion/injection — classified as Critical (cross-tenant access) per the impact rubric.

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate merchant/installer of the app (an unprivileged actor relative to other merchants) so as to receive at least one genuine webhook with a valid `raw_body`/`hmac-sha256` pair for their own shop, and (2) sending a directly-crafted HTTP POST to the app's public webhook endpoint with that same body/HMAC but a different `shopify-shop-domain` (and optionally `shopify-topic`) header. No access to `api_secret_key`, tokens, or the victim's credentials is required, since the header fields are not part of the cryptographic proof at all.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (or otherwise cryptographically bind them, e.g. via a separate signed envelope) so that `Utils::HmacValidator.validate` fails if any of these identity fields are altered relative to what Shopify actually sent. At minimum, `Registry.process` should not trust `request.shop`/`request.topic` for tenant attribution unless those fields are covered by the same signature check as the body.

### Proof of Concept
1. App receives a genuine webhook from Shopify for `attacker-shop.myshopify.com`:
   - Headers: `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: customers/data_request`, `shopify-hmac-sha256: <valid-hmac-of-raw_body>`
   - Body: `raw_body` (arbitrary JSON payload)
2. Attacker (who legitimately received this webhook as the shop owner) resends the exact same `raw_body` and `shopify-hmac-sha256` value to the app's public webhook endpoint, but changes the header to `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully (all required headers present) [7](#0-6) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and finds it matches — validation **passes** despite the shop header being forged [8](#0-7) .
5. The handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though the payload was never issued by Shopify for that shop, demonstrating the cross-tenant identity confusion.

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
