### Title
Webhook `shop` (and `topic`/`webhook_id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body via `Utils::HmacValidator.validate(request)` [1](#0-0) . However, the `Request#to_signable_string` method used as the HMAC digest input returns only `@raw_body` [2](#0-1) . The `shop` (and `topic`, `webhook_id`) values are read straight from HTTP headers and are never included in the signed material [3](#0-2) . After a valid HMAC check, `Registry.process` builds a `WebhookMetadata` object using this unauthenticated `request.shop` value and dispatches it to the handler as the tenant identity [4](#0-3) .

### Finding Description
The binding that should hold is:
`shop header value == shop bound inside the HMAC-signed payload`

but in this implementation the equality is broken: `HmacValidator.validate_signature` only recomputes and compares HMAC over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is exactly `@raw_body` [5](#0-4) [6](#0-5) . The `x-shopify-shop-domain`/`shopify-shop-domain` header is read independently via `shop` and `shopify_header` and participates in no cryptographic check [7](#0-6) .

Because a valid `(raw_body, hmac)` pair can be legitimately obtained by anyone who owns a Shopify shop and installs the app (a normal, unprivileged action), an attacker can:
1. Install the target app on their own shop and capture a genuine webhook delivery — a valid `raw_body` and its correct `x-shopify-hmac-sha256` value, both signed with the app's real `api_secret_key`.
2. Replay that exact `raw_body`/HMAC pair directly to the app's public webhook endpoint, but substitute the `x-shopify-shop-domain` header with an arbitrary victim shop domain.
3. `HmacValidator.validate` still succeeds (only the body bytes are checked), so `Registry.process` calls the handler with `shop: request.shop` set to the attacker-chosen victim domain [8](#0-7) .

Any host application that uses `WebhookMetadata#shop` to key persisted state, trigger per-tenant side effects, or scope data updates will attribute the attacker's payload to the victim tenant — a cross-tenant data integrity/confidentiality break, matching the "field acted on but not covered by the HMAC" analog pattern.

### Impact Explanation
This allows an unprivileged internet user (any developer who can install the target app on a shop they control) to make the app process/emit forged webhook events under an arbitrary victim shop's identity, since the shop attribution is not cryptographically bound to the signed body. This falls under cross-tenant access.

### Likelihood Explanation
Likelihood is moderate-to-high: exploitation requires only a normal app installation (no special privilege, no leaked secret, no TLS interception) and a direct POST to the app's already-internet-exposed webhook endpoint with a modified header. The HMAC verification code path itself never inspects header consistency.

### Recommendation
Do not trust `shop`/`topic`/`webhook_id` headers as authoritative tenant identity from HMAC verification alone. Either:
- Extend `to_signable_string` (or a separate check in `Registry.process`) to bind the `shop-domain`, `topic`, and `webhook-id` header values into the verified digest, or
- Cross-validate `request.shop` against the shop id embedded in the JSON body payload (Shopify webhook bodies typically include the resource's owning shop) before dispatching to handlers, or
- Track/require app-registered `(webhook_id, shop)` pairs so that mismatched shop headers are rejected even with a valid body HMAC.

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop (`attacker.myshopify.com`)
#    and captures a real webhook delivery. Shopify signs the raw body with the
#    app's real api_secret_key:
raw_body = '{"id": 1, "note": "attacker-controlled payload"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# 2. Attacker replays the exact same body+hmac to the app's public webhook
#    endpoint, but swaps the shop-domain header to a victim shop they do not own:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

# 3. HMAC validation succeeds because only raw_body is checked:
request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
``` [9](#0-8) [1](#0-0) [10](#0-9)

### Citations

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
