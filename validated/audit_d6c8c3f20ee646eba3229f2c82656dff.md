## Analysis Result

### Title
Webhook shop-domain and topic identity is not bound by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the signable string used for HMAC verification from the raw HTTP body only, while the `shop`, `topic`, `webhook-id`, and `api-version` values used to route and label the webhook are taken directly from unauthenticated HTTP headers. `Registry.process` trusts these header-derived values after validating only the body's HMAC, so a caller who possesses *any* validly-signed webhook body for the app (trivially obtainable by triggering an event on their own installed store) can replay that exact body with a forged `shop-domain` header and have it processed as if it came from a different, victim tenant.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body` — it does not include `shop`, `topic`, `webhook_id`, or `api_version`: [2](#0-1) 

Those four fields are instead read straight from HTTP headers with no cryptographic binding: [3](#0-2) 

`Registry.process` validates the HMAC (over the body only) and then dispatches the handler using the *unauthenticated* `shop` and `topic` values: [4](#0-3) 

The identity binding this breaks, as an equality that the library should enforce but doesn't:
`HMAC_signed_bytes == (raw_body, shop, topic, webhook_id, api_version)` — but in reality only `HMAC_signed_bytes == raw_body`.

Because Shopify signs webhooks with the app's single `client_secret` shared across every installed shop, any shop that has installed the app can legitimately trigger a webhook with an app-secret-valid HMAC for some body. Since `shop`/`topic`/`webhook_id` are not part of the signed material, that exact `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with `x-shopify-shop-domain` and `x-shopify-topic` headers rewritten to name a different shop/topic. The library will accept it, and `Webhooks::Registry.process` will call the registered handler with `WebhookMetadata` claiming it came from the forged shop and topic: [5](#0-4) 

### Impact Explanation
This crosses a tenant boundary: an app relies on this gem to authenticate that a webhook body genuinely originates from the shop named in its `shop-domain` header before acting on it (e.g., updating that shop's local records, billing state, or triggering side effects). Because `shop` and `topic` are excluded from the HMAC-covered bytes, an unprivileged holder of any one valid-app-secret-signed webhook can forge webhooks attributed to *any other* tenant of the app, and can also relabel the topic to route the body into a different handler than Shopify intended. This is cross-tenant data injection through an identity field that is verified as present but never verified as authentic.

### Likelihood Explanation
Exploitability requires only: (1) being a legitimate but unprivileged user of the app on some shop (installing a free/dev app is trivial), (2) triggering any webhook event on that shop to obtain a validly HMAC-signed body, and (3) replaying the raw body/HMAC pair to the app's webhook endpoint with rewritten `shop-domain`/`topic` headers. No access token, `client_secret`, or privileged account is needed — this is reachable by any internet user who can install the target app on a store they control, which is the normal, unprivileged app-installation flow.

### Recommendation
Include `shop`, `topic`, and (where relevant) `webhook_id`/`api_version` in the signable string used for HMAC verification in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the header-derived routing/identity fields to the signed payload so a body's signature cannot be replayed under a different shop/topic identity.

### Proof of Concept
```ruby
# Attacker legitimately installs the app on their own shop "attacker.myshopify.com"
# and triggers an "orders/create" webhook, capturing the raw body Shopify sent
# along with the real x-shopify-hmac-sha256 header (valid because it's HMAC'd
# with the app's shared client_secret over the body only).

raw_body = captured_raw_body            # from attacker's own shop's real webhook
real_hmac_header = captured_hmac_header # valid Base64 HMAC-SHA256 over raw_body

forged_headers = {
  "x-shopify-topic" => "orders/create",          # can even relabel topic
  "x-shopify-hmac-sha256" => real_hmac_header,    # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged tenant
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes (lib/shopify_api/utils/hmac_validator.rb) because it only
#    checks raw_body, and the registered "orders/create" handler is invoked believing
#    the event came from "victim-shop.myshopify.com".
``` [6](#0-5) [7](#0-6) [4](#0-3)

### Citations

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
