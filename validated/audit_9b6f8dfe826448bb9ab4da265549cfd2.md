Confirmed: `WebhookMetadata` carries `shop` [1](#0-0)  populated directly from the request's `shop-domain` header in `Registry.process` [2](#0-1) , while the HMAC only ever signs the raw body via `to_signable_string` [3](#0-2)  and the `shop` accessor simply reads an unauthenticated header [4](#0-3) .

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing tenant spoofing in `ShopifyAPI::Webhooks::Registry.process` - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` builds the value HMAC-verifies from the raw body only (`to_signable_string` returns `@raw_body`) [3](#0-2) , but `Registry.process` trusts `request.shop`, which is read straight from the `X-Shopify-Shop-Domain` HTTP header with no cryptographic binding to that HMAC [4](#0-3) [2](#0-1) .

### Finding Description
`Utils::HmacValidator.validate` only checks the HMAC against `verifiable_query.to_signable_string`, which for webhooks is exactly `@raw_body` [5](#0-4) [3](#0-2) . The `shop-domain` header is never part of the signed material — it's parsed out of the HTTP headers with no relation to the signature bytes [6](#0-5) . `Registry.process` nonetheless treats `request.shop` as authenticated and forwards it directly into `WebhookMetadata`, which the host application's handler is expected to use to identify which merchant/tenant the webhook belongs to [2](#0-1) [1](#0-0) .

This breaks the identity binding: `hmac-signed(body) == body-for-shop(shop-domain-header)`. In practice, an attacker who is a legitimate merchant/publisher for one Shopify shop receives correctly-signed webhooks for their own shop (a valid `raw_body` + `hmac` pair signed with the app's shared secret). Since the HMAC never binds the `shop-domain` header, that same `(raw_body, hmac)` pair remains valid if replayed with a different `shop-domain` header value pointing at a victim shop. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the payload came from the victim shop, even though the bytes were never actually associated with that shop by Shopify.

### Impact Explanation
Host applications built on this gem's documented webhook API (per `docs/usage/webhooks.md`, out of scope for citation but consistent with `WebhookHandler#handle`) key their per-tenant business logic off `WebhookMetadata#shop` — this is the field the gem hands them as "the shop this webhook is for." Since that field isn't bound to the signature, an attacker who can obtain one legitimately-signed webhook payload for a shop they control can forge the tenant attribution for arbitrary victim shop domains, letting them write, delete, or trigger side effects under another merchant's tenant context in the host app. This crosses the tenant boundary the HMAC is supposed to enforce, which matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only being a Shopify merchant/app-installer (an unprivileged, self-service role) able to receive at least one real webhook for their own shop and the ability to POST an HTTP request with attacker-controlled headers to the app's public webhook endpoint — both are within reach of any internet user who installs the app on their own store, with no access token, `client_secret`, or privileged role required.

### Recommendation
Include the shop domain (and other Shopify-supplied identity headers such as `X-Shopify-Webhook-Id`) inside the HMAC-signed material, or otherwise cryptographically bind them to the verified body — e.g. change `Request#to_signable_string` to incorporate the shop-domain header, or independently verify the shop domain via a trusted source (such as looking it up via a previously stored, session-bound identifier) rather than trusting the header value directly in `Registry.process`.

### Proof of Concept
1. Install the app on shop `attacker-shop.myshopify.com` and capture one legitimate webhook request Shopify sends to the app's callback URL, noting its `raw_body`, `X-Shopify-Hmac-Sha256` value, and other headers.
2. Replay that exact HTTP request to the same endpoint, but replace the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com` (leave `raw_body` and `X-Shopify-Hmac-Sha256` untouched).
3. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC [7](#0-6) ; `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` even though Shopify never generated this HMAC for that shop [8](#0-7) .

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
