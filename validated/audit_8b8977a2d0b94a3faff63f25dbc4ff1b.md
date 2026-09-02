## Title
Webhook `shop` (tenant) identity is read from an HTTP header that is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the webhook's authenticity from an HMAC computed over the raw request body only, but the merchant/tenant identity (`shop`) used by consuming applications to route and attribute the payload is taken from a separate, unsigned HTTP header. This breaks the intended binding of "HMAC-verified bytes == identity acted upon," letting any party who possesses one valid `(raw_body, hmac)` pair for the shared app secret relabel that payload as belonging to a different shop.

### Finding Description
`Utils::HmacValidator.validate` verifies a webhook by recomputing the HMAC over whatever `to_signable_string` returns and comparing it against the `hmac` field: [1](#0-0) 

For `Webhooks::Request`, `to_signable_string` returns only the raw body: [2](#0-1) 

But the `shop` value that is subsequently trusted and handed to the registered handler is pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never part of the signed material: [3](#0-2) [4](#0-3) 

`Registry.process` validates the HMAC and then dispatches directly using `request.shop`, with no cross-check that the signed body actually originated from that shop: [5](#0-4) 

Because all shops that install the same app share the same `client_secret`/`api_secret_key`, the HMAC alone does not bind a payload to a particular shop — it only proves "signed by this app's secret," which is true for every one of the app's installs. The `shop` header is attacker-controllable HTTP metadata and is exactly the kind of "field acted on but not covered by the HMAC" identity-binding gap called out in the bug-class hint: verified bytes (the body) ≠ bytes that determine tenant identity (the header).

### Impact Explanation
This is a cross-tenant confusion vector (Critical bucket: cross-tenant access). A merchant who has installed the app is an "unprivileged internet user" with respect to other tenants of the same app, yet can:
1. Capture one legitimately-signed webhook body/HMAC pair for their own shop (trivial — they receive real webhooks for their own store, or can trigger one).
2. Replay that exact `(raw_body, hmac)` to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain.
3. `HmacValidator.validate` passes (it only checks the body/secret), and `Registry.process` calls the handler with `request.shop` equal to the attacker-chosen victim domain, causing the host application to process/attribute the payload as if it came from the victim shop.

Depending on what the host app's handler does with `data.shop` (e.g., looking up a session/access token for that shop, writing state keyed by shop, or triggering shop-scoped side effects), this can lead to state corruption or actions being taken against/on behalf of another tenant.

### Likelihood Explanation
Requires no privileged credentials — only that the attacker be a legitimate installer of the app (an "unprivileged internet user" relative to other tenants) and be able to POST an HTTP request with attacker-controlled headers to the app's public webhook endpoint. Capturing a valid `(body, hmac)` pair is straightforward since apps receive real webhooks routinely.

### Recommendation
Bind the trusted `shop` value to the signed content rather than to an unsigned header:
- Include the shop domain (and ideally other routing metadata) inside the HMAC-signed payload/signable string, or
- Cross-validate the header-provided `shop` against a shop identity independently derived from data that is covered by the signature (e.g., a shop id embedded in the JSON body), rejecting the webhook if they disagree.

At minimum, document/enforce that host applications must not trust `request.shop` for tenant attribution without an additional binding check, and consider changing `to_signable_string`/`HmacValidator` usage for webhooks to incorporate the shop header into the signed digest so tampering is detected.

### Proof of Concept
```ruby
# Attacker owns shop "attacker.myshopify.com" and legitimately receives:
raw_body = '{"id":1,"note":"hello"}'
valid_hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)
)

# Attacker replays the SAME body/hmac but swaps the shop-domain header to a victim shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,       # still valid, since body is unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # unsigned, attacker-controlled
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The host app now believes this payload came from victim-shop.myshopify.com.
```

### Citations

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
