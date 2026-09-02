### Title
Webhook HMAC signature does not bind `shop-domain` header to raw body content, allowing cross-tenant data confusion - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`Utils::HmacValidator.validate` only verifies the HMAC over `Request#to_signable_string`, which is exactly `@raw_body`. The `shop-domain` header, read by `Request#shop`, is never part of the signed data. `Registry.process` builds `WebhookMetadata` from `request.shop` (unsigned header) and `request.parsed_body` (signed body) independently, with no check that the body actually pertains to the asserted shop, so a valid signature on one shop's body can be replayed with an arbitrary `shop-domain` header.

### Finding Description
The binding this gem must preserve is:
`shop that request.parsed_body's content pertains to == request.shop used for authorization decisions`

Tracing the code:
- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) .
- `Request#shop` reads the `shopify-shop-domain`/`x-shopify-shop-domain` header directly, with no relation to the body or the HMAC [2](#0-1) .
- `HmacValidator.validate_signature` computes the signature purely over `verifiable_query.to_signable_string` (i.e., `@raw_body`) and compares it to the `hmac` header value; the `shop` header is never fed into `compute_signature` [3](#0-2) .
- `Registry.process` validates only the HMAC, then constructs `WebhookMetadata` using `request.shop` (unsigned) for the `shop` field and `request.parsed_body` (signed) for the `body` field, and calls `handler.handle` [4](#0-3) .
- `WebhookMetadata` is a plain `T::Struct` with independent `shop` and `body` fields; Sorbet only checks types, not any relationship between them [5](#0-4) .

Attack flow: The attacker creates their own development shop, installs the app, and registers/receives their own genuine webhook callback from Shopify. This callback comes with a raw body describing the attacker's own shop's data and a correctly computed `X-Shopify-Hmac-Sha256` header for that body. The attacker then sends a raw HTTP POST directly to the app's public webhook endpoint, keeping the exact `raw_body` and `hmac` header from their genuine callback unchanged, but replacing the `X-Shopify-Shop-Domain` header with the victim's shop domain. `HmacValidator.validate` still succeeds because the signature only covers `@raw_body`, which was not modified. `Registry.process` then builds a `WebhookMetadata` where `shop == victim-shop.myshopify.com` but `body` == attacker-authored JSON. Any host handler that (a) uses `data.shop` to look up/authorize the victim's tenant record, and (b) uses `data.body` to decide what to write/update, will apply attacker-controlled content to the victim's tenant — a cross-tenant data-confusion/write.

No existing guard prevents this: `ShopValidator.sanitize!` is not invoked in this webhook path, `Context.setup?`/`private?`/`embedded?` are irrelevant to webhook delivery, and Sorbet typing only enforces `String`/`Hash` shapes, not cross-field consistency.

### Impact Explanation
An unprivileged attacker who merely operates their own development shop can make the app process attacker-chosen JSON body content while the app's own webhook dispatch believes it belongs to an arbitrary victim shop (the attacker only needs to know/guess the victim's `*.myshopify.com` domain, which is often discoverable/public). This is a cross-tenant data-confusion vulnerability: a handler trusting `data.shop` for authorization while consuming `data.body` for content can be tricked into mutating or exposing victim-tenant state using attacker-authored bytes. This is repeatable against any victim shop, for any webhook topic the attacker can register and receive at least once. It falls under "cross-tenant access" — Critical.

### Likelihood Explanation
Preconditions are attacker-affordable: create a dev shop (free), install the app, register any webhook topic the app is subscribed to, and capture one genuine callback (raw body + valid HMAC header). No secrets, tokens, or victim cooperation are required. The victim's shop domain is typically low-entropy/discoverable (Shopify domains are `*.myshopify.com`, often guessable or publicly disclosed via storefront/app listings). The attack is a simple header-only replay to the app's own public webhook endpoint URL, fully repeatable per victim/topic.

### Recommendation
Bind the `shop-domain` header into the signed material, or independently verify shop identity: either include `shop-domain` (and ideally `webhook-id`) in the HMAC signable string used by `Request#to_signable_string`, or have `Registry.process` cross-check `request.shop` against a shop identifier embedded/verified inside the parsed body (or against Shopify's known registered endpoint/shop-id for that webhook subscription) before dispatching to handlers. At minimum, document prominently that `WebhookMetadata#shop` is derived from an unsigned header and must not be trusted independently of body content without additional verification.

### Proof of Concept
```ruby
# test/webhooks/registry_cross_tenant_test.rb
require "test_helper"

class RegistryCrossTenantTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_shop_header_not_bound_to_body_signature
    raw_body = '{"shop_id": "attacker-shop-id", "note": "attacker data"}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest("sha256", ShopifyAPI::Context.api_secret_key, raw_body)
    ).strip

    # genuine signature for attacker's own body, replayed with victim's shop header
    headers = {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => hmac,
      "x-shopify-shop-domain" => "victim-shop.myshopify.com",
      "x-shopify-api-version" => "2023-04",
      "x-shopify-webhook-id" => "abc123",
    }

    request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

    assert ShopifyAPI::Utils::HmacValidator.validate(request),
      "HMAC validates even though body content is unrelated to shop header"

    assert_equal "victim-shop.myshopify.com", request.shop
    assert_equal "attacker-shop-id", request.parsed_body["shop_id"]

    fake_handler = FakeWebhookHandler.new
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", delivery_method: :http, path: "/webhooks", handler: fake_handler,
    )

    ShopifyAPI::Webhooks::Registry.process(request)

    # demonstrates the broken binding: shop == victim, body == attacker content
    assert_equal "victim-shop.myshopify.com", fake_handler.received.shop
    assert_equal "attacker-shop-id", fake_handler.received.body["shop_id"]
  end

  class FakeWebhookHandler
    include ShopifyAPI::Webhooks::WebhookHandler
    attr_reader :received
    def handle(data:)
      @received = data
    end
  end
end
```
This test demonstrates that `WebhookMetadata#shop` and `WebhookMetadata#body` can be populated from an unrelated tenant/content pair off a single validly-signed request, confirming the binding `shop of body content == data.shop` is broken.

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
