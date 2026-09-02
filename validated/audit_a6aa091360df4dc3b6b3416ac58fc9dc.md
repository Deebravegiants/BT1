### Title
Webhook `shop-domain` header is trusted as the tenant identifier but is not covered by the HMAC signature, allowing shop spoofing / cross-tenant misattribution - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking `Utils::HmacValidator.validate(request)` against `Webhooks::Request#to_signable_string`, which returns only `@raw_body` [1](#0-0) . The `shop` attribute that is subsequently handed to the host application via `WebhookMetadata` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is never part of the signed material [2](#0-1) . This breaks the equality "the shop identity acted upon == the shop identity authenticated by the HMAC."

### Finding Description
`Webhooks::Request` gathers `topic`, `shop`, `api_version`, and `webhook_id` from raw HTTP headers [3](#0-2) , but only enforces the presence of the headers (`topic`, `hmac-sha256`, `shop-domain`) without cryptographically binding their values to the signature [4](#0-3) . The `Utils::HmacValidator.validate` call computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` accessor [5](#0-4) , but for `Webhooks::Request` that signable string is defined as just the raw JSON body, excluding the `shop` header entirely [1](#0-0) .

`Registry.process` then trusts `request.shop` and forwards it directly into `WebhookMetadata`, which is the exact value passed to the host application's `WebhookHandler#handle` implementation for tenant-specific processing (e.g. looking up which merchant/session the event belongs to) [6](#0-5) [7](#0-6) .

Because the app's `client_secret` (the HMAC key) is shared across all shops that install the app, any attacker who has installed the app on their own store receives legitimate webhook deliveries with a valid HMAC computed over the body they control. Since the `shop-domain` header is outside the signed data, the attacker can replay that same body+HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim merchant's domain). `HmacValidator.validate` will still pass because it only checks the (unmodified) body against the HMAC; `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` is the attacker-chosen value, not the shop that Shopify actually sent the webhook for.

### Impact Explanation
This is a cross-tenant identity-binding break: the field that downstream code treats as the authenticated tenant boundary (`shop`) is not the field verified by the cryptographic check (raw body only). Any host application that uses `WebhookMetadata#shop` to route webhook side effects to a specific merchant's data/session (the intended, documented use of this field) can be made to apply an attacker-controlled shop domain to legitimate, HMAC-valid webhook data, resulting in cross-tenant data/state confusion. This matches the "Critical - cross-tenant access" impact category since it lets one authenticated app-installing tenant impersonate another tenant's identity in webhook-triggered processing without ever needing the target's credentials.

### Likelihood Explanation
Any unprivileged attacker who can install the app on a store they control (a normal, permitted action for any Shopify Partner/dev store) can obtain valid HMAC-signed webhook bodies from Shopify at will, then replay them to the app's public webhook endpoint with a modified shop-domain header. No secret material, TLS interception, or privileged access is required — only the ability to intercept/re-send HTTP requests to the app's own publicly reachable webhook URL, which is standard replay tooling (e.g., curl/Burp). The gem provides no mitigation (no shop binding in the signature, no origin/IP check), so exploitability depends only on the host app trusting `data.shop` as-is, which is exactly what the gem's own API design encourages.

### Recommendation
Include the `shop` (and ideally `topic`/`api_version`) header values in the signable string used for HMAC verification in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the shop domain to the payload before exposing it via `WebhookMetadata`. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant routing without independent verification (e.g., cross-checking against a known list of installed shops).

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and registers a webhook (or waits for any webhook event).
2. Shopify sends the app: 
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-topic: orders/create`
   - Body: `{"id": 123, ...}`
3. Attacker captures this valid request and replays it to the app's webhook endpoint, changing only the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - (body and `x-shopify-hmac-sha256` unchanged)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`@raw_body` only) [1](#0-0)  — this still matches, so validation passes.
5. `handler.handle` is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` [8](#0-7) , even though the event actually originated from `attacker.myshopify.com`. Any host logic that keys off `data.shop` to select the tenant/session now operates on the wrong (attacker-chosen) tenant.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
