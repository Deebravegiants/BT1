This confirms the vulnerability: the webhook `shop` (and `topic`, `api_version`, `webhook_id`) are read directly from HTTP headers and are **never included in the HMAC-signed payload**. `Utils::HmacValidator.validate` only recomputes the signature over `to_signable_string`, which for `Webhooks::Request` returns `@raw_body` — the headers are entirely outside the cryptographic boundary.

### Title
Webhook `shop` identity is trusted from an unauthenticated header while only the raw body is HMAC-verified - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC signature (validated in `ShopifyAPI::Webhooks::Registry.process`) proves nothing about the `shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, or `shopify-webhook-id` headers. Those header values are passed straight into `WebhookMetadata` and handed to the app's webhook handler as the trusted tenant identifier.

### Finding Description
`Webhooks::Request#shop`, `#topic`, `#api_version`, and `#webhook_id` all read directly from request headers with no cryptographic binding: [1](#0-0) 

`Registry.process` verifies the HMAC and then immediately trusts `request.shop`/`request.topic` to build the metadata delivered to the app's handler: [2](#0-1) 

The equality that should hold is: `shop-in-header == shop-covered-by-hmac`. Instead, the HMAC only covers `raw_body`, so `shop-in-header` is unauthenticated. `Utils::HmacValidator.validate` simply recomputes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the header-supplied `hmac-sha256` value: [3](#0-2) 

Because the app's `client_secret` (`api_secret_key`) is a single, app-wide secret shared across every merchant that installs the app — not a per-shop secret — any merchant who legitimately installs the app receives real webhook deliveries with a valid `hmac-sha256` for their own shop's `raw_body`. That attacker-controlled merchant can capture one such legitimately-signed `(raw_body, hmac)` pair from their own store, then replay the exact same body to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and optionally `shopify-topic`/`shopify-webhook-id`) to point at a victim shop. `HmacValidator.validate` still succeeds because it only re-signs `raw_body`, which is unchanged. The app then processes attacker-supplied data as if it originated from the victim shop, since `request.shop` is passed unauthenticated into `WebhookMetadata`.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce: an app built on this gem's `Registry.process`/`Webhooks::Request` cannot distinguish "genuine data from shop A" from "attacker-replayed data falsely labeled as shop A." A malicious app installer can inject forged webhook events attributed to any other shop that has installed the same app, corrupting per-tenant state (e.g. triggering order/fulfillment/customer-record side effects under another merchant's identity) — a cross-tenant data integrity/confusion issue reachable by any unprivileged app installer, without needing the `client_secret` or any victim credentials.

### Likelihood Explanation
Any user who can install the app (a normal, unprivileged action) automatically becomes a source of validly-HMAC-signed webhook bodies for their own shop and can immediately attempt the header-substitution replay against the app's public webhook endpoint. No secret material, token theft, or elevated access is required — only observing one's own legitimate webhook deliveries.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed payload used for HMAC verification — e.g. bind `to_signable_string` to `"#{shop}\n#{topic}\n#{raw_body}"` — or otherwise cryptographically bind the header-derived identity fields before trusting them in `WebhookMetadata`, so that a valid signature for one shop's payload cannot be replayed under a different shop's identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook POST with header `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <validHmac>`, and some `raw_body`.
2. Attacker replays the identical HTTP request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com` (leaving `raw_body` and `X-Shopify-Hmac-Sha256` untouched).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= raw_body`, unchanged) and finds it valid.
4. `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` is invoked with `shop == "victim.myshopify.com"`, even though the body content originated from the attacker's own shop — demonstrating cross-tenant data attribution with a cryptographically "valid" webhook. [2](#0-1) [4](#0-3)

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
