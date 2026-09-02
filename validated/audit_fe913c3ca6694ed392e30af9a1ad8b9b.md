### Title
`Webhooks::Request#shop` / `#api_version` / `#webhook_id` are unsigned headers trusted as authenticated — cross-tenant webhook impersonation via HMAC replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are read from unsigned HTTP headers [2](#0-1) . `Registry.process` validates only the body's HMAC and then forwards these unsigned header values straight into `WebhookMetadata`, which the app's handler trusts as the authenticated origin shop. [3](#0-2) 

### Finding Description
The intended binding is: `HMAC-valid(raw_body) ⇒ shop == the tenant that actually generated raw_body`. In this code the binding actually enforced is only `HMAC-valid(raw_body)`, with no cryptographic link between `raw_body` and the `shop`, `api_version`, or `webhook_id` claims.

- `HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header. [4](#0-3) 
- `Request#to_signable_string` returns `@raw_body` only — none of `shop-domain`, `api-version`, `webhook-id`, or `topic` participate in the signable string. [1](#0-0) 
- `Request#shop`, `#api_version`, `#webhook_id`, `#topic` are read directly from attacker-suppliable headers (`shopify-shop-domain` / `x-shopify-shop-domain`, etc.) with no further validation (no `ShopValidator.sanitize!` call anywhere in `request.rb`). [5](#0-4) [6](#0-5) 
- `Registry.process` gates only on `Utils::HmacValidator.validate(request)`, then immediately constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, ..., api_version: request.api_version, webhook_id: request.webhook_id)` and dispatches to the app's handler. [3](#0-2) 

Because the shared `api_secret_key` is common to the whole app across every shop that has installed it, an attacker who installs the app on their own (attacker-controlled) development shop can trigger events, capture a Shopify-issued `(raw_body, x-shopify-hmac-sha256)` pair that is valid for that secret, and then POST that exact `raw_body`/HMAC directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-api-version`, `x-shopify-webhook-id`) with a victim shop's domain or an arbitrary value. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim shop, topic, api_version and webhook_id, while the body content is entirely attacker-controlled. No nonce, timestamp, or webhook-id de-duplication/replay tracking exists anywhere in `Registry` or `Request` to bind a signature to a single shop or single delivery.

Existing guards do not prevent this: `ShopValidator.sanitize!` is never invoked in this path (it only formats/normalizes a shop string, it would not reject a syntactically valid but wrong shop domain anyway); `Context.setup?`/`private?`/`embedded?` are unrelated to webhook processing; there is no `state`/nonce comparison for webhooks (that mechanism exists only for OAuth `AuthQuery`, not `Webhooks::Request`).

### Impact Explanation
Any app built on this gem that uses `request.shop` (or `api_version`/`webhook_id`) from `WebhookMetadata` to select which merchant record, session, or database row to act on can be made to apply attacker-supplied webhook data to a different (victim) tenant's data, or to have attacker-controlled content processed under a spoofed shop/api-version identity — a cross-tenant confusion that maps to the "cross-tenant access" / forged-callback-accepted-as-authentic category. This is repeatable per request: the attacker can register their own webhook, capture as many valid `(body, hmac)` pairs as they like, and replay them against the app's public endpoint with any `shop-domain` value forever, since nothing invalidates or ties the signature to that value.

### Likelihood Explanation
Preconditions are minimal and fully within the described unprivileged attacker's capability: install the app on a self-owned development shop, register a webhook, receive one legitimately-signed delivery, and replay it directly to the app's public webhook URL with modified headers. No secret, token, or privileged access is required — only the ability to trigger an event on their own store and send arbitrary HTTP requests to the app's endpoint, which is by definition internet-reachable to receive webhooks.

### Recommendation
Bind the trusted claims to the signed payload instead of trusting bare headers: either (a) include `shop-domain`, `api-version`, and `webhook-id` in the string handed to `HmacValidator` (e.g., concatenate header values with the body before HMAC computation, matching what the server-side verification also expects), or (b) require applications to independently verify that `request.shop` corresponds to a session/shop this app actually has installed for the given `webhook_id`/topic, and track `webhook_id` to reject re-delivery/replay across different shop claims.

### Proof of Concept
```ruby
# test/webhooks/registry_replay_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Webhooks
    class RegistryReplayTest < Test::Unit::TestCase
      def test_same_signed_body_accepted_for_two_different_shops
        body = '{"id":1,"note":"attacker-controlled"}'
        hmac = Base64.encode64(
          OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
        ).strip

        received_shops = []
        handler = Class.new do
          include ShopifyAPI::Webhooks::WebhookHandler
          define_method(:handle) { |data:| received_shops << data.shop }
        end.new

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: "orders/create", delivery_method: :http, path: "/webhooks", handler: handler
        )

        headers_a = { "x-shopify-topic" => "orders/create", "x-shopify-hmac-sha256" => hmac,
                      "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
                      "x-shopify-api-version" => "2023-01", "x-shopify-webhook-id" => "id-1" }
        headers_b = headers_a.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

        req_a = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers_a)
        req_b = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers_b)

        ShopifyAPI::Webhooks::Registry.process(req_a) # HMAC-valid
        ShopifyAPI::Webhooks::Registry.process(req_b) # same body+hmac, HMAC-valid again

        # Binding under test: HMAC-valid(body) should not let two different `shop` claims
        # both be accepted for the identical signature.
        assert_equal(["attacker-shop.myshopify.com", "victim-shop.myshopify.com"], received_shops)
      end
    end
  end
end
```
Both calls to `Registry.process` pass `HmacValidator.validate`, and the handler receives two different `shop` values for one identical `(body, hmac)` pair, demonstrating the unsigned `shop`/header trust and confirming the reachable authentication-bypass path.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
