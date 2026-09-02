Confirmed: the documented API explicitly promises `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`), and the `shop` field is meant to be trusted as the webhook's shop domain (`docs/usage/webhooks.md:14`, `lib/shopify_api/webhooks/webhook_handler.rb:6-9`). But the HMAC only covers the raw body, not the shop header.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop` (tenant identity) that the library hands to the app's handler is read from an unauthenticated header that is never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` gates all authentication on `Utils::HmacValidator.validate(request)` before dispatching to the handler [2](#0-1) . `HmacValidator.validate_signature` computes the HMAC only over `verifiable_query.to_signable_string`, i.e., the raw body — never the headers [3](#0-2) .

However, the `shop` value that is passed to the app's `WebhookHandler` — and that the library's own documentation instructs developers to trust as "The shop domain of the webhook" — is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, completely outside the HMAC-covered bytes [4](#0-3) . `topic`, `webhook_id`, and `api_version` are likewise taken from unsigned headers [5](#0-4) , and all of them are forwarded verbatim into `WebhookMetadata` that the handler is told to trust [6](#0-5) [7](#0-6) .

This breaks the intended binding: `hmac_valid_for(body) == authenticated_shop_and_topic_for(body)`. In reality, `hmac_valid_for(body)` only proves the body bytes were signed by Shopify with the app's secret; it proves nothing about which shop or topic that signature is "attached to" — the shop/topic pairing is attacker-suppliable metadata layered on top of a validly-signed body.

**Root cause:** `lib/shopify_api/webhooks/request.rb:20-23` (`shop` from unsigned header) combined with `lib/shopify_api/webhooks/registry.rb:190` (authentication decision based only on body HMAC) combined with `lib/shopify_api/utils/hmac_validator.rb:26-31` (signable string excludes headers).

### Impact Explanation
Any actor who can obtain one legitimately-signed (body, hmac) pair from Shopify — trivially available to any developer/attacker who installs the target app (or any app using this gem) on their own store and captures a webhook delivery for a shop they control — can replay that exact body/HMAC pair to the victim app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header pointing at a different, victim shop. Since `HmacValidator.validate` only checks the body signature, the forged request passes validation, and the app's handler receives `WebhookMetadata` claiming the event belongs to the victim shop with attacker-chosen `topic` too (e.g., mapping a captured `orders/create` body's HMAC onto a `shop/redact` or `customers/data_request` topic-shop pair, or attributing arbitrary order/customer data to a shop that never sent it). Depending on what the host application does with `data.shop`/`data.topic` (e.g., writing to per-shop records, triggering shop-scoped side effects, honoring mandatory GDPR redaction topics), this enables cross-tenant data injection/corruption — a direct violation of the "cross-tenant access" boundary this program treats as Critical.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's ability to send arbitrary HTTP requests to the target's public webhook endpoint (unprivileged internet access — webhook endpoints are unauthenticated by design), and (2) possession of any one valid (body, HMAC) pair signed with the app's secret, which is freely obtainable if the attacker is themselves a legitimate/trial merchant of the target app (extremely common for SaaS Shopify apps) or otherwise intercepts one delivered webhook. No access token, `api_secret_key`, or privileged account is needed — only knowledge of the app's own past legitimately-delivered webhook traffic for any shop, including the attacker's own.

### Recommendation
Bind the identity fields to the HMAC-signed material instead of trusting bare headers:
- Include `shop`, `topic`, `webhook_id`, and `api_version` (or at minimum `shop` and `topic`) in the bytes that are HMAC-verified, e.g., by having `to_signable_string` canonicalize a string that concatenates these header values with the raw body, and require callers/host apps to independently reject shop headers that don't match a caller-provided expected shop when known.
- At minimum, document and enforce that `request.shop` must be cross-checked by the host application against a shop actually registered/known to the app for that specific webhook subscription (Shopify's own webhook IDs are unique per subscription and could be validated against a stored expected-shop mapping) before any tenant-scoped action is taken.
- Consider adopting an HMAC construction that is computed over `"#{shop}\n#{topic}\n#{raw_body}"`, matching common signed-webhook patterns from other providers, so a captured (body, hmac) pair cannot be re-attributed to a different shop/topic.

### Proof of Concept
```ruby
# Attacker legitimately installs the target app on their own store "attacker.myshopify.com"
# and captures a real webhook Shopify sends them, e.g. for topic "customers/data_request":
raw_body     = '{"customer":{"id":123,"email":"victim@example.com"}, ...}'
valid_hmac_b64 = "<value of x-shopify-hmac-sha256 header from the captured request>"

# Attacker now replays the SAME body + SAME hmac to the target app's public
# webhook endpoint, but swaps the shop-domain header to the victim's shop:
forged_headers = {
  "x-shopify-topic"        => "customers/data_request", # attacker-chosen; unsigned
  "x-shopify-hmac-sha256"  => valid_hmac_b64,            # still valid: only body is signed
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged, unsigned field
  "x-shopify-webhook-id"   => "forged-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# This passes because HmacValidator only checks raw_body against valid_hmac_b64:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "customers/data_request",
#      shop: "victim-shop.myshopify.com", body: ..., ...))
# The host app now believes this GDPR/data event genuinely originated from victim-shop.
``` [8](#0-7) [2](#0-1) [9](#0-8)

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
