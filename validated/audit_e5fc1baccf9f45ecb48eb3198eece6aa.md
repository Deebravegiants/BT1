### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw request body only, while the `shop` (and `topic`/`webhook_id`/`api_version`) values are read directly, unauthenticated, from HTTP headers. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then hands the header-derived `shop` value straight to the app's webhook handler, so the identity that is cryptographically verified (the body) and the identity that is acted upon (the `shop-domain` header) are not the same bytes.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `Request#shop` is read from an attacker-controllable HTTP header with no cryptographic tie to the signed content: [2](#0-1) 

`HmacValidator.validate` only checks the `VerifiableQuery#to_signable_string` (the body) against the HMAC secret: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`) to construct the metadata passed to the app-defined handler: [4](#0-3) 

Because the webhook signing secret is the app's single `client_secret`, shared across every shop that installs the app, any merchant/shop that has installed the app can generate a legitimately-signed webhook body+HMAC pair for their own shop (e.g., by triggering a topic they can control, such as updating one of their own resources). That merchant can then replay the exact same `raw_body`/`x-shopify-hmac-sha256` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still pass, because the signature only ever covered the body — never the shop header — so the check equality that should hold is:

`shop authenticated by HMAC == shop acted upon by the handler`

but the code actually verifies `HMAC(body) == HMAC(body)` while using an entirely separate, unauthenticated `shop` value for downstream authorization/business logic.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to provide to host applications: a webhook handler that keys any state, authorization, or side effects off `data.shop` (as the gem's own documentation instructs handlers to do) can be made to process attacker-supplied body content under the identity of a different, victim shop. This is a cross-tenant access vector — an attacker (a shop that has installed the app) can inject spoofed webhook events attributed to a shop they do not own, as long as they can produce any validly-signed body from their own tenant and replay it with a forged `shop-domain` header.

### Likelihood Explanation
Likelihood is elevated because: (1) the attacker only needs to be any unprivileged merchant who has installed the app — no leaked secrets or privileged access are required, since they can legitimately obtain a signed body+HMAC pair for their own shop; (2) webhook endpoints are public-facing HTTP endpoints by design; (3) the `client_secret` used to sign webhooks is shared across all installs of the app, so the attacker's own legitimately-signed webhook is valid input material for the replay against any other shop.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`/`api_version`) to the HMAC-verified content instead of trusting header values independently of the signed body. Since Shopify's webhook payloads already embed the shop's `myshopify_domain` in most resource payloads, `Request` should cross-check the parsed body's shop identity against the header-derived `shop`, or the HMAC computation should include the header value(s) that downstream code relies on for identity decisions, rejecting the request if they diverge.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (both legitimate installs of the same app, sharing the same `client_secret`).
2. Attacker triggers any webhook topic they control on their own shop (e.g., updates a product), causing Shopify to POST to the app's webhook endpoint with:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`
   - Body: `raw_body` (attacker-controlled content, e.g., a product payload)
3. Attacker intercepts/replays this exact `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint again, but replaces the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(raw_body)` — this still succeeds because the body and HMAC are unchanged.
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` is built with `shop == "victim-shop.myshopify.com"` and the attacker-controlled body, and passed to the app's handler, which believes the event originated from `victim-shop.myshopify.com`. [4](#0-3) [5](#0-4)

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
