### Title
Webhook Shop-Domain Spoofing — HMAC Covers Only the Raw Body, Not the `shop` Header Used for Tenant Attribution - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then unconditionally trusts the `shopify-shop-domain` header (never covered by that HMAC) to attribute the event to a tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string with the app's shared `api_secret_key`: [2](#0-1) 

`Registry.process` treats a passing HMAC check as sufficient authentication, then builds the `WebhookMetadata` handed to the app's handler using `request.shop`, which is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header — a value that was never part of the signed bytes: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `shop attributed to webhook == shop bound by the verified signature`. Instead the equality only proves `raw_body == raw_body signed with api_secret_key`; the `shop` field is parsed from an unauthenticated header and is never checked against anything cryptographically tied to the signature.

Critically, `api_secret_key` is a single, app-wide secret shared across *every* shop that installs the app (it is not a per-shop key) — see its use in HMAC and JWT validation elsewhere in the gem, e.g. `Context.api_secret_key` used identically for all tenants in `JwtPayload` and `HmacValidator`. Consequently, any unprivileged internet user who installs the public app on their own store receives genuinely-signed webhooks (valid HMAC over their own body) from Shopify. Because the header carrying the tenant identity (`shop`) is outside the signed bytes, that same attacker can replay the identical signed body to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Registry.process` will accept the HMAC (it only checks body bytes) and dispatch the handler with `shop: <victim-shop>`, causing the consuming application to process attacker-controlled body data as if it originated from the victim tenant.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an attacker with no privilege on the victim's shop can inject webhook events attributed to that shop. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up install-specific session/state, trigger fulfillment, orders, or GDPR-relevant flows), this enables cross-tenant data confusion/injection — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
The only requirement is a legitimate (attacker-controlled) app installation on any shop, which is trivial to obtain for a public app, plus the ability to POST a replayed HTTP request to the app's public webhook callback URL. No secrets, tokens, or privileged access are needed beyond what an ordinary merchant installing the app already has.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook-id`) values in the signable payload alongside the raw body (e.g., prefix/append the header values to the HMAC input, or verify the header values against values embedded in the signed body/JWT), so the identity used for tenant attribution is cryptographically bound to the same bytes verified by `HmacValidator.validate`. At minimum, document that consuming applications must independently corroborate `WebhookMetadata#shop` against a previously known installation before trusting it, and consider failing closed if no cross-check is possible.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` and triggers a webhook event (e.g., `orders/create`) they control.
2. Shopify sends the app: body `B`, headers including `x-shopify-hmac-sha256: HMAC(api_secret_key, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker intercepts/replays this exact request to the app's public webhook endpoint but changes only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` — unchanged since `to_signable_string` returns only `B` — and the check passes.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, and the host app processes attacker data as belonging to the victim tenant. [3](#0-2) [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
