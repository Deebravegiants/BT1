## Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that host applications use to route/process a webhook from an HTTP header, while the HMAC signature that this gem verifies covers only the raw request body. Because a single app's `api_secret_key` is shared across every shop that has installed the app, an attacker who controls one legitimately-installed (e.g., free/dev) shop can generate a genuinely valid HMAC for a webhook body, then replay that request while swapping the `X-Shopify-Shop-Domain` header to a victim shop, producing a payload that this gem reports as HMAC-valid for the wrong tenant.

## Finding Description
`Request#hmac` decodes the `X-Shopify-Hmac-Sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

The tenant identity used by the rest of the flow, `Request#shop`, is instead read directly and independently from the `X-Shopify-Shop-Domain` header, completely outside the signed material: [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the raw body only) and compares it against the received signature: [4](#0-3) 

This creates the identity-binding break called out in scope: **a field (`shop`) acted on but not covered by the HMAC**. The equality the gem implicitly (and incorrectly) relies on is:
`hmac_valid(raw_body) == true  ⇒  shop_header == originating_shop`

That equality does not hold. `hmac_valid(raw_body)` only proves the body was signed with the app's shared `api_secret_key` — it says nothing about which shop the header claims to be from, because the header is never part of the signed bytes. Since `api_secret_key` is identical for every shop that installs the app, any shop (including one an attacker legitimately installs the app on) can produce a body/HMAC pair that will validate successfully; the attacker can then present that same valid body+HMAC combination together with an arbitrary `X-Shopify-Shop-Domain` value.

## Impact Explanation
If a host application (following this gem's documented pattern of validating HMAC and then using `Request#shop` to look up/act on the corresponding merchant session or data), it can be made to process a webhook it believes originates from shop B while the attacker actually controls shop A. Because webhook payloads and their downstream side effects (e.g., updating stored session/order/customer state keyed by `shop`) are trusted once HMAC passes, this enables cross-tenant data confusion/injection — writing or triggering actions against a victim tenant's records using attacker-supplied body content. This matches the in-scope "cross-tenant access" impact category.

## Likelihood Explanation
Likelihood is realistic but bounded: it requires the attacker to have (or create) at least one legitimate installation of the target app on any shop, which is normal for many public apps (free installs, dev stores, trial shops are commonly available to any internet user). No access token, `api_secret_key`, or privileged account is required — only the ability to receive a genuine webhook (or replay one) from their own shop and modify the plaintext `shop-domain` header before it reaches the app's webhook endpoint, since that header is not authenticated by this gem.

## Recommendation
Bind the tenant identity into the verified material instead of trusting an unauthenticated header:
- Include `shop-domain` (and ideally `topic`, `webhook-id`) in the HMAC-signable string, or
- After HMAC verification, independently corroborate `Request#shop` against session/store data already associated with the specific `webhook-id`/subscription that was registered for that shop, rather than trusting the header value at face value for routing.

## Proof of Concept
1. Attacker's app is installed on `attacker-shop.myshopify.com` (any low-friction install: free plan, dev store).
2. Attacker triggers a genuine webhook delivery (e.g., updates a product) — Shopify sends a request with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's shared `api_secret_key`, and header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker intercepts/replays this exact request to the app's webhook endpoint but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, leaving `raw_body` and the HMAC header untouched.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over the (unmodified) raw body and it matches — validation passes.
5. `Request#shop` returns `victim-shop.myshopify.com` from the (unauthenticated, attacker-modified) header, so the host app processes attacker-controlled webhook content as if it came from the victim tenant. [5](#0-4)

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
