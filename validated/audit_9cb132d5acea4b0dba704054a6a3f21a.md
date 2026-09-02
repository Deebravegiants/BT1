### Title
Webhook shop/topic identity is not covered by HMAC signature, allowing header-spoofed cross-tenant replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, while `topic`, `shop`, `webhook_id`, and `api_version` are read directly from HTTP headers that are never part of the signed material. `Registry.process` validates only the body's HMAC and then dispatches the handler using the unvalidated `request.topic`/`request.shop` values, so an attacker who possesses one genuinely-signed body/HMAC pair (e.g., from their own development shop) can replay it with a forged `x-shopify-shop-domain` (and/or `x-shopify-topic`) header and have the app treat it as belonging to an arbitrary shop/topic.

### Finding Description
The invariant that should hold is: `signed_string == everything the handler treats as authenticated`, i.e. `to_signable_string ⊇ {shop, topic, webhook_id, api_version}`. In this code, that binding is broken: [1](#0-0) 

`to_signable_string` returns only `@raw_body` [2](#0-1) , while `topic`, `shop`, `api_version`, and `webhook_id` are all pulled straight from attacker-controlled headers via `shopify_header` [3](#0-2) . `initialize` only checks that the `topic`, `hmac-sha256`, and `shop-domain` headers *exist* — never that their values match anything cryptographically bound to the body [4](#0-3) .

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against `verifiable_query.hmac` [5](#0-4) . Because `to_signable_string` is body-only, this check is blind to `shop`/`topic`.

`Registry.process` then dispatches trusting these unvalidated fields: it validates the HMAC, looks up the handler by `request.topic`, and calls `handler.handle` with `shop: request.shop` taken straight from the header [6](#0-5) .

Exploit flow: the attacker creates their own development shop, installs the app, and receives a genuinely Shopify-signed webhook (valid `raw_body` + valid `x-shopify-hmac-sha256`). They replay this exact body/HMAC pair to the app's webhook endpoint but substitute `x-shopify-shop-domain` (and optionally `x-shopify-topic`) with a victim shop's domain or a different topic string. `HmacValidator.validate` still passes because the body bytes and secret are unchanged and the shop/topic headers were never part of the signed input. `handler.handle` executes with `shop: <attacker-chosen value>`, so the app processes the payload as if it originated from a shop it did not.

No existing guard closes this gap: `HmacValidator.validate` only checks body-vs-HMAC equality, and `Request#initialize` performs presence checks on headers, never a content/format or cross-field binding check.

### Impact Explanation
An unprivileged attacker who has legitimately received at least one signed webhook for their own shop can cause the target app to process that payload under an arbitrary attacker-chosen shop domain (and/or topic), since `request.shop`/`request.topic` drive downstream handler logic (e.g., tenant lookup, data attribution, mandatory-compliance topics like `shop/redact`, `customers/redact`, `customers/data_request`). This is a cross-tenant identity confusion: one tenant's signed data is attributed to another tenant of the attacker's choosing. It is repeatable indefinitely against any victim shop domain the attacker can guess or enumerate, using the same signed body each time.

### Likelihood Explanation
Preconditions: the host app must actually branch handler behavior on `request.shop`/`request.topic` (which is the documented use of `WebhookMetadata`), and the attacker needs one legitimately signed webhook body (trivially obtainable by installing the app on their own dev shop and triggering any webhook). No secrets, tokens, or privileged access are required — only the ability to POST HTTP requests with custom headers to the app's public webhook endpoint. This makes the attack low-cost and fully repeatable.

### Recommendation
Include `shop`, `topic`, and `webhook_id`/`api_version` header values in the signable string (or otherwise cryptographically bind them to the raw body verification), so that `HmacValidator.validate` fails if any of these header values are altered independently of the body that was actually signed by Shopify.

### Proof of Concept
```ruby
# test/webhooks/request_spoof_test.rb
require "test_helper"

class RequestSpoofTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
    @body = '{"id":1}'
    @hmac = Base64.encode64(OpenSSL::HMAC.digest("sha256", "secret", @body)).strip
  end

  def test_same_signed_body_accepted_for_two_different_shops
    headers_shop_a = {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => @hmac,
      "x-shopify-shop-domain" => "shop-a.myshopify.com",
    }
    headers_shop_b = headers_shop_a.merge("x-shopify-shop-domain" => "shop-b.myshopify.com")

    req_a = ShopifyAPI::Webhooks::Request.new(raw_body: @body, headers: headers_shop_a)
    req_b = ShopifyAPI::Webhooks::Request.new(raw_body: @body, headers: headers_shop_b)

    assert ShopifyAPI::Utils::HmacValidator.validate(req_a)
    assert ShopifyAPI::Utils::HmacValidator.validate(req_b)
    refute_equal req_a.shop, req_b.shop # both pass validation with same signature, different shop
  end
end
```
Both requests pass `HmacValidator.validate` with the identical signature, while `request.shop` differs — demonstrating that the shop identity handed to the webhook handler via `Registry.process` is not bound to the HMAC.

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
