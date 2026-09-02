### Title
Webhook `shop-domain` and `topic` headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and exposes an HMAC that only signs the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` validates only the body HMAC and then forwards the header-derived `shop`/`topic` values, unauthenticated, to the app's webhook handler. This breaks the identity binding `hmac_signed_bytes == bytes_the_app_acts_on`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#hmac` decodes the `hmac-sha256` header [2](#0-1) . `Utils::HmacValidator.validate` verifies only that this body-derived signature matches `Context.api_secret_key` [3](#0-2) .

However, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers with no cryptographic relationship to the signed body [4](#0-3) . `Registry.process` raises only if the body HMAC fails, then immediately constructs the handler payload from these unauthenticated header fields: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))` [5](#0-4) .

The identity binding that should hold is:
`HMAC_valid(body) == (shop, topic used by handler are the same shop/topic that Shopify actually generated that body for)`

In this implementation the equality does not hold: `HMAC_valid(body)` is true whenever *any* previously-issued genuine `(body, hmac)` pair is replayed, regardless of the `shop-domain`/`topic` headers sent alongside it. An unprivileged internet user who legitimately receives even one webhook for their own installed shop (a normal recipient of the app, requiring no `api_secret_key`, access token, or other privileged credential) can capture that valid `(raw_body, hmac-sha256)` pair and replay it to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` and `x-shopify-topic` header. `HmacValidator.validate` will still pass because it only checks the raw body against the secret, and `Registry.process` will hand the (now attacker-chosen) `shop`/`topic` values to the handler as if authenticated.

### Impact Explanation
Applications built on this gem are documented to trust `WebhookMetadata#shop` and `#topic` as the authenticated identity of the webhook (this is the entire purpose of these fields on the metadata object handed to the handler). Because `shop` and `topic` are not bound to the HMAC, a replayed genuine payload can be attributed to a different shop/topic than the one it actually came from. Any handler that uses `data.shop` to select which tenant's records to create/update/delete (a common and expected usage pattern for multi-tenant Shopify apps) can be made to apply another shop's webhook body/action under a forged shop identity, or misclassify data as a different topic than it truly is. This constitutes cross-tenant data confusion/misattribution, which lands in the Critical impact bucket (cross-tenant access) defined by the scan's rules.

### Likelihood Explanation
Likelihood is high because: (1) obtaining a single valid `(raw_body, hmac)` pair requires nothing more than being a normal, unprivileged recipient of one real webhook (e.g., an attacker installs the app on their own shop, triggers any webhook-worthy event, and captures the request that Shopify sends); (2) no `api_secret_key`, access token, or other privileged material is needed to forge the header values, since only the body is signed; (3) the vulnerable code path (`Registry.process` / `HmacValidator.validate` / `Request#shop`/`#topic`) is exercised on every webhook delivery and is part of the gem's own logic, not something the host app must misuse — it is directly reachable via the documented `Registry.process` entry point.

### Recommendation
Bind the `shop-domain`, `topic`, `webhook_id`, and `api_version` headers into the signed material verified by `HmacValidator`, or otherwise cryptographically/structurally tie them to the signed body (e.g., include them in `to_signable_string`, or independently verify `shop` against a list of shops the app has legitimately installed for, keyed by the access token used to register that specific webhook subscription). At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated header echoes and must not be trusted for tenant-scoping decisions without additional verification (e.g., cross-checking against the shop associated with a known, previously stored session/webhook registration).

### Proof of Concept
1. Attacker installs the app on their own shop (`attacker-shop.myshopify.com`) and triggers any subscribed webhook topic (e.g. `orders/create`), capturing the genuine request Shopify sends to the app's webhook endpoint, including headers:
   - `x-shopify-hmac-sha256: <valid_hmac_of_body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
   - raw body: `{"id": 123, ...}` (attacker's own order data)
2. Attacker replays the exact same raw body and `x-shopify-hmac-sha256` value to the same webhook endpoint, but changes:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - (optionally) `x-shopify-topic` to a different registered topic
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, @raw_body)` against the (unchanged) valid signature [6](#0-5) .
4. `Registry.process` then invokes the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's order data>, ...)` [7](#0-6) , causing the host application to process the attacker's data under the victim shop's identity/tenant scope — an authenticated-looking but forged cross-tenant webhook. [8](#0-7) [5](#0-4) [9](#0-8)

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
