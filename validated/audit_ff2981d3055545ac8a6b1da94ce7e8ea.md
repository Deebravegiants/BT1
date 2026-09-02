### Title
Webhook HMAC covers only `@raw_body`, allowing shop/topic header spoofing to redirect an authentically-signed payload to an arbitrary handler and shop - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` verifies nothing about the `x-shopify-topic` or `x-shopify-shop-domain` headers. `Registry.process` then dispatches to a handler using `request.topic` and passes `request.shop` into `WebhookMetadata` as if these values were part of the authenticated payload, when they are not.

### Finding Description
The claimed invariant is: `HmacValidator.validate(request)` being `true` should imply that every value the app subsequently trusts (topic, shop, body) was authenticated by Shopify. In reality, the binding only holds for `@raw_body`: [1](#0-0) 

`to_signable_string` returns `@raw_body` alone, and `hmac`, `topic`, `shop`, `webhook_id`, and `api_version` are all read straight from attacker-controllable headers via `shopify_header`: [2](#0-1) [3](#0-2) 

`HmacValidator.validate_signature` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac` header — it never touches topic or shop: [4](#0-3) 

`Registry.process` then does exactly what the question describes: it validates the HMAC, and *immediately after*, dispatches purely on `request.topic` (an unsigned header) to pick a handler, and forwards `request.shop` (also unsigned) into `WebhookMetadata`, with no separate authorization step tying shop/topic to the validated body: [5](#0-4) 

Exploit flow: an attacker owns/controls a development shop and installs the app, so Shopify legitimately delivers one genuine, HMAC-signed webhook to the attacker's endpoint (e.g., topic `orders/create`, shop `attacker.myshopify.com`). The attacker captures the raw body and the `x-shopify-hmac-sha256` header from that delivery. Because the signature covers only the byte content of `@raw_body`, the attacker can now POST that exact same body and HMAC header directly to the app's public webhook endpoint any number of times, each time substituting a different `x-shopify-shop-domain` header (and/or a different `x-shopify-topic` header, as long as a handler is registered for it). `Utils::HmacValidator.validate` returns `true` every time, because the check only concerns `@raw_body` vs. the (unchanged) HMAC — the shop and topic headers are simply not part of what was signed. `Registry.process` then calls `handler.handle` with a `WebhookMetadata` whose `shop` and `topic` are attacker-chosen values, alongside a body that Shopify only ever intended for the attacker's own original shop/topic combination.

No existing guard closes this gap: `HmacValidator.validate` only checks body+HMAC; there is no `ShopValidator.sanitize!`-equivalent check binding `request.shop`/`request.topic` into the signed string, and `Registry.process` performs no additional per-shop or per-topic authorization before invoking the handler.

### Impact Explanation
A downstream app handler (e.g., a GDPR/mandatory topic handler such as `customers/redact`, or a business-logic handler keyed by `shop`) receives `WebhookMetadata` believing `shop` and `topic` are authenticated, when only the body bytes are. This lets an attacker who controls just one shop (their own) impersonate an arbitrary other shop domain string toward the app's webhook handler, or force a genuinely-signed payload from one topic to be dispatched as if it belonged to a different registered topic. This is a cross-tenant/authentication-bypass class issue: the app treats an unauthenticated `shop` value as authenticated shop identity for handler logic. The severity depends entirely on what the specific app's `WebhookHandler#handle` implementations do with `data.shop`/`data.topic` (e.g., if a handler uses `shop` to look up/mutate per-tenant records, an attacker could cause cross-tenant data operations under a forged shop domain). This is repeatable indefinitely and against any shop-domain string the attacker chooses, without needing to compromise the target shop.

### Likelihood Explanation
This requires the app to be actively using the `Webhooks::Registry`/`Webhooks::Request` HMAC-only verification path as documented, with the attacker being able to (a) register their own shop and receive at least one legitimate signed webhook, and (b) send arbitrary HTTP requests directly to the app's public webhook endpoint (bypassing Shopify's delivery infrastructure) — both of which fall within the stated attacker capabilities. No secrets are required. This mirrors a known, long-standing characteristic of Shopify's real webhook HMAC scheme (the signature has always covered only the body, not headers), so it is a legitimate but low-cost, highly repeatable weakness rather than a hypothetical one.

### Recommendation
Either (a) bind `topic` and `shop` into the signable string / a secondary check before dispatch (e.g., verify the shop is an installed/known shop for this app, and treat `topic`/`shop` headers as merely advisory metadata requiring independent confirmation), or (b) document explicitly that `request.topic`/`request.shop` are unauthenticated header values and require handlers to independently verify shop legitimacy (e.g., against the app's session/shop store) before trusting them, rather than passing them through `WebhookMetadata` as if HMAC-validated.

### Proof of Concept
```ruby
# test/webhooks/registry_replay_test.rb
require "test_helper"

class WebhookReplayTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", delivery_method: :http, path: "/x", handler: FakeWebhookHandler.new
    )
  end

  def test_same_signature_accepted_for_two_different_shops
    raw_body = '{"id":1}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest("sha256", "secret", raw_body)
    ).strip

    request_a = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "x-shopify-topic" => "orders/create",
        "x-shopify-hmac-sha256" => hmac,
        "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
      },
    )
    request_b = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "x-shopify-topic" => "orders/create",
        "x-shopify-hmac-sha256" => hmac,
        "x-shopify-shop-domain" => "victim-shop.myshopify.com",
      },
    )

    assert ShopifyAPI::Utils::HmacValidator.validate(request_a)
    assert ShopifyAPI::Utils::HmacValidator.validate(request_b)
    refute_equal request_a.shop, request_b.shop # same signature, two different "authenticated" shops
  end
end
```
This demonstrates that `HmacValidator.validate` returns `true` for both requests despite differing `shop` (and it would equally differ for `topic`), confirming the shop/topic dispatch values used by `Registry.process` are outside signature coverage.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
