Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated HTTP headers [2](#0-1) . `HmacValidator.validate` only checks that `hmac` matches `to_signable_string` (the body) [3](#0-2) , and `Registry.process` trusts `request.shop` for tenant attribution after that check passes [4](#0-3) .

### Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content as only the raw request body [1](#0-0) , but the `shop` identity used downstream to route webhook data (`request.shop`) is read directly from the `X-Shopify-Shop-Domain` header, which is completely outside the signed content [5](#0-4) . This is the same "field acted on but not covered by the HMAC" class of bug as the reported `innerAdd` analog: a value trusted for a security-relevant decision (carry propagation there, tenant attribution here) is computed/consumed outside the region that is actually integrity-protected.

### Finding Description
`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field using a constant-time compare [6](#0-5) . For webhook requests, `to_signable_string` is defined to be exactly `@raw_body` [1](#0-0) ; none of the Shopify headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) participate in the signature at all [7](#0-6) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [4](#0-3) . Because the body-vs-shop binding is never checked, `shop` here is essentially a header value asserted by whoever delivers the HTTP request, not something bound to the HMAC that supposedly authenticates the payload as coming from Shopify for that shop.

The equality this breaks is: `shop authenticated by HMAC == shop consumed by the handler`. In practice, any body that is HMAC-valid for topic `T` under the app's `client_secret` (e.g. a merchant's own genuine webhook payload for their own shop, which Shopify will legitimately sign and deliver to the app for that merchant) can be re-delivered to the same webhook endpoint with the `X-Shopify-Shop-Domain` (and even `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header swapped to name a different shop, and the HMAC check still passes because those headers were never part of the signed content.

### Impact Explanation
This crosses a tenant boundary: an app that keys off `WebhookMetadata#shop` (e.g., to update per-shop records, revoke access, process GDPR `customers/redact` or `shop/redact` payloads, or attribute billing/business events) can be made to apply a payload legitimately signed for shop A to shop B's tenant data, purely by manipulating unauthenticated headers on an otherwise-valid HMAC. This matches the "cross-tenant access" Critical-impact category since it defeats the shop-identity binding that webhook consumers rely on `HmacValidator` to guarantee.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one genuine HMAC-signed webhook body for their own shop (trivial — any merchant installing the app receives webhooks) and the ability to send an HTTP request to the app's public webhook endpoint with modified headers (also trivial, since webhook endpoints are internet-reachable POST endpoints by design). No access to `api_secret_key` or any privileged credential is required — this only needs a body/HMAC pair the attacker already legitimately owns.

### Recommendation
Include the security-relevant identity fields (`shop`, `topic`, `webhook_id`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the body before they are trusted by `Registry.process`. If Shopify does not sign these headers, the gem should not expose `request.shop` as if it were verified once `HmacValidator.validate` returns true; at minimum, document (and ideally enforce) that consuming apps must independently corroborate `shop` against a known/installed-shop record before acting on webhook data, and consider deriving the topic/shop pairing check from data embedded in the signed body/payload rather than headers.

### Proof of Concept
```ruby
raw_body = '{"id":123,"customer":{"id":1}}'
secret = ShopifyAPI::Context.api_secret_key
hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
)

# This is a genuine signature for a webhook the attacker legitimately received
# for their own shop "attacker-shop.myshopify.com"

spoofed_headers = {
  "x-shopify-topic" => "customers/redact",
  "x-shopify-hmac-sha256" => hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: spoofed_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate succeeds (body+secret match),
#    handler.handle receives WebhookMetadata with shop: "victim-shop.myshopify.com"
```

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
