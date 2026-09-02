### Title
Webhook `HmacValidator` only signs the raw body, letting attacker-controlled `topic`/`shop-domain` headers reach the handler unauthenticated - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes the HMAC only over `request.to_signable_string` (the raw body). It never covers the `topic`, `shop-domain`, `webhook-id`, or `api-version` headers, yet `process` uses `request.topic` to select the handler and forwards `request.shop`/`webhook_id`/`api_version` straight into `WebhookMetadata` as trusted values. Because the app's `api_secret_key` is shared across every shop installed on the app and the webhook delivery URL (`path`) is the same for all shops, any attacker who legitimately receives one signed webhook body from their own development shop can replay that exact body with forged `topic`/`shop-domain` headers to the app's public webhook endpoint and have it accepted as authentic for an arbitrary topic/shop.

### Finding Description
The binding that must hold is: `HmacValidator.validate(request) == true` should imply every value `process` subsequently trusts (`request.topic`, `request.shop`, `request.webhook_id`, `request.api_version`) was itself covered by the signature. Tracing the code shows this is false:

- `Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `Webhooks::Request#topic`, `#shop`, `#webhook_id`, `#api_version` are all read straight from HTTP headers, none of which flow into `to_signable_string`: [2](#0-1) 
- `HmacValidator.validate_signature` computes the HMAC solely from `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 
- `Registry.process` first calls `HmacValidator.validate(request)` (body-only check), then immediately dispatches based on `request.topic` and forwards `request.shop`, `request.webhook_id`, `request.api_version` into the handler's `WebhookMetadata`, none of which were part of the signed string: [4](#0-3) 

Exploit flow: the app's `client_secret`/`api_secret_key` is a single, per-app secret shared by every shop that installs the app, and the webhook callback `path` registered via `add_registration`/`register` is the same URL for all shops/topics of that delivery type. An attacker can install the app on their own development shop, trigger a real event, and receive a genuinely Shopify-signed webhook (valid `hmac` header) for their own shop and topic. Because the signature covers only the raw body, the attacker can now POST that same `raw_body` + `hmac` to the app's public webhook endpoint while freely setting `x-shopify-topic` to a different registered topic and `x-shopify-shop-domain` to the victim shop's domain. `HmacValidator.validate` still returns `true` (the body/HMAC pair is unchanged), so `process` treats the forged headers as authentic, looks up whatever handler is registered under the attacker-chosen topic, and calls it with `shop: <victim shop>`, letting a forged/replayed request be accepted as if it were an authentic delivery for another tenant and another topic.

Existing guards do not stop this: `HmacValidator.validate` only proves knowledge of the body's HMAC under the shared secret, not the topic or shop; there is no `ShopValidator.sanitize!` or session check anywhere in `Registry.process`; no code cross-checks `request.shop` against an active session or against the shop that the given topic/handler was registered for.

### Impact Explanation
This lets an unprivileged attacker (any developer who can install the target app on a shop they control) forge webhook deliveries that the host app will treat as authentic for **any topic** registered in `Registry` and for **any shop domain** value they choose to put in the header, including a real victim merchant's shop domain. Depending on what the registered handler does with `WebhookMetadata#shop` (e.g., deleting data for that shop, revoking access, updating records keyed by shop), this is a genuine authentication bypass: a forged/cross-tenant request is accepted as authentic. It is repeatable indefinitely and against arbitrary shop values, since nothing after `HmacValidator.validate` constrains `shop` or `topic` to what was actually signed.

### Likelihood Explanation
Preconditions are low-cost and fully within the described attacker capability: create a free development shop, install the target app (this is a normal, permitted action for any developer), trigger any webhook event to receive one genuinely signed body/HMAC pair, then send a crafted HTTP POST to the app's known webhook path with forged `topic`/`shop-domain` headers. No access to `api_secret_key` or any credential is required, only observation of one legitimate signed payload. This is feasible for any Shopify app built with this gem and using multiple registered topics/handlers via `Webhooks::Registry`.

### Recommendation
Bind the signature check to more than the raw body: incorporate `topic` and `shop-domain` (and ideally `webhook-id`) into `to_signable_string`, or independently verify that the `shop` header corresponds to a shop that legitimately received a webhook for that `topic`/`webhook_id` (e.g., via out-of-band tracking of webhook IDs, or by cross-checking against the shop's session/installation record) before dispatching to a handler. At minimum, document that `WebhookMetadata#shop` and `#topic` are **not** cryptographically authenticated by `HmacValidator` and must not be trusted for authorization decisions without additional verification by the host app.

### Proof of Concept
```ruby
# test/webhooks/registry_signature_coverage_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Webhooks
    class RegistrySignatureCoverageTest < Test::Unit::TestCase
      def test_signature_does_not_cover_topic_or_shop
        raw_body = "{}"
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          raw_body,
        )
        signed_hmac_header = Base64.encode64(hmac)

        topic_a_called = false
        topic_b_called = false

        handler_a = TestHelpers::FakeWebhookHandler.new(->(_data) { topic_a_called = true })
        handler_b = TestHelpers::FakeWebhookHandler.new(->(_data) { topic_b_called = true })

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: "orders/create", path: "path", delivery_method: :http, handler: handler_a,
        )
        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: "customers/redact", path: "path", delivery_method: :http, handler: handler_b,
        )

        # Attacker captured a genuinely signed body for "orders/create" from their own shop,
        # but re-sends it claiming topic "customers/redact" and a victim shop domain.
        forged_headers = {
          "x-shopify-topic" => "customers/redact",
          "x-shopify-hmac-sha256" => signed_hmac_header,
          "x-shopify-shop-domain" => "victim-shop.myshopify.com",
        }

        request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

        # Binding under test: HmacValidator.validate(request) == true
        #   should imply request.topic/request.shop were covered by the signature.
        assert(ShopifyAPI::Utils::HmacValidator.validate(request)) # passes: body-only HMAC matches

        ShopifyAPI::Webhooks::Registry.process(request)

        # Dispatch followed the unsigned header, not any signed value -> bug demonstrated.
        assert(topic_b_called)
        refute(topic_a_called)
      end
    end
  end
end
```
This demonstrates that `HmacValidator.validate` returning `true` for a body signed under one topic/shop is silently reused by `Registry.process` to authorize dispatch under a completely different, attacker-chosen `topic` and `shop`, confirming the signature-coverage invariant is violated.

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
