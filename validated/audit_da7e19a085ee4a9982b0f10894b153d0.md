### Title
`shop`, `topic`, `webhook_id`, and `api_version` headers are excluded from the HMAC-signed payload, allowing cross-shop webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read from HTTP headers that are never part of the signed string. Because `api_secret_key` is the app's single client secret shared by every shop that installs the app, an attacker who owns their own development shop can capture a legitimately-signed webhook body and replay it to the app's callback endpoint with a forged `x-shopify-shop-domain` (and/or `x-shopify-topic`/`x-shopify-webhook-id`) header pointing at a different shop, and the signature check still passes.

### Finding Description
The claimed binding is: `HmacValidator.validate` should guarantee that every field the handler acts on is bound to the value Shopify actually signed, i.e. `hmac == HMAC(secret, signable_string)` implies `signable_string` determines `shop`. This binding does not hold.

`to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, `api_version` and the HMAC itself are all pulled from headers via the private `shopify_header`, which are stored and normalized independently of the body in `initialize`: [2](#0-1) 

`HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it to the header-supplied `hmac`: [3](#0-2) 

`Registry.process` trusts `request.shop`, `request.topic`, and `request.webhook_id` — none of which are covered by the signature — to build `WebhookMetadata` and dispatch to the host app's handler: [4](#0-3) 

`WebhookMetadata#shop` is a plain `String` field with no further validation, and the documented usage pattern shows the host app using `data.shop` directly to decide which shop's records the enqueued job should act on: [5](#0-4) [6](#0-5) 

Root cause: `api_secret_key` (`Context.api_secret_key`) is the app's single client secret, identical for every shop that has installed the app — it is not shop-specific. Combined with headers being outside the signable string, any party who can obtain one validly-signed webhook body (trivially achievable by installing the app on their own free development shop and receiving a genuine callback) can replay that exact body to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still succeeds because it only checks the body bytes, so `Registry.process` calls the handler with `shop` equal to the attacker-chosen header value rather than the shop that actually produced the signed body. `ShopValidator.sanitize!`, `state` comparisons, and `JwtPayload` checks are irrelevant here (they guard OAuth/session-token paths, not `Webhooks::Request`), and there is no mechanism in `Request`, `Registry`, or `HmacValidator` that ties the header-derived `shop` to the signed body.

The specific mechanism proposed in the question (body-byte divergence between the framework's `JSON.parse` input and the signed bytes via encoding/BOM/rewound-stream tricks) does not apply here — `to_signable_string` and `parsed_body` both operate on the exact same `@raw_body` instance variable, so there is no byte-variance channel for the body itself. The actual exploitable gap is the header/body decoupling described above, which independently satisfies the "shop handed to handler unverified" claim in the question.

### Impact Explanation
An attacker can cause an app's webhook handler to process a body under an attacker-chosen `shop` value that the app then uses to select which tenant's records to write, enqueue jobs for, or otherwise act on (per the documented handler pattern of `perform_later(shop_domain: data.shop, ...)`). This is a cross-tenant data confusion / authentication-bypass class issue: a genuinely-signed payload (attacker's own shop's webhook) is misattributed to an arbitrary victim shop domain, letting the attacker inject fabricated "events" against another merchant's tenant context in the host app. It is repeatable at will against any shop domain string the attacker chooses, since nothing after HMAC validation re-derives or checks `shop` against the signed content.

### Likelihood Explanation
Preconditions: the host app must use `ShopifyAPI::Webhooks::Registry.process`/`Request` as documented, and (as is normal) share one `api_secret_key` across all installs of the app. The attacker needs no privileged credentials — only their own free development store, installing the target app, and receiving one real webhook callback (fully within the described "unprivileged attacker" capabilities: their own shop, their own server, arbitrary header control). The attack cost is a single legitimately obtained signed body plus one replayed HTTP POST with a modified header; it is trivially repeatable.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the signed material the app trusts, or independently verify the shop against a durable, session-bound identifier before dispatching to the handler. Concretely: fold the relevant headers into `to_signable_string` for webhook verification (or require the host app to cross-check `request.shop` against a shop associated with an existing, already-verified session/registration for that webhook topic) before invoking `WebhookHandler#handle`.

### Proof of Concept
```ruby
# test/webhooks/registry_shop_confusion_test.rb
require "test_helper"

class WebhookShopConfusionTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", delivery_method: :http,
      handler: FakeWebhookHandler, path: "callback"
    )
  end

  def test_signature_does_not_bind_shop_header
    body = '{"id":1}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest("sha256", "secret", body)
    ).strip

    received_shops = []
    FakeWebhookHandler.stub(:handle, ->(data:) { received_shops << data.shop }) do
      # Request 1: attacker's own shop
      req1 = ShopifyAPI::Webhooks::Request.new(
        raw_body: body,
        headers: {
          "x-shopify-hmac-sha256" => hmac,
          "x-shopify-topic" => "orders/create",
          "x-shopify-shop-domain" => "attacker.myshopify.com",
          "x-shopify-webhook-id" => "1",
          "x-shopify-api-version" => "2023-01",
        },
      )
      ShopifyAPI::Webhooks::Registry.process(req1)

      # Request 2: same body/signature, forged victim shop header
      req2 = ShopifyAPI::Webhooks::Request.new(
        raw_body: body,
        headers: {
          "x-shopify-hmac-sha256" => hmac,
          "x-shopify-topic" => "orders/create",
          "x-shopify-shop-domain" => "victim.myshopify.com",
          "x-shopify-webhook-id" => "1",
          "x-shopify-api-version" => "2023-01",
        },
      )
      ShopifyAPI::Webhooks::Registry.process(req2)
    end

    # Same HMAC accepted for two different shops -> binding is broken
    assert_equal ["attacker.myshopify.com", "victim.myshopify.com"], received_shops
  end
end
```
Both calls to `Registry.process` succeed (`HmacValidator.validate` passes both times because it only checks `body`/`hmac`), yet `data.shop` differs between the two — proving the header-derived `shop` is not bound by the signature covering `to_signable_string`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-70)
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

      private

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
