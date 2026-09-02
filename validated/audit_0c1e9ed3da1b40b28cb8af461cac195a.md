### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed with the app's `api_secret_key` [2](#0-1) . The `shop` value used downstream to attribute the webhook to a tenant is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed material [3](#0-2) . `Registry.process` validates the HMAC and then immediately hands `request.shop` to the app's handler as an authenticated identity [4](#0-3) , via `WebhookMetadata#shop` [5](#0-4) .

### Finding Description
The identity binding that should hold is: `shop that HMAC-authenticated this request == shop attributed in WebhookMetadata.shop`. In this gem, that equality does not hold, because the HMAC only binds the body bytes, not the shop header.

`api_secret_key` is the *app's* secret and is identical for every shop that installs the app — it is not a per-shop secret [6](#0-5) . Consequently, any attacker who controls a shop that has installed the target app (trivially obtainable — installing a free/dev store copy of a public app) can receive a genuinely Shopify-signed webhook for their own shop. Because the signature covers only `@raw_body` [1](#0-0) , the attacker can replay that exact body + HMAC to the victim app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with any other shop's domain. `HmacValidator.validate` will still pass, since it recomputes the signature only from `to_signable_string` (the body) [7](#0-6) , and `Registry.process` then dispatches to the handler with the forged `shop` field intact [4](#0-3) .

This is exactly the analog pattern of "a field acted on but not covered by the HMAC": the app-level handler is designed to trust `WebhookMetadata.shop` as the authenticated tenant identity (it's the *only* shop identifier the gem exposes post-verification, and the gem's own `process` method is documented as verifying "the request did indeed come from Shopify" before invoking the handler) — but the shop value itself was never authenticated.

### Impact Explanation
This breaks tenant isolation (cross-tenant access): an attacker owning one installed shop can inject arbitrary webhook payloads (topic, body) that the app's handler will process as if they came from a different, victim merchant's shop. Any app logic that uses `data.shop` to select which merchant's data/session to update, write, or invalidate based on webhook content (e.g., `app_uninstalled`, `orders/create`, `customers/redact`, GDPR/data-erasure topics, or app-specific business logic keyed by `shop`) can be manipulated to act on a shop that never sent the request — causing spoofed cross-tenant data mutation with data the attacker fully controls (body, topic). This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only: (1) the ability to install the target app on any shop the attacker controls (standard, low-privilege action, no special credentials), (2) the ability to POST arbitrary HTTP requests with attacker-controlled headers to the app's public webhook endpoint (no privileged access, no TLS interception, no credential theft — `api_secret_key` is never touched). All in-scope reachable paths (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`) confirm this is directly exploitable through this gem's own verification logic, not a host-app misuse of the API — the gem itself hands out `request.shop`/`WebhookMetadata.shop` as if verified.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the HMAC-signable string, or otherwise cryptographically bind the shop identity to the signed payload before exposing it via `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata.shop` is unauthenticated and must be cross-checked by the host app against a known, previously-installed shop record before being trusted.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com`.
2. Shopify delivers a real webhook to the attacker's registered endpoint, e.g. body `{"id":1}"`, with header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` and a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the shared `api_secret_key`.
3. Attacker replays the identical raw body and HMAC value to the victim app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this successfully [8](#0-7) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (the unchanged raw body) and it matches [9](#0-8) .
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [10](#0-9) , even though the webhook never originated from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/auth/oauth.rb (L74-79)
```ruby
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }
```
