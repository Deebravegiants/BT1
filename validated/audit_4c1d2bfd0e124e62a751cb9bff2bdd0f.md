I have sufficient evidence to confirm the vulnerability. The webhook HMAC signature covers only the raw body, while the `shop`, `topic`, `webhook-id`, and `api-version` fields — all read from unauthenticated HTTP headers — are trusted and propagated into the handler without any binding to the signature.

### Title
Webhook `shop` identity not bound to HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content from the raw HTTP body only [1](#0-0) , while the `shop`, `topic`, `webhook_id`, and `api_version` fields consumed by `Registry.process` are read directly from unauthenticated HTTP headers [2](#0-1) . `HmacValidator.validate` only checks the HMAC against `to_signable_string` (the raw body) [3](#0-2) , so the signature never binds the body to a specific shop or topic.

### Finding Description
`Registry.process` validates the request solely via `Utils::HmacValidator.validate(request)` and then dispatches `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) . The `VerifiableQuery` interface only requires `hmac` and `to_signable_string` [5](#0-4) , and `Request#to_signable_string` returns just `@raw_body`, never incorporating the `shop`, `topic`, or `webhook_id` headers [1](#0-0) .

Critically, the HMAC secret (`Context.api_secret_key`) is a single value shared by the app across **every** installed shop/tenant [6](#0-5) . This breaks the intended binding: `hmac_valid(body) == true` should imply `shop_header == shop_that_produced(body)`, but in this design `hmac_valid(body)` only proves "signed with the app's secret at some point for some shop," not "for this specific `shop` header value."

An attacker who legitimately installs the target app on their own shop (an unprivileged, low-cost action available to anyone) receives genuinely-signed webhooks from Shopify (body + HMAC, using the app's single shared secret). Because the header set (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) is never covered by the signature, the attacker can replay the exact same `(raw_body, hmac)` pair directly to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value naming a different, victim merchant. `HmacValidator.validate` will still pass (the body/HMAC pair is valid), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event originated from the victim shop [7](#0-6) .

### Impact Explanation
This is a cross-tenant identity confusion: the gem allows any merchant with a valid app installation to forge webhook events that the host application will process as belonging to a different, unrelated merchant's shop. Any downstream logic keyed on `WebhookMetadata#shop` (e.g., updating that shop's records, triggering shop-scoped side effects, looking up/acting on that shop's stored session or access token) can be manipulated by an attacker who never had any relationship with the victim shop. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires becoming an app user (installing the app on any shop — a normal, unprivileged action), capturing one genuinely Shopify-signed webhook body/HMAC pair, and replaying it to the app's public webhook endpoint with a forged `shop-domain` header. No access to the app's `client_secret`, another merchant's access token, or any privileged credential is required.

### Recommendation
Bind the shop (and ideally topic/webhook id) identity into the verified signable content, or otherwise cryptographically tie the accepted headers to the signed body — e.g., include the `shop` domain in the value that is HMAC-verified, or independently confirm (via a Shopify API call using a session/access token already on file for that exact shop) that the webhook truly originates from the shop named in the header before trusting `request.shop`. At minimum, document that `request.shop`/`request.topic` are unauthenticated and must not be trusted for cross-tenant authorization decisions without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (any user can do this).
2. Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, and a valid `x-shopify-hmac-sha256` computed over the raw body using the app's shared `api_secret_key`.
3. Attacker captures `(raw_body, hmac_header)`.
4. Attacker crafts a new HTTP request to the same webhook endpoint reusing the identical `raw_body` and `hmac_header`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present) [8](#0-7) ; `Utils::HmacValidator.validate` returns `true` since it only checks `raw_body` against the shared secret [6](#0-5) .
6. `Registry.process` calls the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, and the host app processes the forged event as belonging to `victim-shop.myshopify.com` [4](#0-3) .

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L6-16)
```ruby
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```
