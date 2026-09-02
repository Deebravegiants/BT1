## Title
Webhook shop identity spoofing — the `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted from unauthenticated HTTP headers while only the raw body is covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value (along with `topic`, `webhook_id`, `api_version`) directly from unauthenticated HTTP headers, but `Utils::HmacValidator.validate` only verifies the raw request body against the app's shared secret. Because the secret is identical for every shop that installs the app, any unprivileged internet user who can obtain one valid `(body, hmac)` pair (e.g., by installing the app on their own free/dev store and observing a legitimate webhook delivery) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header, and the request will still pass HMAC validation.

## Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which are part of the signed content: [2](#0-1) 

`HmacValidator.validate` only checks the HMAC computed from `to_signable_string` (i.e., the body) against the secret: [3](#0-2) 

`Registry.process` gates entirely on that body-only HMAC check, then forwards the header-derived, unauthenticated `shop` value straight to the app's handler as the trusted tenant identity: [4](#0-3) 

This breaks the intended identity binding: **shop value authenticated by the HMAC == shop value the app acts on**. In this gem, the "authenticated" side of that equality is empty — only the body bytes are bound to the secret, while the shop value delivered to the handler is fully attacker-controlled whenever the request reaches the endpoint from outside Shopify's infrastructure (i.e., the raw public HTTP endpoint the host app exposes for this gem to process). Since the API secret key is shared across every shop that installs the app, an attacker who is a legitimate (even free-tier) merchant of the same app has direct access to one valid `(body, hmac)` pair from their own installation, and can then swap the `x-shopify-shop-domain` header to any victim shop domain without invalidating the signature.

## Impact Explanation
This allows cross-tenant data injection: an attacker can cause the app to process attacker-chosen webhook bodies (topic, payload) attributed to a shop domain of their choosing, since the `shop` value is passed to the handler unauthenticated. Depending on how the host app keys behavior off `data.shop` (session/tenant lookup, order/customer record writes, billing triggers, etc.), this is a cross-tenant confusion/injection vector satisfying the "cross-tenant access" Critical-impact category, driven entirely by this gem's failure to bind the shop identity into its HMAC verification.

## Likelihood Explanation
Requires only: (1) the attacker to obtain one valid signed webhook body from any single installation of the target app (trivially available to any developer/merchant who installs a public app), and (2) network access to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is needed — the API secret key is never exposed to or required by the attacker.

## Recommendation
Include the `shop` domain (and ideally `topic`/`webhook_id`) in the signed content verified by `HmacValidator`, or otherwise independently authenticate the shop claim (e.g., cross-check it against a shop already known to the app via a stored offline session) before trusting `request.shop` in `Registry.process`.

## Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and captures one legitimate webhook delivery: raw body `B` and its valid `x-shopify-hmac-sha256` header `H` (valid because it's HMAC(secret, B), and `secret` is the same for all shops using this app).
2. Attacker sends a forged HTTP POST to the app's webhook endpoint with:
   - `x-shopify-hmac-sha256: H` (unchanged)
   - body: `B` (unchanged)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
   - `x-shopify-topic`, `x-shopify-webhook-id` optionally changed too (also unauthenticated)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` which only recomputes the HMAC over `B` — it succeeds because `B` and `H` are unchanged.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, i.e., data attributable to `victim-shop` even though `victim-shop` never sent this webhook. [4](#0-3) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
