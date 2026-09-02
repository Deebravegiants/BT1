### Title
HMAC signature omits `shop-domain`, `topic`, `api-version`, `webhook-id` headers, allowing header relabeling of a validly-signed webhook body - (File: lib/shopify_api/utils/hmac_validator.rb, lib/shopify_api/webhooks/request.rb)

### Summary
`HmacValidator.validate` computes and compares an HMAC only over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns solely `@raw_body`. The `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from unauthenticated HTTP headers and are never mixed into the signed string, so two `Request` objects built from the same `raw_body`/`hmac` but with arbitrarily different `shop-domain`, `topic`, `api-version`, and `webhook-id` headers validate identically.

### Finding Description
The binding under test is:
`HmacValidator.validate(request_A) == HmacValidator.validate(request_B)` for all `request_A`, `request_B` such that `request_A.raw_body == request_B.raw_body` and `request_A.hmac == request_B.hmac`, regardless of `shop`, `topic`, `api_version`, `webhook_id`.

Tracing the code confirms this holds:
- `HmacValidator.validate` reads only `verifiable_query.hmac` and `verifiable_query.to_signable_string`. [1](#0-0) 
- `validate_signature` computes `OpenSSL::HMAC.hexdigest` over `to_signable_string` and secure-compares it to `hmac`. [2](#0-1) 
- `Webhooks::Request#to_signable_string` returns `@raw_body` only. [3](#0-2) 
- `topic`, `shop`, `api_version`, `webhook_id` are plain header readers, disjoint from `to_signable_string`/`hmac`. [4](#0-3) 

Downstream, `Registry.process` trusts these unauthenticated fields directly: it dispatches to a handler keyed by `request.topic` and builds `WebhookMetadata` using `request.shop`, `request.api_version`, `request.webhook_id`, after only checking `HmacValidator.validate(request)`. [5](#0-4) 

Attack flow: an attacker registers their own app installation on a shop they control and points the webhook delivery URL at a server they operate (permitted under the threat model). They capture any real, validly-signed `(raw_body, hmac)` pair the platform sends them — the `hmac` is computed by Shopify using the app's shared `api_secret_key`, which is the same secret for every shop that installs that app, so the pair is valid independent of which shop originated it. The attacker then replays that exact `raw_body` + `hmac` header to the target app's real (public) webhook endpoint, substituting `shop-domain`, `topic`, `webhook-id`, and `api-version` headers of their choosing (e.g. claiming a victim shop domain and a topic for which the app registered a handler, such as a mandatory GDPR topic if the app added a handler for it). `HmacValidator.validate` returns `true` because it never inspects those headers, and `Registry.process` runs the handler believing the event genuinely originates from the claimed shop/topic/webhook-id.

No existing guard in this file closes the gap: `HmacValidator.validate` has no shop/topic parameter to check against; `Registry.process` performs no additional binding between the validated body and the claimed headers.

### Impact Explanation
The unauthenticated `shop`, `topic`, and `webhook_id` fields are treated as authenticated by `Registry.process` and forwarded to app-defined handlers via `WebhookMetadata`. An attacker can make the app run any registered webhook handler while asserting an arbitrary target shop domain, topic, and webhook id — this is a forged-webhook acceptance, matching the Critical "authentication bypass (forged webhook … accepted)" category. Impact is repeatable against any shop domain string and any topic the target app has registered a handler for, since none of those claims need to be true of the actual signed body. The severity of consequences (e.g., a GDPR redact handler acting under a spoofed shop) depends on what the host app's handler does with `WebhookMetadata#shop`/`#topic`, but the gem provides no protection against the header spoof itself.

### Likelihood Explanation
Preconditions: the attacker needs (1) their own shop with the target app installed (freely obtainable — any developer can create a dev store and install a public/custom app), (2) a webhook delivery endpoint they control to capture one legitimate `(raw_body, hmac)` pair, and (3) knowledge of the target app's real webhook endpoint URL (typically discoverable/public). No secret material, session, or access token is required. This is a low-cost, fully repeatable HTTP replay attack requiring no privileged access.

### Recommendation
Bind the routing/attribution headers into the signed material, or re-derive `topic`/`shop`/`webhook_id` only from values the app already trusts independent of the incoming request (e.g., match `shop` against the app's own installed-shop records before acting, and never let handler dispatch or `WebhookMetadata` attribution rely solely on headers that aren't covered by `to_signable_string`). At minimum, document that `shop`, `topic`, `api_version`, and `webhook_id` are unauthenticated and must be independently verified by the host app before use in any privileged or cross-tenant-sensitive operation.

### Proof of Concept
```ruby
# test/utils/hmac_validator_relabel_test.rb
require "test_helper"

class HmacValidatorRelabelTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", api_version: "2022-01",
      scope: "read_products", is_private: false, is_embedded: true,
      host_name: "app.com", session_storage: nil,
    )
    @raw_body = '{"id":1,"name":"test"}'
    computed = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", @raw_body)
    @hmac_b64 = Base64.strict_encode64(computed)
  end

  def build_request(shop:, topic:, api_version:, webhook_id:)
    ShopifyAPI::Webhooks::Request.new(
      raw_body: @raw_body,
      headers: {
        "X-Shopify-Hmac-Sha256" => @hmac_b64,
        "X-Shopify-Topic" => topic,
        "X-Shopify-Shop-Domain" => shop,
        "X-Shopify-Api-Version" => api_version,
        "X-Shopify-Webhook-Id" => webhook_id,
      },
    )
  end

  def test_hmac_validation_ignores_shop_topic_version_webhook_id
    request_a = build_request(
      shop: "attacker-shop.myshopify.com", topic: "orders/create",
      api_version: "2022-01", webhook_id: "id-1",
    )
    request_b = build_request(
      shop: "victim-shop.myshopify.com", topic: "shop/redact",
      api_version: "2023-10", webhook_id: "id-2",
    )

    assert_equal ShopifyAPI::Utils::HmacValidator.validate(request_a),
      ShopifyAPI::Utils::HmacValidator.validate(request_b)
    assert ShopifyAPI::Utils::HmacValidator.validate(request_a)
    assert ShopifyAPI::Utils::HmacValidator.validate(request_b)
  end
end
```
This demonstrates that `HmacValidator.validate` returns `true` for both requests despite completely divergent `shop`, `topic`, `api_version`, and `webhook_id`, proving zero signature coverage over those fields.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
