## Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` (tenant identity) and `topic` (action identity) fields used by `Registry.process` to dispatch and act on the webhook are taken directly from unauthenticated HTTP headers. This breaks the intended binding `HMAC == f(shop, topic, body)`; in reality `HMAC == f(body)` only. An attacker who can obtain any one legitimately-signed webhook body/HMAC pair (trivially possible by installing the target app on their own free Partner development store) can replay that exact body with a forged `shop-domain`/`topic` header to the app's public webhook endpoint, and the signature will still validate.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` and `topic` accessors are read straight from attacker-controlled headers, with no cryptographic tie to the signed body: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.topic` and `request.shop` to route and execute the handler, passing them into `WebhookMetadata`: [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e., the body) against the secret, and returns a boolean with no knowledge of headers: [4](#0-3) 

This is structurally the same bug class as the referenced report: an operation (`_deposit`/`_withdraw` there; `handler.handle` here) acts on a value (`amount0Min/amount1Min` there; `shop`/`topic` here) that was not included in the value verified for authenticity/integrity before the action was taken. Here, `Context.api_secret_key` is a shared secret for the whole app (not per-shop), so any merchant who installs the app — including the attacker on their own store — receives real webhooks stamped with a valid HMAC of the body. That body+HMAC pair remains valid forever for *any* `shop`/`topic` header combination, because those fields are never part of the signed data.

### Impact Explanation
This crosses a tenant boundary: an attacker-controlled shop can produce a validly-signed webhook payload and relabel it as belonging to a victim shop (`shop-domain` header) and/or as a different topic (e.g., relabeling an innocuous webhook as `app/uninstalled` or `shop/redact` to trigger data-deletion/cleanup logic, or as `orders/create` to inject attacker-chosen order data attributed to the victim shop). Depending on how the host application's webhook handlers use `WebhookMetadata#shop` and `#topic` (e.g., to look up/update per-shop records, trigger GDPR deletion, or grant/act on behalf of a shop), this enables cross-tenant data corruption or unauthorized actions attributed to a victim merchant — satisfying the "cross-tenant access" Critical impact bar.

### Likelihood Explanation
High: the only prerequisite is the ability to install the target Shopify app on any store (including a free attacker-controlled development store) to receive at least one genuinely-signed webhook, then replay that exact body to the app's public webhook URL with modified `shop-domain`/`topic` headers. No secrets, tokens, or privileged access are required — this is fully reachable by an unprivileged internet user with only a public app installation.

### Recommendation
Include the `shop` and `topic` values (and any other identity-bearing header) inside the signed material, or otherwise cryptographically bind them to the payload before dispatching to handlers — e.g., verify HMAC over a canonical string composed of `shop-domain + topic + raw_body`, matching what Shopify's own webhook signing is capable of covering, and reject the request if headers were altered relative to what was originally signed for that body.

### Proof of Concept
1. Attacker installs the target app on their own (free) development store `attacker.myshopify.com`; the app registers a webhook, e.g. for `orders/create`.
2. Shopify sends a legitimately HMAC-signed webhook to the app: body `B`, headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: H` where `H = HMAC(secret, B)` per `HmacValidator.validate_signature`.
3. Attacker captures `(B, H)` and replays a POST to the same app's public webhook endpoint, keeping body `B` and `H` unchanged but setting `x-shopify-shop-domain: victim.myshopify.com` (and/or `x-shopify-topic: shop/redact`).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `B` — succeeds — then invokes `handler.handle(data: WebhookMetadata.new(topic: "shop/redact", shop: "victim.myshopify.com", body: ...))`, causing the host app's handler to act on the victim shop using attacker-supplied identity fields that were never authenticated. [5](#0-4)

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
