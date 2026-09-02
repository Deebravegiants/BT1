### Title
Webhook `shop` (tenant identity) header is not covered by the HMAC signature, breaking the shop↔payload binding - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `Utils::HmacValidator.validate` in `Registry.process` authenticates the body bytes only. The `shop` attribute that `Registry.process` hands to the app's `WebhookHandler` as the tenant identifier for that webhook (`WebhookMetadata#shop`) comes from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is completely outside the signed data. This is the same bug class as the Lybra finding: a value that is *acted on* (used as the authoritative tenant key) is not the value that is *covered by* the authentication check, so the two can be desynchronized.

### Finding Description
`Request#hmac` and `Request#to_signable_string` establish the HMAC binding: [1](#0-0) 

`Registry.process` validates that HMAC and then immediately trusts `request.shop` (an unauthenticated header) as the source-of-truth tenant for the webhook, passing it straight into `WebhookMetadata`, which the host app's `handler.handle` uses to route/attribute the payload: [2](#0-1) [3](#0-2) 

The identity binding that should hold is:
`hmac_valid(request) == true` should imply `(shop, body)` were jointly signed by Shopify with this app's `client_secret`.

In reality the equality that holds is only:
`hmac_valid(request) == true` implies `body` was signed — `shop` is never part of `to_signable_string`, so `hmac_valid(shop_A, body) == hmac_valid(shop_B, body)` for any two shop headers, because the header value plays no role in `compute_signature`: [4](#0-3) 

`Request#shop` simply reads the header verbatim with no cross-check against the signed body: [5](#0-4) 

Because the gem's `Registry.process` is the piece that decides the webhook is "authenticated" and then constructs `WebhookMetadata` (the object contract handed to every app's `WebhookHandler`), this is a defect in the gem's own authentication surface, not merely the host app "ignoring documented API" — the documented contract of `process` is that after HMAC validation the `WebhookMetadata#shop` can be trusted as the originating shop, but the implementation never binds that field to the signature.

### Impact Explanation
An attacker who can observe or induce delivery of one legitimate webhook body for Shop A (webhook bodies for mandatory/compliance topics such as `customers/data_request`, `customers/redact`, `shop/redact` are often low-sensitivity in content but carry a shop-scoped meaning) can replay the exact same `raw_body` + valid `hmac-sha256` value while substituting Shop B's domain in the `shop-domain` header. `Utils::HmacValidator.validate` will still return `true` because the signature only covers `@raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to Shop B. Any host application that uses `WebhookMetadata#shop` (as the gem's own struct encourages) to key data deletion/redaction, order/customer record updates, or entitlement changes will act on the wrong tenant — a cross-tenant data integrity/confidentiality violation performed with a cryptographically "valid" webhook.

### Likelihood Explanation
This requires the attacker to intercept or otherwise obtain one valid `(raw_body, hmac)` pair for any shop using the app (e.g., via a compromised network path, logging, or simply being a legitimate merchant of the same app who saves their own webhook deliveries) and then re-POST it to the app's webhook endpoint with a different `shop-domain` header. No knowledge of `client_secret` is required, and the mismatch is invisible to the endpoint since the only cross-check performed (`HmacValidator.validate`) never looks at the shop header at all.

### Recommendation
Include the shop domain (and ideally topic/api-version) in the signed material, or explicitly verify `request.shop` against an out-of-band trusted value before constructing `WebhookMetadata`, e.g., extend `Request#to_signable_string` to bind headers that are subsequently trusted, or require callers to independently verify `shop` is one of their installed/active shops (comparing against a stored session) before acting on `WebhookMetadata#shop`.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com` with body `{"id":123}` and a valid `x-shopify-hmac-sha256` header computed over that body with the app's `client_secret`.
2. Attacker (or a malicious co-tenant) captures `raw_body` and the `hmac-sha256` value.
3. Attacker POSTs the same `raw_body` and `hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body`: [6](#0-5) 
5. `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: {"id":123}, ...)` is passed to the handler, which the app treats as an authenticated event for `shop-b`, even though it originated from `shop-a`'s data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-13)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
