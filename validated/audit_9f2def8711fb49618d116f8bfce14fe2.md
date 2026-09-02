### Title
Webhook HMAC signs only the raw body, not the `topic`/`shop` headers, so `Registry.process` dispatches an authenticated body to an attacker-chosen handler under an attacker-chosen shop - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`Utils::HmacValidator.validate` only proves that `@raw_body` was HMAC-signed by Shopify with the app's `api_secret_key`; it never covers `topic`, `shop-domain`, `api-version`, or `webhook-id`, since `Request#to_signable_string` returns `@raw_body` alone. `Registry.process` then dispatches based on `request.topic` (an unauthenticated header) and forwards `request.shop` (also unauthenticated) straight into the handler's `WebhookMetadata`, so a validly-signed body captured for one topic/shop can be replayed with a relabeled topic and/or shop header and still pass HMAC validation.

### Finding Description
The broken binding, stated explicitly: `HMAC_valid(raw_body) == true` is treated by `Registry.process` as if it implied `authenticated_topic == dispatched_topic` and `authenticated_shop == dispatched_shop`. That implication does not hold.

- `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `Request#topic`, `#shop`, `#api_version`, `#webhook_id` are all read straight from attacker-controlled headers with no cryptographic tie to the body: [2](#0-1) 
- `HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares to the received signature — again, body-only: [3](#0-2) 
- `Registry.process` gates on this body-only HMAC, then looks up the handler purely by `request.topic` and passes `request.topic`/`request.shop` unchanged into `WebhookMetadata`: [4](#0-3) 
- `MANDATORY_TOPICS` (`shop/redact`, `customers/redact`, `customers/data_request`) only gates the registration-time API (`register`/`unregister`), never `process`: [5](#0-4) [6](#0-5) [7](#0-6) 

Exploit flow: the attacker installs the app on their own shop and receives a legitimate webhook for `products/update` at their own registered endpoint — a real HTTP POST from Shopify with `raw_body` B and header `x-shopify-hmac-sha256 = HMAC(secret, B)`. Because the app's `api_secret_key` is shared across all shops/installations of that app (not per-tenant), this signature is valid for any request whose `to_signable_string` (i.e., raw body) equals B, regardless of what topic/shop headers accompany it. The attacker then sends their own HTTP POST directly to the app's public webhook controller endpoint (the same route the app wires to `Registry.process`), using body B and the captured HMAC, but with `x-shopify-topic: shop/redact` and, if the app doesn't otherwise scope by session, an attacker-chosen `x-shopify-shop-domain`. `HmacValidator.validate` returns `true` (body matches, secret matches), `Registry.process` looks up the handler registered by the app for `shop/redact` (wired independently for GDPR compliance) and invokes `handler.handle(data: WebhookMetadata.new(topic: "shop/redact", shop: <attacker-controlled>, body: <products/update-shaped JSON>, ...))`.

None of the existing guards stop this: `HmacValidator.validate` only binds the secret to the body, not to topic/shop; `MANDATORY_TOPICS` is checked only inside `register`/`unregister`, never inside `process`; there is no Sorbet runtime check binding `WebhookMetadata.topic`/`shop` to anything cryptographic — the struct just stores whatever strings `Registry.process` passes it. `ShopValidator`, `JwtPayload`, and OAuth-session mechanisms are not in this call path at all — webhook processing is a separate, unauthenticated-by-session channel that relies entirely on the HMAC, and the HMAC's coverage is too narrow.

### Impact Explanation
This is a Critical finding matching "cross-tenant access": an unprivileged attacker can trigger destructive GDPR-redaction (or any other registered handler's) logic under a shop identifier of their choosing, using a body payload never intended for that handler, because the topic and shop fields that the handler trusts (via `WebhookMetadata`) are unauthenticated. The blast radius spans every topic/handler the host app has registered, and — if the app doesn't independently verify `data.shop` against the requesting party/session elsewhere — every tenant, since `shop` in `WebhookMetadata` is equally unauthenticated. This is repeatable indefinitely: the attacker can keep receiving legitimate signed bodies from their own shop's ordinary webhook traffic and replay each one under any topic/shop label.

### Likelihood Explanation
Preconditions: (1) attacker has any shop that installs the app and can receive at least one real webhook (trivial — any developer/test shop); (2) the app has registered an HTTP handler for a topic worth abusing (here, `shop/redact`, required for GDPR compliance in virtually every production app); (3) the app's webhook controller endpoint is reachable over the internet (required for Shopify to deliver webhooks in the first place). No secrets, tokens, or session state are needed — the attacker only needs to capture one real `(raw_body, hmac)` pair addressed to their own endpoint and resend it with different headers to the app's endpoint. Attacker cost is minimal and does not depend on timing, races, or DoS mechanics.

### Recommendation
Bind the signed content to the routing/authorization decision:
- Extend `to_signable_string` (or a webhook-specific signable representation) to include `topic` and `shop-domain` alongside the body, so any change to those headers invalidates the HMAC.
- Alternatively/additionally, in `Registry.process`, re-derive dispatch from data included in the authenticated payload (or require the host app to separately verify `shop` against a known/registered shop before invoking mandatory-topic handlers).
- Enforce `MANDATORY_TOPICS` semantics at process-time too, e.g. document/require that handlers for GDPR topics independently re-verify `data.shop` is an installed, currently-active tenant before performing redaction, since `Registry.process` cannot itself guarantee this binding without a code change to the signing scheme.

### Proof of Concept
```ruby
# test/webhooks/registry_topic_confusion_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Webhooks
    class RegistryTopicConfusionTest < Test::Unit::TestCase
      def setup
        super
        ShopifyAPI::Webhooks::Registry.clear
      end

      def test_hmac_does_not_bind_topic_or_shop_allowing_relabeled_dispatch
        raw_body = '{"id":123,"title":"some product"}' # products/update-shaped body
        secret = ShopifyAPI::Context.api_secret_key
        hmac = Base64.encode64(
          OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
        )

        received_shop_redact_data = nil
        shop_redact_handler = TestHelpers::FakeWebhookHandler.new(
          lambda { |data| received_shop_redact_data = data },
        )

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: "shop/redact", delivery_method: :http, path: "callback/shop_redact",
          handler: shop_redact_handler,
        )

        # Attacker relabels topic to shop/redact and shop to an arbitrary victim domain,
        # reusing a validly-signed products/update body/hmac pair.
        forged_headers = {
          "x-shopify-topic" => "shop/redact",
          "x-shopify-hmac-sha256" => hmac,
          "x-shopify-shop-domain" => "victim-shop.myshopify.com",
        }

        forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

        # Binding under test: HMAC-authenticated payload == dispatched (topic, shop).
        # Left side (what was actually signed): raw_body only, no topic/shop.
        # Right side (what process() trusts): topic == "shop/redact", shop == "victim-shop.myshopify.com".
        assert(ShopifyAPI::Utils::HmacValidator.validate(forged_request), "HMAC unexpectedly rejects relabeled headers")

        ShopifyAPI::Webhooks::Registry.process(forged_request)

        assert_equal("shop/redact", received_shop_redact_data.topic)
        assert_equal("victim-shop.myshopify.com", received_shop_redact_data.shop)
        assert_equal(JSON.parse(raw_body), received_shop_redact_data.body)
        # Demonstrates: a body never intended for shop/redact, and a shop the attacker
        # does not own, both reach the GDPR-redaction handler with a passing HMAC check.
      end
    end
  end
end
```
This demonstrates that `HmacValidator.validate` returns `true` for a body/hmac pair whose accompanying `topic` and `shop` headers were changed after signing, and that `Registry.process` forwards those unauthenticated values unchanged into the dispatched handler's `WebhookMetadata`.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
```

**File:** lib/shopify_api/webhooks/registry.rb (L58-59)
```ruby
        def register(topic:, session:)
          return mandatory_registration_result(topic) if mandatory_webhook_topic?(topic)
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

**File:** lib/shopify_api/webhooks/registry.rb (L251-254)
```ruby
        sig { params(topic: String).returns(T::Boolean) }
        def mandatory_webhook_topic?(topic)
          MANDATORY_TOPICS.include?(topic)
        end
```
