## Analysis

The webhook verification path binds the HMAC signature to the **raw request body only**, while `shop`, `topic`, `webhook_id`, and `api_version` are all trusted from **unauthenticated HTTP headers** that are never covered by the signature. [1](#0-0) 

`ShopifyAPI::Webhooks::Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` that is handed to the app's handler: [2](#0-1) 

`HmacValidator.validate_signature` computes the signature over `verifiable_query.to_signable_string`, and for `Webhooks::Request` this is defined as just `@raw_body`: [3](#0-2) 

This is the exact bug class from the reference report: a field that is *acted on* (the `shop` identity used to route/attribute the webhook to a tenant) is not *covered by the HMAC* that authenticates the request.

### Title
Webhook `shop-domain` header (and other headers) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the body bytes but not the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers. `Webhooks::Registry.process` nonetheless trusts `request.shop` as the tenant identity passed to the app's webhook handler.

### Finding Description
The binding that should hold is: `hmac_signed_bytes == bytes_the_app_attributes_to_a_tenant`. Here it doesn't: the signed bytes are `raw_body` only [4](#0-3) , while `shop` is read straight from a header with no cryptographic tie to the body or to the signature [5](#0-4) . Because the HMAC secret (`api_secret_key`) is shared across all shops/installations of a given app, any body+hmac pair that is valid for one shop's webhook delivery is also valid HMAC-wise for a forged request carrying a different `shop-domain` header and the same body — `OpenSSL.secure_compare` in `HmacValidator.validate_signature` will still pass [3](#0-2) . `Registry.process` then dispatches the handler using this unverified `request.shop` value as the tenant key [2](#0-1) .

### Impact Explanation
An attacker who can obtain any one legitimate webhook delivery for the app (e.g., by installing the app on their own store, a straightforward unprivileged action, and capturing a webhook with a body they can predict/reuse, such as `customers/redact` or `shop/update` with attacker-controlled content) can replay that exact body+hmac with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop. Since the shop header isn't authenticated, the app processes the payload as belonging to the victim tenant — a cross-tenant data-integrity/confusion issue (e.g., triggering GDPR redaction logic, membership/plan updates, or other tenant-scoped side effects against a shop the attacker doesn't control).

### Likelihood Explanation
Moderate-to-high: the attacker only needs the ability to install the app on a store they control (or otherwise obtain one valid signed webhook payload) and to send an HTTP request with modified headers to the app's webhook endpoint. No access token, `client_secret`, or other privileged credential is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable material used for HMAC validation (or otherwise cryptographically bind them to the payload), and/or require the consuming application to cross-check `request.shop` against a shop that has a known, previously stored session/installation before acting on the webhook.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggering a real webhook (e.g., `shop/update`) with a body the attacker fully controls/predicts. Shopify signs it with the app's shared `client_secret`, producing `(raw_body, hmac)`.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint using the same `raw_body` and `hmac`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers [6](#0-5) ; `HmacValidator.validate` succeeds because it only checks `raw_body` against `hmac` [7](#0-6) .
4. `Registry.process` calls the handler with `shop: request.shop` = `"victim.myshopify.com"` [8](#0-7) , causing the app to perform tenant-scoped actions against the victim shop using attacker-supplied content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
