I found a valid analog. The Team Finance exploit's root cause was **"lack of check that a parameter is legitimate"** — a value trusted for one purpose is not actually verified against the source of truth. In this gem, the equivalent binding failure is in webhook verification: `ShopifyAPI::Webhooks::Request`'s HMAC signature only covers the raw body, while the `shop-domain` header — which becomes the tenant identity handed to the app's webhook handler — is never covered by that signature.### Title
Webhook shop-domain header is trusted for tenant identity but is excluded from the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signature over the raw HTTP body only, while the `shop-domain` header — which the registry treats as the authenticated tenant identity — is passed through unverified. Because the same `api_secret_key` is shared across every shop that installs an app, an attacker who controls one legitimate installation of the app (e.g. their own store) can capture one of their own validly-signed webhook deliveries and replay it against the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, producing a webhook that the app will process as if it came from the victim tenant.

### Finding Description
`Utils::VerifiableQuery` requires only `hmac` and `to_signable_string`. For webhooks, `to_signable_string` returns just `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors read directly from unauthenticated HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which — per `HmacValidator#validate_signature` — recomputes the HMAC over `to_signable_string` (the raw body) and compares it to the received `hmac-sha256` header: [3](#0-2) 

Once that check passes, `Registry.process` hands `request.shop` straight to the handler as the tenant identity, with no separate verification that this header matches the shop the HMAC was actually issued for: [4](#0-3) 

**Binding that is broken:** the intended equality is
`shop-domain header == shop that produced (raw_body, hmac)`,
but the code only checks `hmac == HMAC(raw_body, api_secret_key)`. The `shop-domain` header is a field acted on (used as the tenant key delivered to the handler) but not covered by the HMAC — this is exactly the bug class described in the prompt ("a field acted on but not covered by the HMAC").

Because `api_secret_key` is a single value shared by the app across all of its merchant installations, any shop that has installed the app — including one controlled by the attacker — can generate a `(raw_body, valid-hmac)` pair. That pair remains valid regardless of which `shop-domain` header accompanies it, since the header is not part of the signed material.

### Impact Explanation
This crosses a tenant boundary without any credential belonging to the victim: an attacker who has installed the app on their own store (a normal, unprivileged action) can forge webhook events (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`, or any custom topic) that the app will attribute to an arbitrary victim shop domain. Any app logic keyed off `WebhookMetadata#shop` — creating/updating shop-scoped records, triggering data exports, revoking sessions, marking a shop as uninstalled, or fulfilling GDPR-related mandatory topics — can be triggered against a shop the attacker does not own. This matches the "cross-tenant access" Critical-impact category in scope for this analysis, since it lets an unprivileged user inject data attributed to another tenant purely by controlling the header of a replayed, self-obtained valid webhook body/HMAC pair.

### Likelihood Explanation
Likelihood is high for any app that (a) accepts more than one merchant installation (nearly all public apps) and (b) uses the `topic`/`shop` from `WebhookMetadata` to perform any shop-scoped side effect without independently re-validating the shop against a known/expected value (e.g., an active session or install record) before acting. The prerequisite — installing the app once as the attacker to obtain one valid `(body, hmac)` pair — requires no special privilege and no leaked secret; it only requires ordinary app usage. The header can be freely rewritten by any HTTP client since the gem performs no comparison between the signed body's origin and the header value.

### Recommendation
Bind the tenant identity into the material that is authenticated, or otherwise verify it independently:
- Extend the webhook's `to_signable_string` (or a separate check in `Registry.process`) to require that the shop the app expects (e.g., from a previously stored install/session record, or from Shopify's `X-Shopify-Shop-Id` in conjunction with a lookup) matches `request.shop`, rather than trusting the header outright.
- At minimum, document/require that consuming applications validate `WebhookMetadata#shop` against their own record of installed shops before performing shop-scoped side effects, since the gem's HMAC check alone does not authenticate the shop field.
- Consider incorporating the shop domain into the signed payload check if Shopify's webhook contract can support it, or reject processing when the shop header does not match a shop with an active session/install known to the host app.

### Proof of Concept
1. Attacker installs the target app onto their own store `attacker-shop.myshopify.com` (a normal unprivileged action supported by any public app) and lets the app register a webhook, e.g. for `customers/data_request`.
2. Shopify (or the attacker's own test harness, since Shopify signs webhooks with the app's single shared `api_secret_key`) delivers a webhook to the app's endpoint with:
   - body: `{"customer": {...}}`
   - header `X-Shopify-Hmac-Sha256`: valid HMAC-SHA256 of that body using the app's `api_secret_key`
   - header `X-Shopify-Shop-Domain`: `attacker-shop.myshopify.com`
3. Attacker captures this exact `(raw_body, hmac)` pair.
4. Attacker sends a new HTTP POST directly to the app's webhook route with the same `raw_body` and `X-Shopify-Hmac-Sha256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only — this still matches, because the shop header was never part of the signed data.
6. The registered handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` and performs whatever shop-scoped action the app implements for that topic, attributing it to the victim shop despite the attacker never having any credential for that shop. [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L1-31)
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
