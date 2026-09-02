### Title
Webhook `shop`/`topic` fields are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then dispatches to the app's handler using the `shop` and `topic` values taken directly from HTTP headers, which are never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to that body [2](#0-1) .

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)` [3](#0-2) , and `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` (i.e. the raw body only) and compares it against the `hmac-sha256` header using a constant-time comparison [4](#0-3) . This check only proves that the body was produced/signed with the app's `client_secret` at some point - it says nothing about which shop the header claims to be from.

Immediately after this check passes, `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` and hands it to the app's registered handler [5](#0-4) . The handler receives an unauthenticated `shop` value as the tenant identifier for a call whose only authentication is "the body was HMAC-signed by *some* legitimate webhook delivery from *some* shop using this app."

The broken binding is:
`shop header value used by handler == shop that actually generated/owns the signed body`
which the code never enforces - it only enforces `HMAC(secret, body) == received_signature`.

### Impact Explanation
Because the HMAC secret (`api_secret_key`) is shared across all shops that install the app rather than being per-tenant, any body+HMAC pair that was legitimately generated for one shop (for example, by an attacker installing the app on their own store and receiving a real webhook delivery, or by capturing/replaying a delivery) remains valid for any other value of the `shop-domain` header, since that header is not part of the signed content. An attacker who controls (or has captured) one valid `(raw_body, hmac)` pair can resend the exact same payload while forging the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to point at a victim shop. `HmacValidator.validate` still succeeds, and the app's handler processes the event as if it originated from the victim shop - a cross-tenant confusion/spoofing condition, since apps commonly use the `shop` field from `WebhookMetadata` to select which merchant's stored session/data to act on.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint and possession of one valid raw-body/HMAC pair for the shared `client_secret` (obtainable by any user who installs the app on their own store and observes their own genuine webhook deliveries - no privileged Shopify credentials, access tokens, or the `client_secret` itself are needed). This is a realistic "unprivileged internet user" scenario.

### Recommendation
Bind the tenant-identifying fields into the authenticated material: include `shop`, `topic`, and `webhook_id` (in addition to the body) in the signable string used for HMAC validation, or otherwise cryptographically bind the `shop-domain` header to the signed payload before it is trusted for handler dispatch. At minimum, cross-check the `shop` header against the shop the app expects for the specific webhook subscription/session context before invoking the handler.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggering a real event (e.g. `orders/create`). They capture the delivered raw JSON body and its `x-shopify-hmac-sha256` header - both valid under the app's shared `api_secret_key`.
2. Attacker sends a POST to the app's webhook endpoint with the same raw body and the same valid `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers [6](#0-5) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over the unchanged raw body and succeeds [3](#0-2) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` [5](#0-4)  and performs whatever tenant-scoped action the app implements (e.g. updating victim shop's stored order data) based on attacker-controlled content, despite the event never having occurred on the victim's store.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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
