The docs explicitly document `data.shop` (line 14 of `docs/usage/webhooks.md`) as "The shop domain of the webhook" — a trusted, verified field for the handler to key business logic on. The library's own `process` method calls `Utils::HmacValidator.validate(request)` and, upon success, unconditionally forwards `request.shop` to the handler. This confirms the root cause is in the gem itself (`Registry.process` + `Request#to_signable_string`), not a documented-but-ignored requirement from the host app.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header spoofing bypasses HMAC — cross-tenant webhook injection - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only authenticates the JSON body against the app's `api_secret_key` [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from HTTP headers [3](#0-2)  and are never included in the HMAC-covered bytes, yet `Registry.process` trusts them and hands `request.shop` directly to the app's handler once the body HMAC checks out [4](#0-3) .

### Finding Description
The binding that should hold is: **bytes verified by HMAC == bytes the handler acts on for tenant identity**. Instead:
- HMAC-verified bytes = `raw_body` only.
- Bytes acted on for tenant identity = `shop` header (plus `topic`, `webhook_id`, `api_version`), none of which are part of `to_signable_string`.

Because the app's `api_secret_key` is shared across every shop that installs the app, any merchant who installs the app (an unprivileged, ordinary user of the app) can legitimately trigger a webhook for their own shop and capture a valid `(raw_body, hmac)` pair. They can then replay that exact body/HMAC pair directly to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still returns `true` because it only recomputes the signature over `raw_body` [5](#0-4) , and `Registry.process` forwards the forged `shop` value unchanged into `WebhookMetadata` for the handler [6](#0-5) .

The gem's own documentation instructs handler authors to treat `data.shop` as "The shop domain of the webhook" and to key business logic on it directly (e.g. `shop_domain: data.shop`), reinforcing that this field is meant to be trusted once `Registry.process` succeeds.

### Impact Explanation
This breaks the tenant-isolation guarantee the gem is supposed to provide via HMAC verification: `authenticated tenant == acted-upon tenant`. An attacker who is merely a legitimate installer of the app on their own shop can inject fabricated (but validly-signed-body) webhook events attributed to any other shop, causing the host app to run per-tenant side effects (data updates, uninstall/redact logic for `shop/redact`, `customers/redact`, `customers/data_request`, cache invalidation, notification triggers, etc.) against a victim tenant's records. This is a cross-tenant access vulnerability rooted entirely in this gem's webhook verification logic.

### Likelihood Explanation
Likelihood is high for any multi-tenant app: the attacker only needs the ability to install the app on a shop they control (a standard, unprivileged capability for any Shopify merchant/dev), which lets them mint valid `(body, hmac)` pairs signed with the shared `api_secret_key`. No access token, no leaked secret, and no privileged account is required — only header manipulation on the replayed HTTP request.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signable string, or otherwise cryptographically bind them to the body signature, so that `to_signable_string` covers every field the handler relies on for tenant attribution. Alternatively, have `Registry.process` reject/require the app to cross-check `request.shop` against the shop that owns the specific `webhook_id`/subscription before invoking the handler.

### Proof of Concept
```ruby
# Attacker installs the app on shop-a.myshopify.com (legitimate action)
# and captures a real webhook delivery for their own shop:
raw_body = '{"id":123,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker replays the same body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to the victim shop:
forged_headers = {
  "x-shopify-topic" => "customers/redact",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => passes HMAC validation (body matches) and invokes the app's handler
#    with data.shop == "victim-shop.myshopify.com", even though the request
#    never originated from Shopify for that shop.
``` [7](#0-6) [4](#0-3) [8](#0-7) [9](#0-8)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-73)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
    end
  end
end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L1-44)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Utils
    module HmacValidator
      extend T::Sig

      class << self
        extend T::Sig

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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
      end
    end
  end
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
    end
  end
end
```
```
