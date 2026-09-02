## Analysis

The reported bug class is: **an index/field is trusted for identity purposes while the actual cryptographic check (HMAC) is computed over different bytes** — i.e., a binding break between "what was authenticated" and "what is acted upon."

Searching `lib/shopify_api/**` (excluding generated REST resources), the closest and reachable analog is in the webhook verification path.

`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines its signable content as **only the raw HTTP body**: [1](#0-0) 

But the `shop`, `topic`, `webhook_id`, and `api_version` identity fields are read straight from **unauthenticated HTTP headers**, not covered by the HMAC signable string: [2](#0-1) [3](#0-2) 

`Registry.process` validates only the HMAC (which covers just the body) and then immediately forwards `request.shop` — an unsigned header — into `WebhookMetadata` passed to the app's handler as if it were verified data: [4](#0-3) [5](#0-4) 

`Utils::HmacValidator.validate` confirms the check truly only compares `verifiable_query.to_signable_string` (the raw body for webhooks) against the computed HMAC — nothing about headers is included in that comparison: [6](#0-5) 

### Title
Webhook shop identity not bound to HMAC signature enables cross-tenant spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed with the app's `client_secret` authenticates the body bytes but not the `x-shopify-shop-domain`, `x-shopify-topic`, or `x-shopify-webhook-id` headers. `Registry.process` treats HMAC success as proof the *entire* request (including `request.shop`) is trustworthy and passes it straight into `WebhookMetadata`, which is handed to the app's `WebhookHandler#handle`.

### Finding Description
The identity binding that should hold is:
`hmac_valid(body) == true` implies `shop header == the shop that produced body`.

That equality does not hold. Because `to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) only signs `@raw_body`, and `shop`/`topic`/`webhook_id` come from `shopify_header` lookups on unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:20-33`), an attacker who controls any webhook delivery target with a *valid* HMAC for some body (e.g., a webhook legitimately delivered to their own installed shop/tenant, whose body+HMAC pair they fully control as the receiving HTTP endpoint) can replay that exact body to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` header. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) will still report success because it only recomputes the HMAC over the body, and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) will construct a `WebhookMetadata` carrying the attacker-chosen `shop` value, dispatched to the host application's handler as verified data.

### Impact Explanation
This crosses a tenant boundary: an app's webhook handler that trusts `WebhookMetadata#shop` (as the library implies it may, since it is only exposed post-HMAC-validation) can be made to process data under a different shop's identity — e.g., writing/deleting data keyed by the spoofed shop, or triggering GDPR redact/mandatory-topic handlers against the wrong tenant. This matches "cross-tenant access" (Critical) per the impact list.

### Likelihood Explanation
Requires the attacker to be able to generate at least one `(body, valid-hmac)` pair for the same app/client_secret — achievable by installing the app on their own shop and capturing one of their own legitimately delivered webhooks, then replaying it with a forged shop header to the shared webhook endpoint. No access to the `client_secret`, tokens, or another tenant's credentials is needed.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in `Request#to_signable_string` (or otherwise cryptographically bind them), or require callers to independently correlate `WebhookMetadata#shop` against a known/installed shop record rather than trusting the header once HMAC on the body succeeds.

### Proof of Concept
1. Install the app on attacker-controlled shop `evil.myshopify.com`; capture a legitimate webhook delivery: body `B` with header `x-shopify-hmac-sha256: H` (valid because Shopify signed `B` with the app's secret) and `x-shopify-shop-domain: evil.myshopify.com`.
2. Replay the exact same `B` and `H` to the app's webhook endpoint, but change the header to `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` reads `shop` from the (now forged) header (`lib/shopify_api/webhooks/request.rb:21-23`); `Utils::HmacValidator.validate` recomputes HMAC over `B` only and returns true (`lib/shopify_api/utils/hmac_validator.rb:27-31`).
4. `Registry.process` dispatches to the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: B, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to act on victim's tenant using attacker-supplied body content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
