### Title
`Webhooks::Request#shop` is derived from an unauthenticated header and is never covered by HMAC validation, enabling cross-tenant webhook attribution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `#shop` (and `#topic`, `#api_version`, `#webhook_id`) are read straight from caller-supplied headers via `shopify_header`. `Utils::HmacValidator.validate` (invoked from `Registry.process`) only verifies the HMAC over `to_signable_string`, so the shop attribution used to build `WebhookMetadata` is never bound to the cryptographic signature. The header-normalization step (`headers.to_h { |k, v| ... }`) additionally means that if two differently-cased/prefixed header keys collapse to the same normalized key, the last one wins silently, giving an attacker (or an intermediary) an extra lever over which value is picked — but this is a secondary aggravation of the same core binding gap, not a separate root cause.

### Finding Description
The broken binding: `request.shop` (`lib/shopify_api/webhooks/request.rb:21-23`, via `shopify_header`, lines 68-70) is claimed/assumed to equal "the shop that produced the HMAC-valid `raw_body`", but no code enforces `request.shop == shop_bound_to(hmac_signature)`.

Trace:
- `to_signable_string` returns `@raw_body` only: [1](#0-0) 
- `shop` is read from `@headers["shopify-shop-domain"] || @headers["x-shopify-shop-domain"]`, populated straight from the `headers:` argument with only cosmetic normalization: [2](#0-1) 
- `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares to `verifiable_query.hmac`, i.e., it authenticates the body bytes and the `hmac-sha256` header value only, never the shop or topic headers: [3](#0-2) 
- `Registry.process` validates the HMAC then immediately trusts `request.shop` (and `request.topic`) to build `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the shop header sits outside the signable string, HMAC success proves only "the body+secret combination is genuine," not "this body came from shop X." An attacker who operates their own development shop and installs the app there can register a real webhook subscription, receive a validly HMAC-signed callback from Shopify for their own shop, and then send that same `raw_body`+valid `hmac-sha256` to the app's webhook endpoint while substituting an arbitrary `Shopify-Shop-Domain`/`X-Shopify-Shop-Domain` header value naming a victim shop. `HmacValidator.validate` still returns `true` (it never inspects the shop header), and `Registry.process` hands the handler a `WebhookMetadata` claiming the victim shop, with a body the attacker fully controls the content and timing of.

The header-normalization collision described in the prompt (`.to_h` keeping the last of two keys that normalize to the same string, e.g., `HTTP_X_SHOPIFY_SHOP_DOMAIN` vs. a literal `shopify-shop-domain` key) is a real Ruby `Hash#to_h` behavior at `lib/shopify_api/webhooks/request.rb:48`, but it only matters if the host app's `headers:` hash already contains two differently-named keys that normalize identically — that duplication is a property of what the web server/Rack layer chose to put in the headers hash, not something this gem introduces on the wire. It does not add a new attack surface beyond the base finding: the base finding (shop header excluded from `to_signable_string`) is sufficient by itself, with no need for duplicate-header trickery, to achieve cross-tenant attribution once the attacker holds one validly-signed body+HMAC pair for their own shop.

No existing guard prevents this: `HmacValidator.validate` (above) only checks the body signature; there is no `ShopValidator.sanitize!`/domain-format check tying `request.shop` to the HMAC; `Context.setup?`/`private?`/`embedded?` and Sorbet typing only constrain configuration and static types, not this value binding.

### Impact Explanation
An app built on this gem that keys tenant-specific processing (data updates, redaction, notifications, etc.) off `WebhookMetadata#shop` will attribute an attacker-controlled webhook body to any shop domain string the attacker chooses in the header, despite a "valid" HMAC. This is a cross-tenant impact: one tenant's (the attacker's) genuinely-signed traffic can be relabeled as another tenant's (the victim's) webhook. This matches the Critical category — cross-tenant access / authentication-bypass-style trust of unauthenticated header data as verified/authenticated. It is repeatable against arbitrary victim shop domains for every request, limited only by the attacker's ability to obtain any valid signed body+HMAC pair (which they always can, from their own shop's webhooks).

### Likelihood Explanation
Preconditions: the host app must call `Webhooks::Request.new`/`Registry.process` as documented (this is the gem's only supported webhook-verification path), and must use `WebhookMetadata#shop` (or `request.shop`) for tenant attribution, which is the documented purpose of that field. The attacker needs no credentials: they can create their own development shop, install the app, and receive genuinely-signed webhooks for topics they can trigger themselves. Constructing the forged request (replaying body+HMAC with a swapped shop header) requires only the ability to send arbitrary HTTP headers, which any internet client has. This makes the attack cheap, fully attacker-controlled, and repeatable.

### Recommendation
Bind shop (and ideally topic) into the signed material, or otherwise cryptographically/independently verify the shop domain before trusting it:
- Include the shop domain (and other Shopify-controlled metadata) in `to_signable_string`, or
- After HMAC validation succeeds, independently verify the shop domain against a source that Shopify itself binds to the request (e.g., cross-check against the registered webhook's known shop when available, or require the app to independently confirm the shop via a signed channel such as an OAuth session token rather than trusting the plain header).
- Additionally, harden `initialize`'s header normalization to reject/error on duplicate keys that normalize to the same name rather than silently keeping the last one, to remove the secondary ambiguity lever.

### Proof of Concept
```ruby
# test/webhooks/registry_shop_binding_test.rb
require "test_helper"

class RegistryShopBindingTest < Test::Unit::TestCase
  def test_shop_header_is_not_bound_to_hmac
    body = '{"id":1}'
    secret = "secret"
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: secret, host_name: "app.com",
      scope: "read_products", is_embedded: true, api_version: "2023-10", is_private: false)

    valid_hmac = Base64.strict_encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, body)
    )

    # Attacker's own shop's genuinely-signed webhook, replayed with victim's shop header
    forged_headers = {
      "HTTP_X_SHOPIFY_TOPIC" => "orders/create",
      "HTTP_X_SHOPIFY_HMAC_SHA256" => valid_hmac,
      "HTTP_X_SHOPIFY_SHOP_DOMAIN" => "victim.myshopify.com", # attacker-chosen, unsigned
      "HTTP_X_SHOPIFY_API_VERSION" => "2023-10",
      "HTTP_X_SHOPIFY_WEBHOOK_ID" => "1",
    }

    request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

    assert ShopifyAPI::Utils::HmacValidator.validate(request), "HMAC should validate (it only covers the body)"
    assert_equal "victim.myshopify.com", request.shop,
      "shop is taken verbatim from an unauthenticated header despite HMAC success"
  end
end
```
This demonstrates that `HmacValidator.validate(request)` returns `true` while `request.shop` reflects an attacker-supplied, unsigned value — proving `request.shop` is trusted as authenticated data when it is not bound to the HMAC signature.

### Citations

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
