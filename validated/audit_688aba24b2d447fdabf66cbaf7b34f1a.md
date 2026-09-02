Confirmed: the documented usage explicitly tells the app author `Registry.process` "will verify the request did indeed come from Shopify" (implying the whole request is authenticated), then hands the app a `WebhookMetadata` including `data.shop` for the app to act on directly, per `docs/usage/webhooks.md` lines 125-136 and `test/webhooks/registry_test.rb` lines 218-239. The gem itself is responsible for asserting the shop/topic came from that HMAC-verified request, not the host app — so this is a bug in the gem's own claimed guarantee, not host-app misuse.

### Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before invoking the app's handler with the webhook's shop domain and topic. In reality, the HMAC only covers the raw request body; the `shop-domain` and `topic` HTTP headers are read directly from attacker-controllable input and passed to the handler unauthenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, and its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop` and `topic` are read straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only checks `to_signable_string` (the body) against the app's `client_secret`: [3](#0-2) 

Then it dispatches to the app's handler using the *unauthenticated* `request.shop` and `request.topic`: [4](#0-3) 

The identity binding that should hold is: `hmac(client_secret, body)` valid ⇒ `(body, shop, topic)` triple is authentic. Instead the gem only proves `hmac(client_secret, body)` valid ⇒ `body` is authentic; `shop` and `topic` are unauthenticated header values silently trusted as if they'd been verified. Critically, `client_secret` (the app's `api_secret_key`) is *shared across every merchant* that installs the app — it is not per-shop. An attacker can legitimately install the target app on their own free/dev store, capture a genuinely-signed webhook (valid `hmac` for a known raw body), then replay that exact `raw_body`+`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header to name a victim merchant's shop domain. `Utils::HmacValidator.validate` still returns `true` (it only checked the body), and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the forged victim shop.

### Impact Explanation
This breaks the tenant isolation the gem's documentation promises host apps can rely on. Any app that keys persistence, cache invalidation, GDPR/data-erasure actions, or entitlement checks off `data.shop` (exactly as shown in the gem's own webhook doc example: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to apply an attacker-chosen payload to a different merchant's record, or to trigger shop-scoped side effects (e.g. deleting/creating resources, revoking access, redeeming discount data) attributed to a shop the attacker doesn't own. This is a cross-tenant access vulnerability arising purely from this gem's incomplete signature verification.

### Likelihood Explanation
No credentials, tokens, or privileged access are required beyond the ability to install the target app on any shop (including a free development store) — something any internet user can do for a public embedded app. The attacker only needs one genuinely-signed webhook body/HMAC pair for a topic the app subscribes to, which is trivially obtainable by triggering the corresponding event (e.g. `app/uninstalled`, `orders/create`) on their own store, then replaying it with a modified `shop-domain` header directly to the app's public webhook endpoint.

### Recommendation
Include `shop-domain` and `topic` (and any other header fields the handler will trust) in the HMAC-signed material, or otherwise cryptographically bind them to the verified body before constructing `WebhookMetadata`. At minimum, `Utils::HmacValidator.validate` should be changed so `VerifiableQuery#to_signable_string` for `Webhooks::Request` incorporates the shop and topic headers, and `Registry.process` should reject requests where headers were altered after signing.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and receives a legitimate webhook, e.g. for topic "customers/data_request":
#      headers: {
#        "x-shopify-topic" => "customers/data_request",
#        "x-shopify-hmac-sha256" => "<real-signature-for-body>",
#        "x-shopify-shop-domain" => "attacker.myshopify.com"
#      }
#      raw_body: '{"customer": {"id": 123, "email": "attacker@example.com"}}'
#
# 2. Attacker replays the exact same raw_body + hmac header, but swaps only
#    the shop-domain header to a victim shop the attacker does not control:

require "net/http"
require "uri"

uri = URI("https://victim-app.example.com/webhooks/customers_data_request")
raw_body = '{"customer": {"id": 123, "email": "attacker@example.com"}}'

headers = {
  "x-shopify-topic" => "customers/data_request",
  "x-shopify-hmac-sha256" => "<real-signature-for-body>",  # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",   # forged
}

Net::HTTP.post(uri, raw_body, headers)

# 3. On the server:
#    ShopifyAPI::Webhooks::Registry.process(
#      ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
#    )
# HmacValidator.validate returns true (body/hmac match), and the handler
# receives WebhookMetadata with shop == "victim-shop.myshopify.com",
# despite the request never having originated from Shopify for that shop.
``` [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-63)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end

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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
