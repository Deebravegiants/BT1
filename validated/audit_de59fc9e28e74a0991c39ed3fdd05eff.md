### Title
Unsigned `shop-domain` and `topic` headers trusted by `Registry.process` while HMAC only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `HmacValidator.validate` covers the body alone. `Request#topic`, `Request#shop`, `Request#webhook_id`, and `Request#api_version` are all read from HTTP headers that are excluded from that signable string, yet `Registry.process` uses `request.topic` to select the handler and passes `request.shop`/`request.webhook_id` straight into `WebhookMetadata` as authenticated data.

### Finding Description
The invariant under test is: "every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`." Concretely this should mean `to_signable_string == f(topic, shop, webhook_id, api_version, body)`, but in fact: [1](#0-0) 

only returns `@raw_body`, while `topic`, `shop`, `webhook_id`, and `api_version` are pulled from `@headers` via `shopify_header`: [2](#0-1) 

`HmacValidator.validate` only calls `verifiable_query.to_signable_string` and `verifiable_query.hmac` to compute/compare the signature: [3](#0-2) 

`Registry.process` validates the HMAC once, then immediately trusts `request.topic` to look up a handler, and forwards `request.shop`/`request.webhook_id`/`request.api_version` into the handler's data without any additional check that these header values match what Shopify actually signed: [4](#0-3) 

Because `shopify-topic`/`x-shopify-topic`, `shopify-shop-domain`/`x-shopify-shop-domain`, and `shopify-webhook-id`/`x-shopify-webhook-id` are not part of the signable string, an attacker who has ever received one genuinely-signed webhook body+HMAC pair for their own dev shop (Shopify apps use a single global `api_secret_key` shared across all installs) can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting arbitrary values for `x-shopify-shop-domain` and/or `x-shopify-topic`. `HmacValidator.validate` still succeeds because it only checks the body, but `Registry.process` dispatches on the attacker-chosen `topic` and passes the attacker-chosen `shop` to the handler as if it were authenticated. No existing guard (`ShopValidator.sanitize!`, `Context.setup?`, Sorbet typing) checks that the header values were part of what Shopify signed—Sorbet only enforces that `topic`/`shop` are non-nil strings, not that they are authentic.

### Impact Explanation
A handler that keys tenant-specific behaviour off `WebhookMetadata#shop` (a normal pattern: look up the shop's session/access token, write to that shop's records, trigger merchant-specific side effects) can be made to act on behalf of an arbitrary shop domain chosen by the attacker, using a body the attacker legitimately received for their own installation. Likewise, replaying the same signed body under a different `topic` can route data into a handler that assumes a different JSON schema/semantics for that topic, causing handler-topic confusion. This is a cross-tenant integrity issue: one signed payload can be re-attributed to any shop, satisfying the "one tenant's request touching another tenant's data" criterion.

### Likelihood Explanation
Preconditions: attacker only needs to install the target app on their own development shop (a normal, unprivileged action) to receive at least one genuinely signed webhook body/HMAC pair, and to be able to POST directly to the app's webhook endpoint (no TLS interception or secrets needed). Cost is a single HTTP replay with modified headers; it is fully repeatable against any shop domain string the attacker chooses, since the endpoint itself does not independently verify that the `shop-domain` header corresponds to a real installation before calling `Registry.process`.

### Recommendation
Include the relevant header values (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the string that is HMAC-verified, or otherwise cryptographically bind them to the body (e.g., verify `shop` against an actively known/installed shop and require it be cross-checked before dispatch), so that `to_signable_string` reflects everything `Registry.process` and `WebhookMetadata` act on.

### Proof of Concept
```ruby
# test/webhooks/request_signature_coverage_test.rb
require_relative "../test_helper.rb"

class WebhookSignatureCoverageTest < Test::Unit::TestCase
  def test_replayed_body_can_impersonate_different_shop
    body = "{}"
    hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
    hmac_header = Base64.encode64(hmac)

    received_shops = []
    handler = TestHelpers::FakeWebhookHandler.new(lambda { |data| received_shops << data.shop })
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", path: "path", delivery_method: :http, handler: handler,
    )

    headers_a = {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => hmac_header,
      "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
    }
    headers_b = headers_a.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers_a),
    )
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers_b),
    )

    # Same signed body/hmac accepted twice, dispatched with two different, attacker-chosen shops
    assert_equal(["attacker-shop.myshopify.com", "victim-shop.myshopify.com"], received_shops)
  end
end
```
Both requests use the identical `raw_body`/`hmac` pair (so `HmacValidator.validate` passes both times), yet `data.shop` differs per request—demonstrating that `shop` (and by the same code path, `topic`) is not covered by the signature that `Registry.process` relies on for authorization.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
