### Title
Webhook shop-domain header is not bound to the HMAC signature, enabling cross-tenant impersonation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Request#shop` (lib/shopify_api/webhooks/request.rb:20-23) reads the `shop-domain` header directly and is never cross-checked against anything cryptographic. `Request#to_signable_string` (lines 35-38) returns only `@raw_body`, and `HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb:12-22) computes the HMAC over that body alone using a single app-wide secret (`Context.api_secret_key`), which is the same secret for every shop that has installed the app. Because the secret and signed content are shop-agnostic, a body+HMAC pair legitimately obtained by an attacker for their own shop remains valid when replayed with a different `shop-domain` header.

### Finding Description
Binding claimed: "shop that authored/holds the secret validating this HMAC == shop field consumed by `WebhookMetadata` and the host app." Tracing the code shows this binding never existed to begin with, and is false both before and after the request is processed:

- `Request#hmac` and `Request#to_signable_string` only ever involve `@raw_body` — [1](#0-0) .
- `Request#shop` is a plain, unauthenticated header read — [2](#0-1) .
- `HmacValidator.validate_signature` computes `HMAC(secret, raw_body)` and compares it to the received signature using `Context.api_secret_key` (or the rotated `old_api_secret_key`) — [3](#0-2) . This secret is the app's single `client_secret`, shared across every shop that has the app installed (confirmed by its use throughout OAuth/JWT/session code, e.g. `lib/shopify_api/context.rb`), not a per-shop secret.
- `Registry.process` validates the HMAC, then builds `WebhookMetadata` directly from `request.shop` with no further check — [4](#0-3) .

Exploit flow: the attacker installs the app on their own development shop (legitimately permitted), triggers a `products/update` event on their own shop, and lets Shopify deliver a genuinely-signed webhook to them containing attacker-controlled product data with a valid `x-shopify-hmac-sha256`. The attacker then POSTs that same raw body and HMAC directly to the app's public webhook endpoint, changing only the `shop-domain` (or `x-shopify-shop-domain`) header to the victim's shop. Since the HMAC covers only the body and the same app secret validates every shop, `HmacValidator.validate` still returns `true`, `Registry.process` proceeds, and `WebhookHandler#handle` receives a `WebhookMetadata` whose `shop` is the victim's domain but whose `body` is entirely attacker-authored. No code path in `request.rb`, `registry.rb`, `hmac_validator.rb`, or `shop_validator.rb` re-derives or authenticates the shop from anything tied to the signature.

This mirrors the documented behavior of Shopify's own webhook HMAC scheme (sign only the body, with the app's shared secret) — the gem does not add any check binding the delivered `shop-domain` header to an actual install record or the signature, and the docs (`docs/usage/webhooks.md`) describe `Registry.process` as verifying "the request did indeed come from Shopify," which is misleading: it verifies the request came from *an* installation of *this app*, not from the specific shop named in the header.

### Impact Explanation
Any handler that trusts `WebhookMetadata#shop` for writes (e.g., inventory sync, order processing) can be made to attribute attacker-authored payloads to an arbitrary victim shop that has the app installed, as long as the topic is one the attacker can also trigger on their own store. This is cross-tenant data injection — Critical impact per the given severity taxonomy — and is repeatable against any shop running the same app, for any topic the attacker can generate on their own store (e.g. `products/update`, `orders/create` on their own test orders, etc.), limited only by which fields the attacker can control within their own shop's resources.

### Likelihood Explanation
Preconditions are all attacker-obtainable without secrets: a free/development Shopify shop, installing the target app on it (many apps are publicly installable), and knowledge/discoverability of the app's webhook callback path (commonly documented or guessable, e.g. `/webhooks`, `/callback/<topic>`). No TLS interception, no leaked credentials, and no privileged access are required — only the ability to install the app and to send a direct HTTP POST to its public endpoint, both explicitly within the defined attacker capabilities.

### Recommendation
Do not treat the `shop-domain` header as authenticated by the HMAC. Options: (1) incorporate the shop domain into the signable string/HMAC scheme if this can be changed at the platform level (not possible unilaterally for this gem, since Shopify controls the signing), or (2) require host apps (and provide gem-level enforcement) to cross-check `request.shop` against records of shops that have an active, session-confirmed installation and an active webhook subscription id (`request.webhook_id`) known to belong to that shop before trusting `WebhookMetadata`. At minimum, update documentation to make clear that HMAC validation only proves the payload originated from an install of this specific app, not that it originated from the named shop, and encourage per-shop reconciliation before performing writes.

### Proof of Concept
```ruby
# test/webhooks/cross_shop_forgery_test.rb
require_relative "../test_helper"

class CrossShopForgeryTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", host_name: "host",
      api_version: "2024-01", is_embedded: true, is_private: false,
      user_agent_prefix: "test",
    )
    ShopifyAPI::Webhooks::Registry.clear
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "products/update", delivery_method: :http, path: "callback",
      handler: FakeHandler,
    )
  end

  class FakeHandler
    class << self
      attr_accessor :last_metadata
      def handle(data:)
        self.last_metadata = data
      end
    end
    extend ShopifyAPI::Webhooks::WebhookHandler
  end

  def test_hmac_does_not_bind_shop_domain
    raw_body = '{"id":1,"title":"attacker product"}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest("sha256", "secret", raw_body)
    )

    attacker_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "shopify-topic" => "products/update",
        "shopify-hmac-sha256" => hmac,
        "shopify-shop-domain" => "attacker-shop.myshopify.com",
      },
    )

    victim_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "shopify-topic" => "products/update",
        "shopify-hmac-sha256" => hmac,
        "shopify-shop-domain" => "victim-shop.myshopify.com",
      },
    )

    assert(ShopifyAPI::Utils::HmacValidator.validate(attacker_request))
    assert(ShopifyAPI::Utils::HmacValidator.validate(victim_request))

    ShopifyAPI::Webhooks::Registry.process(victim_request)
    assert_equal("victim-shop.myshopify.com", FakeHandler.last_metadata.shop)
    assert_equal("attacker product", FakeHandler.last_metadata.body["title"])
  end
end
```
This demonstrates: the same `raw_body`/`hmac` pair validates for two different `shop-domain` values, and `Registry.process` happily attributes attacker-authored body content to `"victim-shop.myshopify.com"` — confirming the claimed binding is false.

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
