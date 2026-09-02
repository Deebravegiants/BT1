### Title
Webhook HMAC authenticates only the raw body, not the `shop-domain`/`topic` headers, enabling cross-tenant/cross-topic replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` computes/compares the HMAC solely over that raw body [1](#0-0) . `Registry.process` trusts `request.shop` and `request.topic`, which come straight from unauthenticated headers, once `HmacValidator.validate` returns true, and `ShopValidator.sanitize!` is never invoked anywhere in this path [2](#0-1) . This means an attacker who legitimately receives one validly-signed webhook body from their own installation (using the app's single, shop-independent `client_secret`) can replay that exact `(raw_body, hmac)` pair with forged `shop-domain` and `topic` headers, and it will still validate.

### Finding Description
The binding that should hold is: `shop_authenticated_by_hmac == shop_acted_on_by_handler` and `topic_authenticated_by_hmac == topic_acted_on_by_handler`. Tracing the code:

- `Webhooks::Request#initialize` only checks that the three headers are *present*; it never sanitizes or validates `shop-domain` against `ShopValidator.sanitize!`, and never binds it to the body [3](#0-2) .
- `#shop` and `#topic` are plain header reads [4](#0-3) .
- `#to_signable_string` returns `@raw_body` alone, so the HMAC signable string contains no shop or topic information at all [1](#0-0) .
- `HmacValidator.validate_signature` recomputes HMAC over `verifiable_query.to_signable_string` (i.e. body only) using `Context.api_secret_key` and compares to the received signature [5](#0-4) .
- `Registry.process` raises only if the HMAC fails, then looks up the handler by `request.topic` and calls it with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` — both taken directly from headers, with zero cross-check against the body [2](#0-1) .

So after tracing: the two sides of the binding are **not equal** — the HMAC authenticates only the body; `shop` and `topic` are unauthenticated header values trusted verbatim by `Registry.process`/`WebhookMetadata`.

Critically, the `api_secret_key` (the app's `client_secret`) is the **same value for every shop that installs the app** — it is not per-tenant. This means an attacker can:
1. Install the target app on their own (attacker-controlled) development shop and register a webhook for any topic on their own webhook endpoint.
2. Receive one legitimately-signed webhook: a real `(raw_body, hmac)` pair signed with the shared `client_secret`.
3. Replay that exact `raw_body` and `hmac` header value to the victim app's webhook endpoint, but substitute `x-shopify-shop-domain` with an arbitrary victim shop domain and `x-shopify-topic` with any topic registered in that app's `Registry` (including topics different from the one originally captured).
4. Because `HmacValidator.validate` only checks `raw_body`/secret, and `ShopValidator.sanitize!` is never called, the forged request passes and the handler executes believing it received an authentic event for the victim shop/topic.

This is confirmed by the gem's own test fixtures, which build a `Request` from a fixed `hmac` computed over `"{}"` and freely-chosen `shop`/`topic` headers, and `Registry.process` accepts it [6](#0-5) [7](#0-6) .

No existing guard prevents this: `HmacValidator.validate` (body-only check) passes trivially with a replayed body; `ShopValidator.sanitize!` is never invoked in this file or in `Registry`; there is no `state` comparison or JWT `aud` check in this webhook path (those apply only to OAuth/session-token flows, not webhooks).

### Impact Explanation
A handler that trusts `WebhookMetadata#shop` and `WebhookMetadata#topic` (as the gem's own design intends, since these are the only shop/topic signals provided) can be made to process/act on data intended to represent a different merchant and/or a different event type than what was actually signed. This is a cross-tenant authentication/binding failure: the app cannot cryptographically distinguish "this body was really sent by Shopify for shop X and topic Y" from "this body was sent by Shopify for some other shop/topic and replayed by an attacker." Depending on what host applications do inside their `WebhookHandler#handle` implementations (e.g., writing/deleting merchant data keyed by `data.shop`, honoring `customers/redact` or `shop/redact` compliance actions, or triggering billing/plan logic keyed by `data.shop`), this can result in cross-tenant data corruption or spurious compliance/administrative actions attributed to a shop that never sent the event. It is repeatable indefinitely and against arbitrary victim shop domains (the attacker only needs to know or guess a victim's `.myshopify.com` domain, which is often public), for any topic present in the app's `Registry`.

### Likelihood Explanation
This is inherent to how Shopify's webhook signing scheme works and how this gem faithfully implements it: the HMAC is documented by Shopify to be computed over the raw body only, with `shop`/`topic` delivered as separate, unsigned headers. Any developer building an app on this gem, and any attacker, can trivially install the target app on a free development store, capture one real signed webhook, and replay it with modified headers — no secret material, TLS interception, or privileged access is required, matching the stated attacker model. The severity in practice depends entirely on whether the host application's webhook handlers make security-sensitive decisions based on `WebhookMetadata#shop`/`#topic` without any additional out-of-band verification (e.g., checking that the shop is one the app has an active session for, or that the body content itself matches the claimed shop). The gem provides no primitive to close this gap (no `ShopValidator.sanitize!` call, no signed shop/topic).

### Recommendation
- Do not treat `WebhookMetadata#shop` as authenticated by itself; document that host apps must independently verify the shop (e.g., against an active session/install record) before acting on webhook data, or
- Extend the signable string / verification to incorporate `shop-domain` and `topic` where feasible, and/or
- At minimum call `ShopValidator.sanitize!` on `request.shop` inside `Webhooks::Request#initialize` or `Registry.process` to reject malformed/spoofed shop domains, and clearly document in `docs/usage/webhooks.md` that shop/topic headers are not covered by the HMAC and must not be solely relied upon for tenant isolation.

### Proof of Concept
```ruby
# test/webhooks/registry_cross_tenant_replay_test.rb
require_relative "../test_helper.rb"

module ShopifyAPITest
  module Webhooks
    class CrossTenantReplayTest < Test::Unit::TestCase
      def setup
        super
        @raw_body = "{}"
        @real_hmac = Base64.encode64(
          OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, @raw_body),
        )
      end

      def test_replay_across_shops_and_topics
        %w[topic/a topic/b].each do |topic|
          handled = false
          handler = TestHelpers::FakeWebhookHandler.new(lambda do |data|
            assert_equal("victim-shop.myshopify.com", data.shop)
            handled = true
          end)
          ShopifyAPI::Webhooks::Registry.add_registration(
            topic: topic, path: "path", delivery_method: :http, handler: handler,
          )

          forged_headers = {
            "x-shopify-topic" => topic,
            "x-shopify-hmac-sha256" => @real_hmac,          # captured from attacker's own shop
            "x-shopify-shop-domain" => "victim-shop.myshopify.com", # arbitrary victim, never signed
            "x-shopify-webhook-id" => "forged-id",
            "x-shopify-api-version" => "2024-01",
          }

          request = ShopifyAPI::Webhooks::Request.new(raw_body: @raw_body, headers: forged_headers)

          # Binding check: HMAC authenticates only @raw_body, not shop/topic
          assert(ShopifyAPI::Utils::HmacValidator.validate(request))

          ShopifyAPI::Webhooks::Registry.process(request) # accepted -> cross-tenant forgery
          assert(handled)
        end
      end
    end
  end
end
```
This demonstrates the same `(raw_body, hmac)` pair, obtainable by any attacker who installs the app on their own shop, being accepted by `Registry.process` for an arbitrary `shop-domain` and multiple different `topic` values, confirming `shop_authenticated_by_hmac != shop_acted_on_by_handler` (and same for `topic`).

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

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

        @headers = headers
        @raw_body = raw_body
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

**File:** test/webhooks/registry_test.rb (L14-30)
```ruby
        @shop = "shop.myshopify.com"

        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
```

**File:** test/webhooks/registry_test.rb (L218-239)
```ruby
      def test_process
        handler_called = false

        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal(@headers["x-shopify-webhook-id"], data.webhook_id)
            assert_equal(@headers["x-shopify-api-version"], data.api_version)
            handler_called = true
          end,
        )

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: @topic, path: "path", delivery_method: :http, handler: handler,
        )

        ShopifyAPI::Webhooks::Registry.process(@webhook_request)

        assert(handler_called)
      end
```
