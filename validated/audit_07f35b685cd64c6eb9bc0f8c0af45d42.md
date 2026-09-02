### Title
`Webhooks::Request#shop` trusts the unsigned `shopify-shop-domain` header, allowing cross-tenant shop-identity spoofing in replayed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Utils::HmacValidator.validate` only verifies the HMAC over `to_signable_string`, which for `Webhooks::Request` is `@raw_body` alone [1](#0-0) . None of `topic`, `shop`, `api_version`, or `webhook_id` — all pulled unsigned straight from headers via `shopify_header` [2](#0-1)  — are included in the signable string or otherwise bound to the HMAC.

### Finding Description
The claimed invariant is: `WebhookMetadata#shop` (delivered to the host app's handler) should equal the shop identity that Shopify's HMAC signature actually authenticates. In reality:

- `Registry.process` computes `Utils::HmacValidator.validate(request)` [3](#0-2) , which calls `validate_signature`, comparing `compute_signature(verifiable_query.to_signable_string, secret)` against `verifiable_query.hmac` [4](#0-3) .
- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) ; the shop-domain, topic, webhook-id, and api-version headers are never part of that signed string.
- `Request#shop` simply casts the raw `shopify-shop-domain`/`x-shopify-shop-domain` header value to `String` with no verification [5](#0-4) .
- `Registry.process` then builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` and passes it straight to the host app's handler [6](#0-5) , and the docs confirm apps are expected to key business logic off `data.shop` (e.g. `shop_domain: data.shop`) [7](#0-6) .

Because `api_secret_key` is shared across every shop that installs a given app, an attacker who installs their own app on a shop they control can receive one legitimately-signed webhook body (any topic they can trigger). They can then POST that exact `raw_body` and its valid `x-shopify-hmac-sha256` value to the app's real webhook endpoint, but with the `x-shopify-shop-domain` header rewritten to the victim merchant's domain. `Utils::HmacValidator.validate` still passes (HMAC only checks body+secret, both unchanged), so `Registry.process` accepts the forgery and calls the handler with `WebhookMetadata#shop` equal to the attacker-chosen victim domain. The "SINGLE IDENTITY" invariant the question asks about is broken: the identity Shopify's signature authenticates (the sender/body-integrity) and the identity the host app is told to act on (`data.shop`) diverge, because the header is not part of the signed material at all.

None of the existing guards catch this: `HmacValidator.validate` never inspects `shop`/`topic`/`webhook_id` [8](#0-7) ; `Request#initialize` only checks header *presence*, not header authenticity [9](#0-8) ; and Sorbet's `T.cast` only enforces the Ruby type (String), not provenance.

### Impact Explanation
If a host app trusts `data.shop` to decide which merchant's stored access token/session to use for follow-up Admin API calls (as the documented usage pattern implies), an attacker can trigger the app to perform actions against, or leak data about, a victim merchant's shop using the app's own credentials for that shop — a cross-tenant confusion. This matches the "cross-tenant access" Critical category in scope. It is repeatable: any attacker who can install the app on a self-controlled development shop and trigger any webhook topic can replay that body against arbitrary target shop domains, limited only to the fields present in that specific webhook's `body` (attacker does not control body content arbitrarily — it is a real webhook payload from their own shop) but with an attacker-chosen `shop` value.

### Likelihood Explanation
Preconditions: the app must (a) actually branch logic on `WebhookMetadata#shop` (documented as the intended use) and (b) not additionally re-verify the shop against another authenticated source (e.g., the URL path or a mapping from webhook_id back to the subscription). Attacker cost is low — creating a dev store, installing the target app, and triggering one webhook event is within the documented unprivileged-attacker capability set. No secrets are needed since HMAC coverage of `raw_body` is unaffected by the header swap.

### Recommendation
Do not treat `shop`, `topic`, `webhook_id`, or `api_version` headers as trusted metadata based solely on HMAC-body validation. Either (a) include these fields in the signable string so they are cryptographically bound to the signature (matching what Shopify actually signs, if it does — this should be confirmed against Shopify's current webhook HMAC spec), or (b) require host apps to cross-check `WebhookMetadata#shop` against an independent authenticated record (e.g., the webhook subscription id ⇄ shop mapping obtained during registration) before trusting it for tenant-scoped operations, and document this requirement prominently.

### Proof of Concept
```ruby
# test/webhooks/registry_shop_spoof_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Webhooks
    class ShopSpoofTest < Test::Unit::TestCase
      def test_shop_header_not_covered_by_hmac
        body = "{}"
        hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
        encoded_hmac = Base64.encode64(hmac)

        legit_headers = {
          "x-shopify-topic" => "orders/create",
          "x-shopify-hmac-sha256" => encoded_hmac,
          "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
        }
        spoofed_headers = legit_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

        legit_request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: legit_headers)
        spoofed_request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: spoofed_headers)

        # Binding under test: HMAC validity does not depend on / bind the shop header
        assert(ShopifyAPI::Utils::HmacValidator.validate(legit_request))
        assert(ShopifyAPI::Utils::HmacValidator.validate(spoofed_request))
        refute_equal(legit_request.shop, spoofed_request.shop)

        received_shop = nil
        handler = Class.new do
          extend ShopifyAPI::Webhooks::WebhookHandler
          define_singleton_method(:handle) { |data:| received_shop = data.shop }
        end
        ShopifyAPI::Webhooks::Registry.add_registration(topic: "orders/create", delivery_method: :http, handler: handler, path: "cb")

        ShopifyAPI::Webhooks::Registry.process(spoofed_request)
        assert_equal("victim-shop.myshopify.com", received_shop) # attacker-controlled identity accepted as authentic
      end
    end
  end
end
```
This demonstrates that a body signed under the attacker's own shop's install of the app validates identically regardless of the `shop-domain` header value, and `Registry.process` propagates the attacker-chosen shop into `WebhookMetadata#shop` unchanged.

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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
