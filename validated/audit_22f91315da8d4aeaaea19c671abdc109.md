### Title
Webhook `shop-domain` (tenant identity) is not covered by the HMAC signature, allowing tenant spoofing in `Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Registry.process` authenticates only the raw request body via HMAC, but uses the unauthenticated `x-shopify-shop-domain` header value as the tenant identity passed to the merchant's webhook handler, breaking the binding "HMAC-verified bytes == bytes used to identify the tenant."

### Finding Description
`Utils::HmacValidator.validate` verifies the signature over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body`: [1](#0-0) 
The `shop` accessor, however, is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is never part of the signed content: [2](#0-1) [3](#0-2) 
`Registry.process` validates the HMAC and then immediately forwards `request.shop` (the unauthenticated header) into `WebhookMetadata`, which is delivered to the app's `WebhookHandler#handle`: [4](#0-3) 
`WebhookMetadata` treats `shop` as a trusted, first-class field the handler is expected to rely on for tenant scoping: [5](#0-4) 

The HMAC only proves that Shopify's secret produced a signature for the given `raw_body` bytes; it says nothing about which shop sent it. `HmacValidator.validate_signature` compares only `computed_signature` (derived from the body) against the received signature and never incorporates the shop domain into the signable string: [6](#0-5) 

Contrast this with the OAuth callback path, where `shop` *is* part of the signed content (`AuthQuery#to_signable_string` includes `shop`), correctly binding the shop identity to the signature: [7](#0-6) 

This is exactly the identity-binding gap called out in the bug-class rules: a field acted on (the `shop` used for tenant routing/authorization inside the handler) is not covered by the HMAC that is supposed to authenticate the message.

### Impact Explanation
Any party who can obtain one valid HMAC signature for a given raw body from Shopify's push (e.g., by observing a webhook of their own single-tenant shop, or via a shop they control receiving any webhook with a body they can predict/replicate, such as a mandatory `shop/redact` webhook with empty/known JSON) can replay that request while substituting an arbitrary `x-shopify-shop-domain` header. `Registry.process` will accept the (still-valid-for-that-body) HMAC and deliver `WebhookMetadata` claiming to originate from a victim shop the attacker never has access to. Any app whose `WebhookHandler#handle` implementation trusts `data.shop` for tenant-scoped writes/lookups (a documented, expected usage pattern) can be tricked into acting on behalf of, or mutating data associated with, a shop the attacker does not own — a cross-tenant identity confusion. This satisfies the "cross-tenant access" criterion for Critical/High impact.

### Likelihood Explanation
Exploitation requires the attacker to already possess at least one valid `(body, hmac)` pair signed with the app's `client_secret`/HMAC key for some shop (this is available to any shop that has the app installed, including the attacker's own trial/dev store, or via the mandatory GDPR webhooks which have predictable/empty bodies). Given that, forging the `shop-domain` header requires no cryptographic secret, since the gem never binds the header to the signature. This is a low-effort library-level gap reachable from an unprivileged HTTP endpoint (the app's own webhook receiver), not merely a host-application misuse issue, because the vulnerable binding lives entirely in `Webhooks::Request#to_signable_string` and `Registry.process`.

### Recommendation
Include the shop domain (and ideally the topic/api-version) in the HMAC-covered signable content, or otherwise cryptographically bind the `shop-domain` header to the verified payload before it is exposed via `WebhookMetadata`. At minimum, `Webhooks::Request#to_signable_string` should incorporate `shop` (mirroring how `AuthQuery#to_signable_string` binds `shop` into its signed string), and `Registry.process` should reject requests where the header-derived shop cannot be tied to the HMAC-verified body.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` (or uses the mandatory `customers/data_request` webhook, whose body format is fixed/known).
2. Shopify sends a legitimate webhook to the app with a valid `x-shopify-hmac-sha256` for that specific `raw_body` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `(raw_body, hmac)` and replays the exact same body/hmac to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the signature (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and invokes the app's handler, which acts as if the event genuinely originated from the victim shop (`lib/shopify_api/webhooks/registry.rb:188-200`).

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
