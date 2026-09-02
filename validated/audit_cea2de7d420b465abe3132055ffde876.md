This confirms the finding: the documented usage explicitly tells host apps to trust `data.shop` from `WebhookMetadata` — "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook" — implying the `shop` field is authenticated by the same process as the body. It is not; only the body is signed.I have confirmed the root cause and finalize the analog now.

### Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` reads the tenant identity (`shop`, plus `topic`, `webhook_id`, `api_version`) from HTTP headers, but its `to_signable_string` — the value the HMAC is actually computed and verified over — only returns the raw request body. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then hands the *unverified* `shop` value straight to the app's `WebhookHandler` as authoritative tenant identity. This breaks the intended binding: `shop header used to route/attribute data == shop covered by the HMAC that "proves this came from Shopify for this shop"`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all pulled straight from attacker-controllable HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)` (which calls `to_signable_string`, i.e. checks only the body), and — once that single check passes — forwards `request.shop` unchanged into `WebhookMetadata`, which is passed to the app-defined handler as trusted tenant identity: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` and the app's single, shop-independent `api_secret_key`: [4](#0-3) 

Since the same `api_secret_key` is used to sign webhooks for every shop that has the app installed, any unprivileged merchant who has installed the app on their own store can capture a legitimate, validly-signed webhook body from their own store (e.g. by triggering `orders/create`), then replay that exact body to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to point at a different (victim) shop. Because the header is not part of the signed content, `HmacValidator.validate` still returns `true`, and `Registry.process` dispatches the forged `shop` value to the handler as if Shopify itself attested that this event belongs to the victim shop.

The gem's own documentation confirms apps are meant to trust this value as authenticated: "*This will verify the request did indeed come from Shopify and then call the specified handler for that webhook*", and the handler example uses `data.shop` directly as the tenant key (e.g., `shop_domain: data.shop`) without any additional gem-level verification step being documented or available: [5](#0-4) 

This is not a case of the host app ignoring the documented API — the documented API itself hands back an unauthenticated `shop` field labeled as verified.

### Impact Explanation
This breaks the tenant isolation boundary the HMAC check is supposed to provide. An attacker who controls one shop (unprivileged, merely an app installer) can inject event data/webhook processing attributed to an arbitrary other shop of their choosing, as long as they can produce (via their own store's real events) a validly-signed body of the topic they want to forge. Depending on how the host app uses `data.shop` (e.g., to update per-shop billing state, feature flags, order records, or trigger per-shop side effects), this enables cross-tenant data corruption/injection — a cross-tenant access impact.

### Likelihood Explanation
Requires only that the attacker have (or create) an installation of the app on a shop they control — a normal, unprivileged merchant capability, not a leaked credential or privileged access. No access token, `api_secret_key`, or MITM is required; the attacker only needs to observe/replay traffic to their own webhook consumer and repoint the shop-domain header at the app's public webhook endpoint.

### Recommendation
Bind the tenant-identifying headers into the signed content (or otherwise cryptographically bind them) before trusting them: either include `shop`, `topic`, `webhook_id`, and `api_version` in `to_signable_string`, or require the caller to separately verify that `request.shop` matches a shop known/expected for that installation (e.g., cross-check against a stored session/shop record) before dispatching to the handler. At minimum, the gem's documentation should not represent `data.shop` as verified equivalent to "this came from Shopify," since only the body is actually authenticated.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed.
# 1. Attacker triggers a real event (e.g. orders/create) on their own store.
#    Shopify sends a genuine webhook to the app with a valid HMAC computed
#    over the raw body using the app's api_secret_key:
#
#    headers:
#      x-shopify-topic: "orders/create"
#      x-shopify-hmac-sha256: <valid HMAC over raw_body>
#      x-shopify-shop-domain: "attacker-shop.myshopify.com"
#    body: <attacker-controlled order JSON from their own store>

# 2. Attacker captures this raw_body + hmac and replays it to the same
#    webhook endpoint, only changing the shop-domain header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_valid_hmac, # unchanged, still valid for the body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: forged_headers)

# 3. HMAC validation passes because it only checks the body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# 4. Registry.process dispatches to the handler believing it's for victim-shop:
ShopifyAPI::Webhooks::Registry.process(request)
# handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: attacker-controlled, ...)
``` [6](#0-5) [3](#0-2) [7](#0-6)

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

**File:** docs/usage/webhooks.md (L125-135)
```markdown
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
