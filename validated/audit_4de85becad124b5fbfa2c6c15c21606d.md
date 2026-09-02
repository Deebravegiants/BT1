This confirms the finding: the docs explicitly state `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" via HMAC, and the `WebhookHandler` receives `data.shop` as a trusted identity for tenant-scoped processing (`perform_later(shop_domain: data.shop, ...)`), yet the `shop` field is sourced purely from an HTTP header never covered by the HMAC.

### Title
Webhook `shop`, `topic`, `webhook_id` and `api_version` headers are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC signature over the raw request body via `Utils::HmacValidator.validate(request)`, where `Request#to_signable_string` returns only `@raw_body`. The `shop` (and `topic`, `webhook_id`, `api_version`) values, which are read straight from HTTP headers (`shopify-shop-domain` / `x-shopify-shop-domain`), are never included in the signed content, yet they are trusted and forwarded verbatim into `WebhookMetadata` and passed to the app's `handler.handle`, which the docs (`docs/usage/webhooks.md`) explicitly instruct developers to use for tenant-scoped actions (e.g. `shop_domain: data.shop`).

### Finding Description
`Registry.process` is the sole authentication gate for inbound webhooks: [1](#0-0) 

It calls `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`: [2](#0-1) 

`Request#to_signable_string` is defined to return only the raw request body: [3](#0-2) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers with no cryptographic binding to the signed content: [4](#0-3) 

After the HMAC check passes, `Registry.process` builds `WebhookMetadata` directly from these unverified header values and dispatches it to the app-supplied handler: [1](#0-0) 

This breaks the identity binding the library implicitly promises: **authenticated tenant (HMAC-covered content) ≠ shop the handler is told the data belongs to (`request.shop`, from an unauthenticated header)**. The gem's own documentation instructs developers to trust `data.shop` for tenant-keyed side effects (`perform_later(shop_domain: data.shop, webhook: data.body)`), confirming that `shop` is treated as an authenticated identity by design, when in fact it carries no cryptographic guarantee.

An attacker who is a legitimate merchant using the same app (an "unprivileged" tenant with no elevated access) receives real, validly-signed webhooks from Shopify addressed to their own store. Because the HMAC only signs the body, the attacker can replay that exact signed body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header with an arbitrary victim shop domain. `Utils::HmacValidator.validate` still succeeds (the body/HMAC pair is untouched and valid), so `Registry.process` proceeds and calls the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own store.

### Impact Explanation
This is a cross-tenant data integrity/access issue (impact: Critical - cross-tenant access) as defined by the rules. Any host application that follows this gem's own documented pattern of keying tenant-scoped writes or business logic off `WebhookMetadata#shop` (as literally shown in `docs/usage/webhooks.md`) can have attacker-supplied data injected into or attributed to a different merchant's tenant record set, purely by an existing, unprivileged app user replaying their own legitimately-signed webhook with a forged shop header. No access token, `client_secret`, or `api_secret_key` leakage is required — only a body/HMAC pair the attacker already legitimately possesses from their own installation.

### Likelihood Explanation
Likelihood is high for any app built directly against this gem's documented API: capturing one's own valid webhook (body + `X-Shopify-Hmac-Sha256` header) requires no special access, and forging the shop-domain header on a replayed HTTP request is trivial. The vulnerability is deterministic — it does not depend on timing, races, or any weakness in the crypto itself, only on the fact that the signed payload excludes tenant-identifying headers entirely.

### Recommendation
Either:
1. Bind the `shop`, `topic`, `webhook_id`, and `api_version` values into the HMAC-signed content (e.g., include the relevant headers in the signable string, as some webhook schemes do), or
2. Require callers of `Registry.process`/handler implementations to independently verify that `request.shop` corresponds to a shop with an active, known installation/session before trusting it for any tenant-scoped action, and clearly document in `docs/usage/webhooks.md` that `data.shop` is **not** cryptographically authenticated and must be cross-checked against stored session/shop records before use.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook (e.g. `orders/create`) from Shopify with a valid `X-Shopify-Hmac-Sha256` header computed over the raw body using the app's `client_secret` — this is a normal message the attacker is entitled to see since it targets their own store.
2. Attacker resends that exact HTTP request (same raw body, same `X-Shopify-Hmac-Sha256` value) to the app's webhook endpoint, but replaces the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC (`request.rb:35-38`, `hmac_validator.rb:26-31`) — headers, including `shop`, are irrelevant to this check.
4. `Registry.process` invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the app (following the gem's own documented pattern) to persist or act on the attacker's payload as if it belonged to `victim-shop`. [1](#0-0) [5](#0-4) [6](#0-5)

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
