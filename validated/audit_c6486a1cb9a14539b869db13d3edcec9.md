## Finding

The Gearbox bug class (an identity field acted upon that isn't covered by the authenticating signature — "liquidations operate on the borrower's address... not the CreditAccount") maps directly onto how this gem authenticates inbound Shopify webhooks.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` — the bytes that are actually HMAC-verified — is defined as **only the raw request body**: [1](#0-0) 

But the `shop`, `topic`, `api_version`, and `webhook_id` used to route and attribute the webhook are all pulled straight from unauthenticated HTTP headers: [2](#0-1) 

`HmacValidator.validate` only checks that the HMAC matches `to_signable_string` (the body), never binding `shop`/`topic` into what's verified: [3](#0-2) 

`Registry.process` validates the HMAC, then trusts `request.shop` and `request.topic` (header-derived, unauthenticated) to build the dispatched metadata and select which handler runs: [4](#0-3) 

The identity binding that should hold is: **`shop`/`topic` verified == `shop`/`topic` acted upon**. Instead, only the body is verified while `shop`/`topic` are parsed independently from headers — exactly the "bytes verified versus bytes parsed" / "field acted on but not covered by the HMAC" pattern called out in scope.

### Exploit path

Since a public app's `client_secret` (and thus the HMAC key) is shared across every shop that installs the app, an attacker who installs the app on their own shop can:
1. Trigger any real webhook event on their own store (e.g. `orders/create`) to obtain a body + a genuinely valid `X-Shopify-Hmac-Sha256` signature.
2. Replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint, but with the `X-Shopify-Shop-Domain` header changed to a victim shop, and/or `X-Shopify-Topic` changed to any registered topic (e.g. `customers/data_request`, `shop/redact`, `app/uninstalled`).
3. `HmacValidator.validate` still passes (it only checks the untouched body), so `Registry.process` dispatches the attacker-chosen topic/shop combination to the handler as if it legitimately came from the victim shop.

This lets an unprivileged app-installer forge webhook events attributed to any other tenant of the same app — a cross-tenant confused-deputy condition (e.g. triggering data-redaction, uninstall cleanup, or business logic keyed by `shop` for a shop the attacker doesn't control).

### Recommendation
Bind `shop` and `topic` into the value that is HMAC-verified (or otherwise cryptographically authenticate them), rather than trusting header values independent of the HMAC-covered payload. At minimum, hosts using this gem should be warned that `request.shop`/`request.topic` are not covered by `HmacValidator.validate` and must not be trusted for tenant attribution without additional checks (e.g. cross-referencing against the shop's stored webhook registration). [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
