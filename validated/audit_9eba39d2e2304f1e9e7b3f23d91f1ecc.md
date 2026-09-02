Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from HTTP headers without being part of the HMAC-signed payload [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)`, which checks `request.hmac` against a signature computed from `to_signable_string` (i.e. only the body) [3](#0-2) [4](#0-3) , then dispatches the handler using the unauthenticated `request.shop` value as the tenant identity in `WebhookMetadata` [5](#0-4) .

### Title
Webhook shop-domain identity is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string solely from the raw request body, excluding the `X-Shopify-Shop-Domain` header that the gem exposes as `shop` and that calling applications use as the tenant identity for a webhook.

### Finding Description
The equality the gem is supposed to guarantee is: `shop attributed to a processed webhook == shop that Shopify's HMAC signature actually authenticates`. Per Shopify's documented webhook verification scheme, the HMAC (`X-Shopify-Hmac-Sha256`) is computed over the raw request body only, and this gem implements that faithfully in `to_signable_string` [1](#0-0) . However, `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from headers with no cryptographic binding to the body or to each other [2](#0-1) . `HmacValidator.validate` only proves that the body was signed by the app's secret at some point — it says nothing about which shop, topic, or webhook-id header accompanies that body [4](#0-3) . `Registry.process` then trusts `request.shop` unconditionally to build `WebhookMetadata`, which is handed to the app's handler as the tenant context for the event [6](#0-5) .

Because any body that was ever legitimately signed for one shop (e.g. a `shop/redact` or `app/uninstalled` payload with generic/no shop-identifying content) produces the same valid HMAC over that body regardless of which shop headers accompany it, an unprivileged party who can capture (not forge) one HMAC/body pair — for instance by replaying an intercepted webhook delivery to the app's public webhook endpoint — can resubmit it with an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming an attacker-chosen shop.

### Impact Explanation
This breaks the binding between "authenticated bytes" (the body) and "the identity the application acts on" (the shop header), which is exactly the class of cross-tenant identity confusion the review is scoped to catch. Depending on how the host application's `WebhookHandler` uses `data.shop` (e.g., to select which merchant's local records to update/delete, especially for mandatory compliance topics like `shop/redact` or `customers/redact`), this allows an attacker to cause the app to attribute a webhook event to a different tenant than the one Shopify actually sent it for — a cross-tenant integrity/confusion issue with no need for the app's `client_secret`, access token, or any privileged credential; only replay of a previously observed, legitimately-signed body is required.

### Likelihood Explanation
Exploitation requires capturing a valid `(body, hmac)` pair once (e.g., from network capture, logs, or a shop the attacker controls sending a webhook with attacker-controlled/empty body content) and replaying it to the app's public webhook endpoint with a modified shop header — no secret material or privileged access is needed, and the gem itself performs no cross-check between the signed body and the shop/topic/webhook-id headers.

### Recommendation
Bind the tenant/topic identity into the verified payload rather than trusting headers unconditionally: either include the normalized `shop`, `topic`, and `webhook-id` header values in `to_signable_string` (analogous to how `AuthQuery#to_signable_string` includes `shop` alongside other OAuth callback fields, see `lib/shopify_api/auth/oauth/auth_query.rb` lines 33-43), or require the calling application to independently confirm `request.shop` corresponds to a known, previously-authorized session before trusting `WebhookMetadata#shop`, and document this requirement prominently since the gem's own validation does not provide that guarantee today.

### Proof of Concept
1. Attacker registers/controls `attacker-shop.myshopify.com` (or otherwise observes a legitimate webhook delivery) and captures a webhook body plus its valid `X-Shopify-Hmac-Sha256` value for a topic such as `app/uninstalled` with an empty/generic JSON body `{}`.
2. Attacker sends a POST to the victim app's webhook endpoint with the original `raw_body` and original `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and desired `X-Shopify-Topic`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers without validation of their relation to the body [7](#0-6) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes the HMAC over `@raw_body` [8](#0-7) .
5. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", ...)`, causing the app to act as though Shopify sent this event for `victim-shop.myshopify.com` [5](#0-4) .

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
