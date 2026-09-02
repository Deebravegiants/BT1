## Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the request body, but the `shop` identity that is handed to the host application's handler is read from an HTTP header that is never included in the signed material. This breaks the intended binding: `HMAC-verified bytes == bytes the shop identity is derived from`.

## Finding Description
`Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` value from the same object using `OpenSSL.secure_compare`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — the JSON body — while `hmac` and `shop` are both pulled independently from HTTP headers (`x-shopify-hmac-sha256` / `shopify-hmac-sha256` and `x-shopify-shop-domain` / `shopify-shop-domain`, respectively): [3](#0-2) [4](#0-3) 

So the HMAC only proves "this body was produced/authorized using the shop's secret key at some point"; it proves nothing about which shop's domain the request claims to be. Yet `request.shop` (the unauthenticated header value) is what gets forwarded, unmodified, straight into the merchant-identifying data passed to the app's own webhook handler: [5](#0-4) [6](#0-5) 

The identity equality the gem should enforce is: `shop value bound inside the HMAC-signed bytes == shop value delivered to the handler`. Instead it enforces only: `HMAC(body) is valid` AND separately, unauthenticated, `shop header == whatever the sender wrote`. These are not the same guarantee — the `shop` field is a "field acted on but not covered by the HMAC," exactly the analog bug class described in the report (an unprotected trust boundary between what's verified and what's acted upon).

## Impact Explanation
Because `HmacValidator.validate` only binds the signature to the raw body, an unprivileged internet user who can obtain one legitimately-signed webhook body/HMAC pair (e.g., from an app instance they legitimately installed on their own shop, or any webhook whose body content is attacker-influenced/predictable) can replay that exact `(raw_body, hmac)` pair while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` because it never inspects the `shop` field, and `Registry.process` will hand the forged shop domain straight to the host application's `WebhookHandler#handle` as trusted `WebhookMetadata#shop`. Any host application that uses this "verified" shop value as a key to fetch sessions, persist data, or authorize actions can be tricked into applying data/events under the wrong tenant identity — a cross-tenant integrity issue rooted entirely in this gem's webhook verification contract, not an application misuse of a documented API.

## Likelihood Explanation
Exploitation requires no credentials, tokens, or `api_secret_key`: the attacker only needs one instance where they can obtain a body+HMAC pair (trivial if they run their own store with the app installed, since Shopify signs webhooks it sends to that store using the shared app secret) and the ability to send an arbitrary HTTP request to the app's own public webhook endpoint with a modified header — something entirely under attacker control since HTTP headers are not part of the TLS-protected payload validation performed by this gem. This is a low-effort, unprivileged-internet-user attack path directly through code in `lib/shopify_api/webhooks/`.

## Recommendation
Bind the shop identity into the verified material. Either:
1. Include the `shop-domain` (and ideally `topic`/`webhook-id`) header value inside `to_signable_string` (matching Shopify's actual webhook HMAC computation contract), so the HMAC cryptographically covers the shop claim, or
2. After HMAC validation, cross-check the `request.shop` value against an independently-trusted source (e.g., the shop associated with the session/store lookup used to register that specific webhook subscription) before passing it downstream, rejecting mismatches.
At minimum, the library should document explicitly that `request.shop` is unauthenticated and must not be trusted for tenant-identification without an additional binding, so host apps aren't silently exposed to this gap.

## Proof of Concept
```ruby
# Attacker has one shop ("attacker.myshopify.com") with the app installed and can trigger
# a webhook delivery with body content they influence (or any predictable body),
# capturing the resulting HMAC that Shopify computed over that body.

hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, "{}")
# (In reality, the attacker doesn't need the secret key — they simply capture Shopify's
#  own signed webhook request sent to their store for body "{}".)

forged_headers = {
  "x-shopify-topic"          => "orders/create",
  "x-shopify-hmac-sha256"    => Base64.encode64(hmac),   # valid signature for body "{}"
  "x-shopify-shop-domain"    => "victim-shop.myshopify.com", # <-- spoofed, not covered by HMAC
  "x-shopify-webhook-id"     => "any-id",
  "x-shopify-api-version"    => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)

# Passes verification because HMAC only covers @raw_body, never the shop header:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))
# The host app's handler now believes this event legitimately originated from victim-shop.
``` [7](#0-6) [8](#0-7) [1](#0-0)

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
