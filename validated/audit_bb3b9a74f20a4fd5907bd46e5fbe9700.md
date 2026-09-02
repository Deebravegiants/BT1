### Title
Webhook shop/topic headers are not covered by the HMAC signature, allowing cross-tenant header spoofing on replay — (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Registry.process` validates only that the raw request body's HMAC matches the app's shared secret via `Utils::HmacValidator.validate`, then builds `WebhookMetadata` using `request.shop`, `request.topic`, and `request.webhook_id`, all of which are read straight from unsigned HTTP headers. Because `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , none of these headers are cryptographically bound to the signature, so any `(body, hmac)` pair the attacker legitimately obtains from their own shop can be replayed with arbitrary `shop-domain`/`topic`/`webhook-id` headers and will still pass verification.

### Finding Description
The binding under test is: `shop authenticated by the signature == shop delivered to the handler`. Tracing the code:

- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received `hmac` [2](#0-1) .
- `Request#to_signable_string` returns `@raw_body` only — no headers are mixed into the signable string [1](#0-0) .
- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are all read directly from `@headers` via `shopify_header`, with no cross-check against the signed body [3](#0-2) .
- `Registry.process` raises only if the HMAC check fails, then immediately constructs `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from those same unauthenticated headers and hands it to the app's handler [4](#0-3) .
- `WebhookMetadata#shop` is a plain `T::Struct` field with no additional validation [5](#0-4) .

The app's `api_secret_key` is shared across **all shops** installed on that app (it is a per-app secret, not per-shop). Therefore any attacker who installs the app on their own shop and receives a genuine, validly-signed webhook (e.g., a `products/update` webhook whose body content they fully control because it describes their own store's data) possesses a `(raw_body, hmac)` pair that is valid for that app's secret regardless of which shop it is attributed to. Because the shop-domain, topic, and webhook-id headers are not part of the signed payload, the attacker can resend that exact body and HMAC to the same webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header with any value they choose. `HmacValidator.validate` still succeeds, since it never inspects headers, and `Registry.process` faithfully forwards the attacker-chosen `shop` string into `WebhookMetadata#shop` as if it were authenticated.

No existing guard closes this gap: `HmacValidator.validate` checks only the body signature; there is no `ShopValidator.sanitize!` call, JWT `aud`/`dest` check, or `session.shop` comparison anywhere in the webhook `process` path — webhooks in this gem carry no session/JWT at all, only headers and a signed body.

### Impact Explanation
If a host app uses `WebhookMetadata#shop` as the tenant key to look up which merchant's record to update/delete with the webhook body's data (the intended and documented usage pattern for Shopify webhooks), an attacker can cause the app to process their own webhook payload under an arbitrary victim shop domain string. This is a cross-tenant data-integrity issue: the app will attribute attacker-supplied (their-own-shop) data to another merchant's tenant record, potentially triggering writes/deletes scoped to the victim's tenant using the attacker's chosen body content. The severity aligns with "Critical – cross-tenant access," since the shop identifier the handler trusts as authenticated is fully attacker-controlled once a valid `(body, hmac)` pair exists, and this pair is trivially attacker-obtainable (they only need to be a legitimate app installer on their own store).

### Likelihood Explanation
Preconditions: the attacker must (1) install the target app on their own shop (freely available to any developer), (2) trigger any webhook topic the app subscribes to and capture the resulting body + `X-Shopify-Hmac-Sha256` header, and (3) resend that exact body/HMAC to the app's webhook endpoint with a modified `shop-domain` (and optionally `topic`/`webhook-id`) header. No secrets, tokens, or privileged access are required — this is fully within the "unprivileged attacker" threat model (install own app instance, control headers/body/ordering of their own HTTP requests). This is repeatable against arbitrary victim shop domain strings, limited only by whatever downstream validation (if any) the host app performs on `WebhookMetadata#shop`, which this gem does not itself provide.

### Recommendation
Bind the security-relevant headers into the signed payload verification, or otherwise avoid trusting `shop-domain`/`topic`/`webhook-id` headers as authenticated identifiers:
- Extend `Request#to_signable_string` (or add a secondary check) so that `shop-domain`, `topic`, and `webhook-id` are included in what `HmacValidator` verifies, so a replayed body cannot be paired with different header values without invalidating the signature.
- Alternatively, document and enforce that host apps must not treat `WebhookMetadata#shop`/`topic` as authenticated tenant identifiers without independently confirming that the shop is one which has completed OAuth and has a valid stored access token, and that the webhook body content is validated against expected schema/ownership for that shop before use.

### Proof of Concept
```ruby
# test/webhooks/registry_shop_binding_test.rb
require "test_helper"

class RegistryShopBindingTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", api_version: "2023-01",
      host_name: "app.example.com", scope: "read_products", is_embedded: false,
      is_private: false, session_storage: nil,
    )
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_replayed_body_can_claim_any_shop
    body = '{"id":1,"title":"attacker-owned product"}'
    hmac = OpenSSL::HMAC.base64digest(OpenSSL::Digest.new("sha256"), "secret", body)

    handler = Class.new do
      include ShopifyAPI::Webhooks::WebhookHandler
      attr_reader :received_shop
      def handle(data:)
        @received_shop = data.shop
      end
    end.new

    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "products/update", delivery_method: :http, path: "/webhooks", handler: handler,
    )

    request = ShopifyAPI::Webhooks::Request.new(
      raw_body: body,
      headers: {
        "X-Shopify-Topic" => "products/update",
        "X-Shopify-Hmac-Sha256" => hmac,
        # Attacker substitutes an arbitrary victim shop domain here;
        # the header is never covered by the signature.
        "X-Shopify-Shop-Domain" => "victim-shop.myshopify.com",
        "X-Shopify-Api-Version" => "2023-01",
        "X-Shopify-Webhook-Id" => "attacker-chosen-id",
      },
    )

    ShopifyAPI::Webhooks::Registry.process(request)

    # FAILS the intended invariant: shop authenticated by the signature (attacker's own shop)
    # != shop delivered to the handler (arbitrary victim string), yet processing succeeds.
    assert_equal "victim-shop.myshopify.com", handler.received_shop
  end
end
```
This test demonstrates that a body/HMAC pair valid for the app's shared secret can be freely paired with any `shop-domain` header value, and `Registry.process` accepts it and forwards the spoofed shop to the handler as authenticated `WebhookMetadata#shop`.

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
