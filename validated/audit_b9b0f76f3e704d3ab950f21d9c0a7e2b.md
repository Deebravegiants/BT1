### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) identity fields are trusted from unauthenticated HTTP headers while only the request body is HMAC-verified - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, but the tenant-identifying `shop` field (along with `topic`, `webhook_id`, and `api_version`) is read from separate, unsigned HTTP headers and passed unmodified to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#hmac` reads the `hmac-sha256` header: [1](#0-0) 

`Registry.process` validates the HMAC against this signable string only, then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which are covered by the HMAC — and forwards them to the registered handler as `WebhookMetadata`: [2](#0-1) 

`WebhookMetadata.shop` is a plain `String` const with no further validation performed by the gem: [3](#0-2) 

The equality the gem should enforce is: `shop header authenticated by HMAC == shop attributed to the webhook payload processed by the handler`. Because the HMAC signature only binds the body bytes, this equality does not hold — the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers can be swapped for any value while keeping a previously-obtained valid `(body, hmac)` pair, and `HmacValidator.validate` will still return `true` since it only re-computes the digest over `@raw_body`: [4](#0-3) 

Since Shopify's HMAC secret (`api_secret_key`) is not known to unprivileged internet users, an attacker cannot forge an entirely new signed payload. However, an attacker who has legitimately received (or otherwise obtained) one valid `(raw_body, hmac-sha256)` pair for *any* topic/shop — e.g., from their own test store, from a public webhook sample, or by observing traffic to their own endpoint — can replay that exact body/HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop domain (and/or the `X-Shopify-Topic` header for a different topic). `HmacValidator.validate` will pass because it only checks the body signature, and `Registry.process` will dispatch the replayed body to the handler under the attacker-chosen `shop` and `topic`, since `WebhookMetadata` carries whatever the caller supplied for `shop`/`topic`, unconstrained by the signature.

### Impact Explanation
This breaks the tenant-identity binding that host applications rely on to attribute webhook data to the correct shop (`request.shop`) and to select correct processing logic (`request.topic`). An application that uses `WebhookMetadata.shop` to look up per-tenant records, apply updates, or make trust decisions (as the gem's own documentation encourages) can be made to process attacker-supplied but "HMAC-valid" data under an arbitrary victim shop's identity — i.e., cross-tenant data injection through a spoofed identity binding. This matches the Critical "cross-tenant access" impact category, since the gem itself performs no binding between the verified bytes and the shop/topic metadata it hands to the app.

### Likelihood Explanation
Exploitability requires the attacker to already possess at least one valid `(body, hmac)` pair — for example from their own development store's webhook deliveries, which are trivially obtainable by any developer with a free Shopify partner/dev shop. No access to `api_secret_key`, access tokens, or the target's credentials is required. The header fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) are fully attacker-controlled on any raw HTTP request reaching the app's public webhook endpoint, since the gem does not check them against the signed body.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signable representation (similar to how `AuthQuery#to_signable_string` binds `shop`, `host`, `code`, `state`, `timestamp` together), or otherwise cryptographically bind these header values to the signed body so that a replayed body cannot be re-attributed to a different shop/topic.

### Proof of Concept
1. Obtain one legitimate webhook delivery to a dev/test store: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Send a new HTTP request to the target app's webhook endpoint with the same body `B` and same `H`, but headers `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and (optionally) a different `X-Shopify-Topic`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds successfully; `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes the HMAC over `B`.
4. `Registry.process(request)` dispatches to the handler with `WebhookMetadata.new(topic: <attacker-chosen>, shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the app to process attacker-influenced data as if it originated from, and pertains to, the victim shop. [5](#0-4) [6](#0-5)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
