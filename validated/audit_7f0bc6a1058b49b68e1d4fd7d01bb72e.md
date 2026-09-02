### Title
Webhook `shop` (tenant identity) is not covered by the HMAC signature, allowing spoofed shop-domain on a validly-signed body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the shop identity used by consumers of the request (`request.shop`) is read directly from the unauthenticated `X-Shopify-Shop-Domain` header. This breaks the identity binding `shop_verified_by_hmac == shop_used_for_tenant_dispatch`, which is the same asymmetric-update class of bug described in the report (a value used for control-flow decisions diverges from the value that was actually authenticated).

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

and `HmacValidator.validate` computes/compares the signature purely against this signable string: [2](#0-1) 

Meanwhile, `Request#shop` — the value that identifies *which merchant/tenant* the webhook belongs to — is pulled straight from the `X-Shopify-Shop-Domain` header without any cryptographic binding to the body or to the HMAC: [3](#0-2) 

The header value is only checked for *presence*, not integrity, during construction: [4](#0-3) 

The equality that should hold is:
`shop_bound_in_HMAC(raw_body) == shop_used_to_route/attribute_the_webhook(request.shop)`

Because the HMAC only signs `@raw_body`, this equality never actually holds — `request.shop` can be any string the caller/attacker supplies in the header, independent of what (if anything) the body's HMAC attests to. A caller that trusts `Request#hmac` returning `true` from `HmacValidator.validate(request)` as proof that "this webhook, including its shop, came from Shopify for this merchant" is relying on a binding this gem does not provide.

### Impact Explanation
An app that uses `request.shop` (after HMAC validation succeeds) to scope tenant data — e.g., to look up the session/access token for that shop or to attribute the payload to a specific merchant record — can be made to process a validly-HMAC'd body under an attacker-chosen shop domain, since the shop field carries no authentication. This is a cross-tenant identity-binding break in the same family as the report's core issue: a value is acted upon (`shop` for tenant dispatch) while the authenticity check (`hmac`) covers a disjoint set of bytes (`raw_body` only, no headers). This matches the report's listed analog category "a shop authenticated versus the shop stored as a session key."

### Likelihood Explanation
Reaching this requires only knowledge of one legitimately-signed webhook body/HMAC pair for the app's client secret (obtainable simply by installing the app on any shop and receiving one real webhook) — no privileged credentials, access token, or TLS interception is required. Replaying that body with a modified `Shop-Domain` header is trivial for an unprivileged internet user who controls the HTTP request reaching the endpoint.

### Recommendation
Bind the shop (and other Shopify headers that downstream code treats as trusted, e.g., `topic`, `webhook-id`) into the material that is verified, or explicitly document that `Request#shop`/`Request#topic` are **not** authenticated and must not be used for tenant/session lookup without additional verification (e.g., cross-checking against a known/installed shop list) before HMAC success is treated as proof of the webhook's origin and target tenant.

### Proof of Concept
```ruby
# Attacker has ONE legitimately-received webhook for their own shop:
raw_body = '{"id":123,"note":"hello"}' # exact bytes Shopify sent
valid_hmac_b64 = "..." # X-Shopify-Hmac-SHA256 value Shopify actually sent for raw_body

# Attacker now sends this exact body+HMAC to the app's webhook endpoint,
# but swaps the shop-domain header to a victim shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unauthenticated
  "x-shopify-webhook-id" => "whatever",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

ShopifyAPI::Utils::HmacValidator.validate(request) # => true, because HMAC only checks raw_body
request.shop # => "victim-shop.myshopify.com"  (fully attacker-controlled, unverified)
```
Any host code that does `if HmacValidator.validate(request); process_for_shop(request.shop, request.parsed_body); end` will attribute the attacker's own webhook payload to `victim-shop.myshopify.com` despite the HMAC never having authenticated that shop value.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
