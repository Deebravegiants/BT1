### Title
Unauthenticated `topic` and `shop-domain` headers accepted as authenticated identity in `Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::HmacValidator.validate` only verifies the HMAC over `Request#to_signable_string`, which is the raw request body [1](#0-0) . The `topic` and `shop` values used by `Registry.process` to select the handler and populate `WebhookMetadata` are read directly from unauthenticated headers and are never covered by that signature [2](#0-1) . An attacker who obtains any one validly-signed webhook body for a shop they control can replay that exact body to the app's webhook endpoint with a different `x-shopify-topic` and/or `x-shopify-shop-domain` header, and the HMAC check still passes.

### Finding Description
The binding the code implicitly relies on is:
`HmacValidator.validate(request) == true` ⟹ `request.topic` and `request.shop` are the topic/shop that Shopify actually signed for this body.

Tracing the code shows this is false:
- `initialize` only requires the three headers to be *present*, not that they correspond to the signed payload [3](#0-2) .
- `hmac` is read from the `hmac-sha256` header and compared, via `HmacValidator.validate_signature`, against `HMAC(secret, to_signable_string)` where `to_signable_string` returns only `@raw_body` [4](#0-3) [1](#0-0) .
- Neither `topic` nor `shop` (nor `api-version`/`webhook-id`) is folded into `to_signable_string`, so they are never authenticated by the signature.
- `Registry.process` first calls `HmacValidator.validate(request)` (a body-only check), then unconditionally trusts `request.topic` to select the handler and `request.shop` to build `WebhookMetadata`, which is handed to the app's handler as the tenant identity [5](#0-4) .

Exploit flow: the attacker (per the threat model) creates a development shop, installs the app, and registers a webhook, causing Shopify to send them one legitimately HMAC-signed callback (any topic, e.g. `orders/create`) with a body `B`. The attacker then POSTs `B` unmodified straight to the app's public webhook endpoint, but swaps `x-shopify-topic` to a different registered topic (e.g. one whose handler performs a privileged, shop-scoped action) and/or swaps `x-shopify-shop-domain` to a victim merchant's domain. `HmacValidator.validate` still succeeds because it only checks `B` against the secret; `Registry.process` dispatches to the relabelled topic's handler with `shop:` set to the forged/victim domain. If the host app's handler uses `WebhookMetadata#shop` to look up a stored session/access token (the documented, expected usage pattern for webhook handlers) and perform an authenticated Admin API action, it now does so with the victim's token/tenant context under attacker-chosen topic semantics — a confused-deputy across shops.

No guard in this gem prevents this: `HmacValidator.validate` is body-only by construction; `ShopValidator.sanitize!` is never invoked in the webhook path; there is no per-topic or per-shop binding in the signed content; Sorbet typing only enforces the header values are non-nil strings, not that they match the signed body.

### Impact Explanation
Any app that keys token/session lookup or shop-scoped side effects off `WebhookMetadata#shop` (the value returned by `Webhooks::Request#shop`) can be made to act on behalf of a shop/topic the attacker did not actually receive a callback for, using a body the attacker fully controls (their own shop's data). This breaks the single-identity invariant (signed body ↔ topic ↔ shop must be one authenticated unit) and can be leveraged for cross-tenant confusion or to trigger privileged handlers under an unintended topic, matching the "cross-tenant access" / credential-exposure class. The severity depends entirely on what the host app's handler does with `shop`/`topic`, which is outside this gem — the gem's contribution is that it hands out `topic` and `shop` as if they were authenticated by the passing HMAC check, when they are not.

### Likelihood Explanation
Low attacker cost: the attacker only needs a working dev shop and one legitimate webhook delivery to themselves (explicitly permitted in the threat model), then can replay the same body indefinitely with arbitrary topic/shop headers to the app's public webhook URL. No secrets are required. However, real-world exploitability is entirely dependent on how the host application's webhook handler uses `shop`/`topic` — the gem itself does not perform any privileged action, it only supplies the (potentially mismatched) values to the app-provided `WebhookHandler#handle`.

### Recommendation
Do not treat `topic`/`shop-domain` headers as authenticated merely because the body HMAC validates. Either (a) include the topic and shop-domain in the signable string used for HMAC comparison so any relabelling invalidates the signature, or (b) document/require host apps to cross-check `WebhookMetadata#shop` against the shop associated with the delivery out-of-band (e.g., via the registered callback URL per shop, or session lookup with additional binding), and avoid deriving trust solely from `Registry.process`'s current header-based dispatch.

### Proof of Concept
```ruby
# test/webhooks/registry_topic_relabel_test.rb
require_relative "../test_helper"

class RegistryTopicRelabelTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_signed_body_can_be_relabelled_to_a_different_topic
    body = { id: 1, note: "attacker's own shop data" }.to_json
    hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
    hmac_header_value = Base64.encode64(Digest.hexencode(hmac)) # inverse of Request#hmac decode

    received_shop = nil
    received_body = nil

    handler_a = Class.new(ShopifyAPI::Webhooks::WebhookHandler) do
      define_method(:handle) { |data:| }
    end.new
    handler_b = Class.new(ShopifyAPI::Webhooks::WebhookHandler) do
      define_method(:handle) do |data:|
        received_shop = data.shop
        received_body = data.body
      end
    end.new

    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", delivery_method: :http, path: "/webhooks", handler: handler_a,
    )
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "shop/update", delivery_method: :http, path: "/webhooks", handler: handler_b,
    )

    # Attacker replays the SAME signed body under a different topic and forged shop-domain
    forged_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: body,
      headers: {
        "x-shopify-topic" => "shop/update",              # relabelled, unsigned
        "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, unsigned
        "x-shopify-hmac-sha256" => Base64.encode64([hmac].pack("H*")),
      },
    )

    ShopifyAPI::Webhooks::Registry.process(forged_request)

    # HMAC over the body validated successfully, yet topic/shop were attacker-chosen,
    # proving topic/shop are not bound to the signed content.
    assert_equal("victim-shop.myshopify.com", received_shop)
    assert_equal(JSON.parse(body), received_body)
  end
end
```
This demonstrates that `HmacValidator.validate` passes while `topic` and `shop` diverge from anything actually signed by Shopify, confirming the broken binding.

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

**File:** lib/shopify_api/webhooks/request.rb (L46-63)
```ruby
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
