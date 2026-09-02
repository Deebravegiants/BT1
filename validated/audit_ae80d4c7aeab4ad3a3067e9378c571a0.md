### Title
`shop`/`topic`/`webhook_id` headers are unauthenticated because `to_signable_string` covers only `raw_body` - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` verifies nothing about the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers. [1](#0-0)  `Registry.process` nonetheless trusts `request.shop`, `request.topic`, and `request.webhook_id` — sourced straight from those unsigned headers — to build `WebhookMetadata` handed to the app's handler. [2](#0-1)  Any client that once obtains a legitimately-signed `(raw_body, hmac)` pair for its own shop can replay that exact body/HMAC against the app's public webhook endpoint with a different `x-shopify-shop-domain` (or `x-shopify-webhook-id`/`x-shopify-topic`) header value, and `HmacValidator.validate` will still pass.

### Finding Description
The binding under test is: *every value the app acts on for a webhook must be inside the string `HmacValidator` verifies via `to_signable_string`*. That binding is broken. `to_signable_string` returns `@raw_body` only: [1](#0-0) 
`shop`, `topic`, `webhook_id`, and `api_version` are all read from `@headers`, not from `@raw_body`: [3](#0-2) 
`HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against the decoded `hmac-sha256` header — it never touches any other header: [4](#0-3) 
`Registry.process` calls `HmacValidator.validate(request)` and, once it passes, forwards `request.shop`, `request.topic`, and `request.webhook_id` unchecked into `WebhookMetadata`, which is the only tenant/topic identity the app's `handler.handle` receives: [2](#0-1) [5](#0-4) 

Exploit flow: an attacker registers a webhook on their own development shop (a shop they control, per the threat model), receives a genuinely Shopify-signed callback (`raw_body`, `x-shopify-hmac-sha256`, plus headers including their own `x-shopify-shop-domain`), and simply POSTs that identical `raw_body` + `hmac-sha256` header again to the app's public webhook endpoint, replacing `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) with a victim shop's domain / a different topic / a different webhook id. `HmacValidator.validate` recomputes the same HMAC over the same `raw_body` and it matches, because the signature check is agnostic to headers. `Registry.process` then invokes the handler with `WebhookMetadata` claiming the payload is for the victim shop (or a different topic/id), even though Shopify never sent that combination.

The base64url (`-`/`_`) framing in the question is a red herring for actual signature forgery: `Base64.decode64` (`unpack1("m")`) is lenient about invalid alphabet characters but this only degrades the decoded bytes used for `secure_compare` — it does not let an attacker produce a matching digest without the secret, so it cannot forge a signature on its own. The genuine, demonstrable divergence is the header/body signature-coverage gap described above, not the base64 variant handling.

No other guard closes this gap: `ShopValdiator.sanitize!`, JWT `aud`/`iss` checks, and `Context.setup?` are unrelated to webhook processing; nothing in `Registry.process` cross-checks `request.shop`/`request.topic`/`request.webhook_id` against anything derived from `raw_body` or against Shopify's HMAC-covered content.

### Impact Explanation
Because tenant identity (`shop`) and delivery identity (`topic`, `webhook_id`) live entirely outside the signed content, a signature valid for shop A's webhook is also "valid" (per this gem's check) when replayed with headers claiming it is for shop B, a different topic, or a different webhook id. If the app's handler uses `data.shop` to select which merchant's records to update (the documented usage pattern shown in `docs/usage/webhooks.md`, e.g. `perform_later(shop_domain: data.shop, webhook: data.body)`), an attacker-controlled shop-domain value lets one tenant's signed payload be attributed to another tenant, i.e., cross-tenant data confusion — this matches the "cross-tenant access" Critical category. The attacker only ever needs a signature from their own legitimately-owned shop's webhook traffic (which they can generate repeatedly and freely as the owner of a dev shop), and can replay it against arbitrarily many victim shop-domain values, so the attack is fully repeatable.

### Likelihood Explanation
Preconditions: the app must (a) expose the webhook-processing route publicly (true by design — "the app's public webhook endpoint"), (b) use `request.shop`/`request.topic`/`request.webhook_id` as the trusted identity fields when acting on the payload, which is exactly the documented handler pattern in `docs/usage/webhooks.md`. Attacker cost is low: register a dev shop, trigger any webhook topic they've subscribed to, capture the resulting `raw_body` + `hmac-sha256`, then replay it directly to the app's endpoint with a forged `x-shopify-shop-domain`/`x-shopify-topic`/`x-shopify-webhook-id`. No secret, no TLS interception, and no privileged access are required — only the ability to send arbitrary HTTP POSTs to a route that is public by definition. This is fully repeatable against any number of target shop-domain strings.

### Recommendation
Bind the identity headers into the signed content that `HmacValidator` verifies, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the verified body before they are trusted. Concretely, change `Registry.process`/`Request` so that after `HmacValidator.validate` succeeds, the app is required (and the gem enforces) that `shop`/`topic`/`webhook_id` are cross-checked against values embedded in, or derivable from, the verified `raw_body` (or against a known-registered webhook subscription/shop record), rather than trusting the raw headers verbatim. At minimum, document prominently that `request.shop`/`topic`/`webhook_id` are NOT covered by the HMAC and must not be used as the sole tenant-selection key without additional verification (e.g., confirming the shop has an active, verified session/install record) — and add delivery-id-based idempotency/replay tracking as defense in depth.

### Proof of Concept
```ruby
# test/webhooks/cross_tenant_replay_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Webhooks
    class CrossTenantReplayTest < Minitest::Test
      def setup
        ShopifyAPI::Context.setup(
          api_key: "key", api_secret_key: "secret_key", api_version: "2024-01",
          host_name: "app.com", scope: "read_products", is_embedded: true,
          is_private: false, session_storage: nil,
        )
        received = []
        handler = Class.new do
          extend ShopifyAPI::Webhooks::WebhookHandler
          define_singleton_method(:handle) { |data:| received << data.shop }
        end
        ShopifyAPI::Webhooks::Registry.clear
        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: "orders/create", delivery_method: :http, path: "cb", handler: handler,
        )
        @received = received
      end

      def test_same_signature_accepted_for_two_different_shops
        raw_body = '{"id":1}'
        hmac = Base64.encode64(
          OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret_key", raw_body),
        ).strip

        headers_shop_a = {
          "x-shopify-topic" => "orders/create",
          "x-shopify-hmac-sha256" => hmac,
          "x-shopify-shop-domain" => "shop-a.myshopify.com",
          "x-shopify-webhook-id" => "id-1",
          "x-shopify-api-version" => "2024-01",
        }
        headers_shop_b = headers_shop_a.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

        ShopifyAPI::Webhooks::Registry.process(
          ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers_shop_a),
        )
        ShopifyAPI::Webhooks::Registry.process(
          ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers_shop_b),
        )

        # Same body + same HMAC accepted for two distinct shops -> signature does not bind shop identity
        assert_equal(["shop-a.myshopify.com", "victim-shop.myshopify.com"], @received)
      end
    end
  end
end
```
Both calls to `HmacValidator.validate` succeed (same `raw_body`/`hmac`), yet `@received` ends up containing two different shop domains for one signature, proving `shop` (and equally `topic`/`webhook_id`) is not covered by the signature check performed in `lib/shopify_api/utils/hmac_validator.rb` and `lib/shopify_api/webhooks/request.rb`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
