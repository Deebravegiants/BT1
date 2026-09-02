### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, entirely outside the HMAC-covered bytes [2](#0-1) . `Registry.process` validates only the body HMAC and then unconditionally trusts `request.shop` when building the `WebhookMetadata` handed to the app's handler [3](#0-2) . This breaks the intended binding `HMAC(secret, raw_body) == received_hmac` should imply `shop == tenant-that-produced-this-body`; instead the equality only certifies the body content, not which tenant it belongs to.

### Finding Description
The gem's own documentation instructs host apps to trust `data.shop` from `WebhookMetadata` as the identifier of the shop the webhook is for, and to key downstream actions (e.g. `perform_later(topic: ..., shop_domain: data.shop, ...)`) off of it [4](#0-3) . `Registry.process` is documented as verifying "the request did indeed come from Shopify" before invoking the handler [5](#0-4) , implying the shop attribution can be relied upon once HMAC validation passes.

In practice, `HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC [6](#0-5) , and for webhooks that signable string is exclusively the raw JSON body [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` headers are read independently and are not part of the signed payload [7](#0-6) . Consequently, given any single (body, hmac) pair that once validated successfully for shop A, that exact pair remains valid if replayed with the `shop-domain` header changed to shop B — `Registry.process` will pass HMAC validation and dispatch to the handler with `shop: "shop-b.myshopify.com"` even though the body was never produced for shop B [3](#0-2) .

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler receives an attacker-controlled tenant identifier (`shop`) paired with data that legitimately belongs to a different, unrelated shop, while the HMAC check gives false assurance that the whole payload (including the shop attribution) is authentic. Any host application that follows the documented pattern of trusting `data.shop` to route data, apply per-tenant authorization, or persist records keyed by shop (as literally shown in the gem's own docs example) is exposed to writing/attributing one merchant's data into another merchant's account — a cross-tenant access issue.

### Likelihood Explanation
Exploitation requires the attacker to obtain one legitimately-signed (body, hmac) pair (e.g. via network capture, logging, or a previously delivered webhook they can observe such as one for their own shop or a public/low-sensitivity topic), then POST it to the app's public webhook endpoint with a forged `x-shopify-shop-domain` header. Since HMAC validation never touches the header, this requires no knowledge of `api_secret_key`. This is a realistic “unprivileged internet user” capability against the app's public webhook route, and does not require any credential.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the signable material, or otherwise require the host application to independently verify that `request.shop` corresponds to a shop for which this exact `webhook_id`/body combination was actually registered/expected, rather than trusting the header purely because the body-only HMAC validated. At minimum, document prominently that `data.shop` is unauthenticated relative to the HMAC and must not be used as the sole tenant boundary without additional verification (e.g., cross-checking against a webhook_id/shop registry recorded at subscription time).

### Proof of Concept
```ruby
# Attacker captures one legitimate webhook delivery for shop-a.myshopify.com:
body = '{"id":123,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
headers_shop_a = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "shop-a.myshopify.com",
}

# Attacker replays the same (body, hmac) but swaps the shop-domain header:
headers_shop_b = headers_shop_a.merge("x-shopify-shop-domain" => "shop-b.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers_shop_b)
ShopifyAPI::Webhooks::Registry.process(request)
# HMAC validation succeeds (it only checks `body`), and the handler is invoked with
# data.shop == "shop-b.myshopify.com" even though the body was signed for shop-a.
``` [8](#0-7) [3](#0-2)

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

**File:** docs/usage/webhooks.md (L12-26)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
