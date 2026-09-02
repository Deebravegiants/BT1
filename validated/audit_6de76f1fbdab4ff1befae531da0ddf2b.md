Confirmed: `ShopValidator` is never referenced anywhere in `lib/shopify_api/webhooks/` (only used in OAuth/token-exchange/client-credentials/storefront code paths), and `WebhookMetadata` in `lib/shopify_api/webhooks/registry.rb` is built directly from `request.shop` with no validation.### Title
Webhook HMAC does not bind `shopify-shop-domain`, allowing cross-tenant shop-identity forgery via header swap - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` verifies the HMAC solely against that body using the app's single, shop-independent `api_secret_key`. Neither `Request#initialize` nor `Registry.process` ever calls `Utils::ShopValidator` or otherwise ties the `shopify-shop-domain` header to the signature, so an attacker who possesses one validly-signed `(raw_body, hmac)` pair (obtainable by installing the app on their own shop and receiving a real webhook) can replay it with an arbitrary `shopify-shop-domain` value and have it accepted as belonging to any victim shop.

### Finding Description
The binding the host app relies on is:
`shop_value_the_hmac_actually_authenticates == shop_value_used_as_tenant_key`

Tracing the code:
- `Request#initialize` (`lib/shopify_api/webhooks/request.rb:45-63`) only checks header *presence* for `topic`, `hmac-sha256`, and `shop-domain` [1](#0-0) . It never validates the shop value.
- `Request#to_signable_string` returns `@raw_body` only [2](#0-1) . The `shop-domain`, `topic`, and `webhook-id` headers are excluded from the signed content.
- `Utils::HmacValidator.validate` computes `HMAC(api_secret_key, to_signable_string)` and compares it against the `hmac` header [3](#0-2) . `api_secret_key` is a single, app-wide secret, not scoped per shop.
- `Registry.process` calls `HmacValidator.validate(request)` and, on success, builds `WebhookMetadata` directly from `request.shop` with no further check [4](#0-3) .
- `Utils::ShopValidator.sanitize!`/`sanitize_shop_domain` exist and are used elsewhere (OAuth, token exchange, client credentials, storefront client) [5](#0-4)  but are never invoked from `lib/shopify_api/webhooks/`, confirmed by searching the codebase for `ShopValidator` usage — no hits in the webhooks directory.
- `WebhookMetadata` (`lib/shopify_api/webhooks/webhook_handler.rb:6-12`) is a plain struct with a `shop: String` field with no validation logic of its own [6](#0-5) , matching the documented pattern in `docs/usage/webhooks.md` where `handler.handle(data:)` trusts `data.shop` as the tenant key.

Attacker flow:
1. Attacker installs the app on their own shop, registers a webhook, and receives a legitimately-signed callback: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, `x-shopify-shop-domain = attacker-shop.myshopify.com`.
2. Attacker sends a new HTTP request directly to the app's public webhook endpoint with the *same* `raw_body = B` and the *same* `hmac` header, but sets `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and/or a topic they want).
3. `Request.new` succeeds (all three headers present). `HmacValidator.validate` succeeds because it only checks `HMAC(secret, B)`, which is unchanged. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`.
4. Any host-app logic that uses `data.shop` as a tenant key (exactly as documented) now processes attacker-controlled body content under the victim's tenant identity.

No existing guard prevents this: `HmacValidator.validate` only proves knowledge of the shared secret over the body, not authorship of the shop-domain header; `ShopValidator.sanitize!` is not called anywhere in the webhook path; there is no per-shop signing key, no `state` comparison, and no session/JWT check in play for webhooks. This differs qualitatively from Shopify's own topic/shop binding assumptions, and the gem provides no compensating check even though `ShopValidator` is available and used for exactly this kind of domain trust decision elsewhere in the same codebase.

### Impact Explanation
An external, unprivileged attacker can make the host application believe that Shopify-supplied event data (body content of a webhook, e.g. `orders/create`, `customers/data_request`, etc., which for many topics contains attacker-influenceable data since it originates from actions the attacker performs on their own shop) belongs to an arbitrary victim shop. Any host app that keys work, billing, data storage, or side effects off `WebhookMetadata#shop` (the documented and only sanctioned usage) can have its per-tenant data or behavior corrupted or read/written under the wrong tenant. This is repeatable against arbitrary victim shop domains for every topic the attacker can register and receive on their own shop, and is not limited to a single request. This matches the "Critical — cross-tenant access" impact category: a value that was never authenticated (the shop-domain header) is trusted as the authenticated tenant identity.

### Likelihood Explanation
Preconditions are modest and fully within the described attacker capability: the attacker only needs to (a) install the app on a shop they control (any developer/attacker can do this), (b) register at least one webhook topic and receive one legitimately signed delivery, and (c) know or guess the target's `shop-domain` value (typically a public, guessable `*.myshopify.com` handle). No secrets, tokens, or privileged access are required. The app's webhook endpoint must be reachable directly (true for any HTTP-based webhook receiver, which is the documented integration pattern). This makes the attack cheap, reliable, and repeatable across many victim shops without needing a new signed payload per victim — the same captured `(body, hmac)` pair can be replayed with different shop-domain values.

### Recommendation
Bind the shop identity to the HMAC-verified signable content, or independently authenticate the shop-domain header before trusting it as a tenant key:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in `Request#to_signable_string` so the HMAC covers the full tuple the app relies on, or
- At minimum, call `Utils::ShopValidator.sanitize!(request.shop)` in `Registry.process` (or in `Request#initialize`) and reconcile it against any shop-level state the app maintains (e.g., verify the shop is one for which the app previously completed OAuth/has an active webhook registration) before constructing `WebhookMetadata`.
- Document clearly that `WebhookMetadata#shop` must not be trusted as an authenticated tenant key unless such additional binding is performed.

### Proof of Concept
```ruby
# test/webhooks/shop_domain_forgery_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Webhooks
    class ShopDomainForgeryTest < Test::Unit::TestCase
      def setup
        super
        @body = "{}"
        @real_hmac = Base64.encode64(
          OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, @body),
        )
      end

      def test_hmac_still_validates_after_shop_domain_is_swapped
        # Attacker captures a legitimately-signed webhook for their own shop
        attacker_headers = {
          "x-shopify-topic" => "orders/create",
          "x-shopify-hmac-sha256" => @real_hmac,
          "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
        }
        attacker_request = ShopifyAPI::Webhooks::Request.new(raw_body: @body, headers: attacker_headers)
        assert(ShopifyAPI::Utils::HmacValidator.validate(attacker_request))

        # Attacker replays same body+hmac but swaps shop-domain to victim
        forged_headers = attacker_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")
        forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: @body, headers: forged_headers)

        # Binding under test: shop the HMAC authenticates (attacker-shop) vs
        # shop used as tenant key (victim-shop) -- should NOT both be accepted.
        assert(
          ShopifyAPI::Utils::HmacValidator.validate(forged_request),
          "HMAC validation passes even though shop-domain was swapped to an unrelated shop",
        )
        assert_equal("victim-shop.myshopify.com", forged_request.shop)

        # Demonstrate Registry.process trusts the forged shop as tenant key
        handler_shop = nil
        handler = TestHelpers::FakeWebhookHandler.new(->(data) { handler_shop = data.shop })
        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: "orders/create", path: "path", delivery_method: :http, handler: handler,
        )
        ShopifyAPI::Webhooks::Registry.process(forged_request)

        assert_equal("victim-shop.myshopify.com", handler_shop,
          "Registry.process delivered attacker's body under victim's tenant identity")
      end
    end
  end
end
```
This test requires no live shop, no WebMock network calls, and no app secret beyond the test fixture's `ShopifyAPI::Context.api_secret_key` (which the attacker in the threat model does not need to know — they only need one legitimately-delivered `(body, hmac)` pair from their own installation, which this test simulates by computing the HMAC the same way Shopify would for the attacker's own shop).

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L50-59)
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L50-64)
```ruby
        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
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
