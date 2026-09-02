### Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — which the app relies on to attribute the webhook to a specific merchant and event — are read directly from unauthenticated HTTP headers and are never included in the signed bytes. `Utils::HmacValidator` therefore proves only that *some* valid body was signed by Shopify with the app's secret; it proves nothing about which shop or topic that body belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` checks the `hmac` header against `HMAC(secret, to_signable_string)`, i.e., against the body alone: [3](#0-2) 

`Webhooks::Registry.process` then dispatches the handler using the unauthenticated `request.shop` and `request.topic` values, alongside the (correctly) verified body: [4](#0-3) 

The broken identity binding: `hmac == HMAC(secret, body)` is validated, but the equality that the app actually needs — `shop-domain header == shop the body was generated for` — is never checked. Any merchant that installs the app receives their own genuinely-signed webhook deliveries (valid `body` + valid `hmac`). Because the signature never binds the body to a specific shop, that same `body`/`hmac` pair remains valid when replayed with an arbitrary `x-shopify-shop-domain` header pointing at a different, victim shop. The app's `WebhookHandler` will process the payload believing it originated from the victim shop.

### Impact Explanation
This crosses a tenant boundary: an attacker who legitimately installs the app on their own shop can obtain a validly-signed webhook body/HMAC pair (e.g. from `orders/create` on their own store) and resend it to the app's webhook endpoint with a forged `shop-domain` header identifying a different, victim shop. `HmacValidator.validate` still returns `true` because the signature never covered the shop identity, and `Registry.process` calls the handler with `shop: <victim shop>` and the attacker-controlled body. Any app logic keyed off `data.shop` (e.g., updating that shop's records, triggering shop-scoped side effects, writing to per-shop storage) is now attacker-controlled cross-tenant, meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Any unprivileged internet user can install the target app on their own (attacker-controlled) shop for free, capture one legitimately-signed webhook delivery, and replay it against the app's public webhook endpoint with a modified `shop-domain` header — no access token, `api_secret_key`, or privileged account is required. This requires no cooperation from Shopify beyond normal app installation.

### Recommendation
Bind the header-derived identity fields into the signed content, or otherwise verify them out-of-band before trusting them:
- Include `shop-domain`, `topic`, and `webhook-id` in the value that is HMAC-verified (e.g., sign `"#{shop}\n#{topic}\n#{webhook_id}\n#{raw_body}"` instead of `raw_body` alone), matching what the sending side (Shopify) actually authorizes for that delivery, or
- At minimum, cross-check the `shop-domain` header against an expected/registered shop for the given `webhook_id`/subscription before dispatching to a handler, so a valid-body-wrong-header replay is rejected.

### Proof of Concept
1. Install the target Shopify app on an attacker-owned shop `attacker-shop.myshopify.com`.
2. Trigger a real event (e.g. create an order) so Shopify sends a legitimately-signed webhook to the app's endpoint:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   ```
3. Capture the raw request `body` and `x-shopify-hmac-sha256` value.
4. Replay the same `body` and `hmac` header to the app's webhook endpoint, but swap the shop header:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same valid HMAC, unchanged>
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
5. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` (it only checks `body` against the secret), and `ShopifyAPI::Webhooks::Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker's body — demonstrating that the shop identity is not authenticated by the HMAC. [5](#0-4) [6](#0-5) [4](#0-3)

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
