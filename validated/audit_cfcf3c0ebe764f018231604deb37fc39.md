### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop/tenant spoofing on replayed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and exposes an HMAC-verifiable digest, but the digest is computed only over the raw request body. The `shop`, `topic`, `api_version`, and `webhook_id` values are all read directly from unauthenticated HTTP headers and are never included in the signable content, so the binding "HMAC covers what the app trusts as originating from a specific shop" does not hold.

### Finding Description
`Request#hmac` returns the decoded `shopify-hmac-sha256` / `x-shopify-hmac-sha256` header value, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are pulled straight from the corresponding `shopify-*`/`x-shopify-*` headers with no cryptographic binding to the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that `compute_signature(verifiable_query.to_signable_string, secret)` matches the received HMAC — i.e., it verifies the *body* was signed with the app's secret, but says nothing about which shop, topic, or webhook id the caller-supplied headers claim: [3](#0-2) 

This is exactly the identity-binding gap called out in the report: *"a field acted on but not covered by the HMAC."* Here the equality that should hold is `shop_used_for_tenant_routing == shop_that_produced_this_signed_payload`, but nothing in this gem enforces that equality — `shop` is metadata supplied by the untrusted request, not part of `to_signable_string`.

### Impact Explanation
A caller who can obtain one valid `(raw_body, hmac)` pair for their own shop (e.g., a merchant who installed the app and can capture their own legitimate webhook delivery) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. Since `HmacValidator.validate` passes (the body/HMAC pair is genuinely valid), any host application that relies on this gem's `Request#shop` to determine which merchant/tenant a webhook event belongs to would process the event under the attacker-chosen shop domain instead of the shop that actually produced it. This is a cross-tenant identity confusion at the webhook-verification layer provided by this gem.

### Likelihood Explanation
Exploitation requires possession of at least one genuinely signed webhook body (obtainable by any merchant who installs the app on their own store, which is an ordinary, unprivileged action), plus the ability to POST directly to the app's webhook endpoint with modified headers — both are realistic for an external actor and require no access to `api_secret_key`, access tokens, or the app's infrastructure.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed content that is verified, or otherwise cryptographically bind the header-derived `shop` value to the verified body before it is used for any tenant-routing decision, e.g. by requiring host applications to independently confirm the webhook's shop against the accompanying signed body's own shop-identifying content rather than trusting the header alone.

### Proof of Concept
1. Merchant A installs the app; the app registers a webhook and Shopify sends a legitimately signed webhook (`raw_body`, `X-Shopify-Hmac-Sha256`, `X-Shopify-Shop-Domain: shop-a.myshopify.com`) to the app's endpoint.
2. Attacker captures this delivery (e.g., is Merchant A themselves, or intercepts it via their own logging/proxy on infrastructure they control).
3. Attacker replays the identical `raw_body` and `hmac` header to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` is constructed; `Utils::HmacValidator.validate` (via whatever registry/handler calls it) succeeds because it only checks `raw_body` against the HMAC.
5. `request.shop` now returns `shop-b.myshopify.com`, and any host-app logic keyed off `request.shop` (e.g., looking up sessions, tenant-scoped processing) is fooled into treating Shop A's event data as belonging to Shop B. [4](#0-3)

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
