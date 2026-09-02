### Title
Webhook shop-domain identity is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the raw request body via HMAC, but the `shopify-shop-domain` header — which the gem hands to the app's webhook handler as the authoritative tenant identifier — is never included in the signed payload. An attacker who legitimately controls one shop (any free/dev store) can capture a validly-signed webhook delivered to them, then replay the identical body+HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop, and the gem will accept it as authentic for the victim tenant.

### Finding Description
`Webhooks::Registry.process` verifies authenticity solely with:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
``` [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC over `verifiable_query.to_signable_string`, and `Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) [3](#0-2) 

The `shop` value that gets forwarded to the app's handler is read directly from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header, independent of the signed content: [4](#0-3) [5](#0-4) 

The dispatched metadata trusts this header value as the tenant identity for the event: [6](#0-5) 

**Broken binding**: `HMAC-authenticated(body)` is treated as equivalent to `HMAC-authenticated(shop, body)`, but the equality `shop_in_signed_payload == shop_delivered_to_handler` never holds — `shop` is completely outside the MAC's scope. Any request whose body+HMAC pair was legitimately produced for shop A can be replayed with shop B's identity attached, and the gem will not detect the substitution.

### Impact Explanation
Because the shop identifier used by the app to route/attribute webhook side effects (e.g., `customers/redact`, `shop/redact`, `app/uninstalled`, order/product update handlers) is forgeable independently of the cryptographic check, an attacker can cause the app to process webhook events attributed to an arbitrary victim shop. Depending on what the host app's `WebhookHandler#handle` implementation does with `data.shop` (which is the gem's own documented contract for identifying the tenant), this enables cross-tenant state manipulation — e.g. spoofing an uninstall event, a redaction/GDPR event, or any topic the app has registered, against a shop the attacker does not control. This satisfies the "cross-tenant access" criterion for a Critical-severity finding.

### Likelihood Explanation
Likelihood is realistic for an unprivileged attacker: they only need to be a legitimate merchant on their own shop (trivial, free) to receive a genuinely HMAC-signed webhook body from Shopify, and then send an ordinary HTTP POST directly to the app's public webhook endpoint with a spoofed `shopify-shop-domain`/`x-shopify-shop-domain` header. No access to the app's `client_secret`, access tokens, or any privileged account is required — this exactly matches the "field acted on but not covered by the HMAC" analog class.

### Recommendation
- Bind the shop domain (and topic/webhook-id) into the value that is actually verified — either include these headers in the signable string used for HMAC computation, or require the caller to validate that the `shopify-shop-domain` header matches a shop with an active session/installation known to the host app before dispatching to the handler.
- Document/require that host apps cross-check `data.shop` against their own stored installation registry before trusting it, since the interface itself does not defend against header substitution.

### Proof of Concept
1. Attacker registers/installs the target app on their own store `attacker.myshopify.com` and triggers a webhook topic the app handles (e.g. `orders/create`), receiving a POST to their `path` with a body `B` and a valid header `X-Shopify-Hmac-SHA256: H` (computed by Shopify over `B` using the app's real secret).
2. Attacker captures `B` and `H` (they own this shop, so this is not a secret they need to steal — Shopify sends it to them as the destination of their own webhook).
3. Attacker crafts a new HTTP POST directly to the app's public webhook endpoint with:
   - body `B` (unchanged)
   - header `x-shopify-hmac-sha256: H` (unchanged, still valid because the body did not change)
   - header `x-shopify-shop-domain: victim-shop.myshopify.com` (replaced)
   - header `x-shopify-topic`, `x-shopify-webhook-id` set as desired
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers; `Utils::HmacValidator.validate` passes because only `B` is checked; `Registry.process` invokes the registered handler with `WebhookMetadata` whose `shop` is `"victim-shop.myshopify.com"`, despite the HMAC having no relation to that shop. [6](#0-5) [7](#0-6)

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
