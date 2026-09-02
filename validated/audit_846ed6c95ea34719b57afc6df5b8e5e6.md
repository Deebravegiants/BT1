### Title
`Registry.process` accepts a validly-signed webhook body with attacker-relabeled `topic` and `shop` headers, letting one attacker's genuine webhook impersonate any shop/topic - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
The webhook HMAC is computed and verified only over the raw request body (`Request#to_signable_string` returns `@raw_body`) [1](#0-0) , while `topic` and `shop` are read directly from unauthenticated HTTP headers (`shopify-topic`, `shopify-shop-domain`) [2](#0-1) . `Registry.process` validates the HMAC and then blindly trusts `request.topic` and `request.shop` to build `WebhookMetadata` dispatched to the handler [3](#0-2) . Since the signature never covers these headers, any attacker who legitimately received one genuinely signed webhook body (e.g. for their own dev shop) can replay that same body+HMAC to the app's public webhook endpoint with arbitrary `shopify-topic` / `shopify-shop-domain` headers, and the gem will accept it.

### Finding Description
The binding the gem is supposed to enforce is:
`(topic, shop)` authenticated by HMAC over `@raw_body` == `(topic, shop)` delivered to `handler.handle(data:)`.

Tracing the code:
- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares against `verifiable_query.hmac` [4](#0-3) .
- `Webhooks::Request#to_signable_string` returns only `@raw_body` — the signable string never includes the topic or shop headers [1](#0-0) .
- `Request#topic` and `Request#shop` are pulled straight from the (attacker-controlled, unauthenticated) HTTP headers `shopify-topic`/`x-shopify-topic` and `shopify-shop-domain`/`x-shopify-shop-domain` with no cross-check against the body or against any known/installed-shop list [2](#0-1) .
- `Registry.process` raises only if the HMAC is invalid, then looks up the handler by `request.topic` and constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, handing attacker-controlled `topic`/`shop` straight to the handler [3](#0-2) .

Because the two sides of the equality are computed from disjoint sources (HMAC over body vs. plain headers for topic/shop), they can diverge freely: the HMAC only proves "this body was produced by someone holding `api_secret_key`" — it proves nothing about which topic or which shop that body belongs to.

Exploit flow:
1. Attacker creates their own development shop and installs the target app, registering their own endpoint or simply observing the app's single shared webhook endpoint URL (apps typically use one fixed callback URL for all shops/topics).
2. Attacker receives one legitimate webhook delivery for their own shop/topic — a raw body plus its `X-Shopify-Hmac-SHA256` value, both genuinely computed by Shopify using `api_secret_key`.
3. Attacker sends a new HTTP POST directly to the app's public webhook endpoint, reusing the exact same raw body and `X-Shopify-Hmac-SHA256` header (so HMAC validation passes), but sets `X-Shopify-Topic` and `X-Shopify-Shop-Domain` to any topic/shop of their choosing (e.g. a mandatory topic like `customers/redact`, or any shop domain string).
4. `HmacValidator.validate` succeeds because it only checks `@raw_body` against the reused HMAC.
5. `Registry.process` dispatches to whatever handler is registered for the attacker-chosen topic, with `WebhookMetadata#shop` set to the attacker-chosen shop string.

No existing guard blocks this: `HmacValidator.validate` only authenticates the body; there is no `ShopValidator.sanitize!` call on `request.shop` in this path, no comparison against a list of installed shops, and no inclusion of headers in the signable string.

### Impact Explanation
Any handler registered via `Registry.add_registration` can be invoked with a completely attacker-chosen `shop` value and (for any topic the app has registered a handler for) an attacker-chosen `topic`, while the handler code has no way to distinguish this from a real Shopify-originated webhook, since it received a validly-verified HMAC. If handler logic keys any per-tenant behavior (e.g. deleting data, marking a shop uninstalled, triggering GDPR redaction flows, updating shop-scoped records) off `WebhookMetadata.shop`/`topic`, an attacker can trigger that logic against **any shop string**, including victim shops they have no relationship with — this is cross-tenant impersonation of arbitrary shops for arbitrary registered topics, repeatable indefinitely from a single captured signed body (the same body/HMAC pair can be replayed with different header combinations).

### Likelihood Explanation
Preconditions are minimal and fully within the stated attacker capabilities: the attacker only needs to install the target app on their own shop (or otherwise cause one legitimate webhook to be sent to them), capture the raw body and HMAC header of that delivery, and send a direct HTTP request to the app's public webhook endpoint with forged `shopify-topic`/`shopify-shop-domain` headers. No secrets, credentials, or privileged access are required. This is a low-cost, reliably repeatable attack against any app that uses `ShopifyAPI::Webhooks::Registry.process` as documented.

### Recommendation
Include the `topic` and `shop` header values (and ideally `webhook_id`/timestamp) in the HMAC-signable string, or otherwise cryptographically bind them to the verified body before trusting them, and/or validate `request.shop` against the set of shops actually installed/known to the app (via `ShopValidator.sanitize!` plus a session/store lookup) before dispatching to the handler.

### Proof of Concept
```ruby
# test/webhooks/registry_forged_topic_shop_test.rb
require "test_helper"

class RegistryForgedTopicShopTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", host_name: "example.com",
      scope: "read_products", is_private: false, api_version: "2022-01"
    )
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_attacker_can_relabel_topic_and_shop_with_one_valid_hmac
    handled = nil
    handler = Class.new do
      define_method(:handle) { |data:| handled = data }
    end.new

    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "customers/redact", delivery_method: :http, path: "/webhooks", handler: handler
    )

    raw_body = '{"id":1}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest("sha256", "secret", raw_body)
    ).strip

    # Legit HMAC, but attacker-chosen topic/shop headers
    forged_headers = {
      "x-shopify-hmac-sha256" => hmac,
      "x-shopify-topic" => "customers/redact",
      "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker never owned this shop
      "x-shopify-api-version" => "2022-01",
      "x-shopify-webhook-id" => "attacker-chosen-id",
    }

    request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

    ShopifyAPI::Webhooks::Registry.process(request)

    # Handler receives attacker-controlled shop despite the app never having a relationship with it
    assert_equal "victim-shop.myshopify.com", handled.shop
    assert_equal "customers/redact", handled.topic
  end
end
```
This test asserts `Registry.process` succeeds and dispatches attacker-chosen `WebhookMetadata#shop`/`#topic` off a single genuine HMAC over the body, confirming the broken binding.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/webhooks/registry.rb (L189-199)
```ruby
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
