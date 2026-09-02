## Finding [1](#0-0) 

### Title
Webhook shop-tenant binding not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content (`to_signable_string`) from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from unauthenticated HTTP headers that are never covered by the signature. `Registry.process` validates only that the body is correctly signed, then forwards the header-derived `shop` value straight to the handler as the tenant identity.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [2](#0-1) 

`Request#shop` is read verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed payload: [3](#0-2) 

`HmacValidator.validate_signature` only recomputes the HMAC over `to_signable_string` (i.e., the body) and compares it to the `hmac-sha256` header: [4](#0-3) 

`Registry.process` checks only that this body-only HMAC is valid, then immediately trusts the header-derived `shop` (along with `topic`/`webhook_id`) to build the `WebhookMetadata` passed to the app's handler: [5](#0-4) 

The equality the gem should enforce is: `shop_bound_by_signature == shop_used_for_tenant_routing`. In reality, `shop_bound_by_signature` doesn't exist at all — the signature binds only the body bytes, not the shop header — so `shop_used_for_tenant_routing` is fully attacker-controllable once any single valid `(body, hmac)` pair is obtained. This mirrors the report's root-cause pattern: a state/field that gates a privileged action (`isActive`/`startTimestamp` for claim creation there; `shop` for tenant routing here) is not bound by the mechanism (`hasNoClaim` modifier there; HMAC signature here) that is supposed to enforce the invariant.

### Impact Explanation
An unprivileged internet user can install the target app on their own (attacker-owned) shop for free, trigger any webhook topic the app subscribes to, and capture the resulting `(raw_body, X-Shopify-Hmac-SHA256)` pair — both fully within their control since it's their own shop's data. They can then replay that exact body and HMAC header to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (e.g., a victim merchant's domain). `Utils::HmacValidator.validate` still succeeds because it never inspects the shop header, and `Registry.process` calls the app's handler with `shop: request.shop` set to the attacker-chosen victim domain. Any app that uses `WebhookMetadata#shop` to look up/authorize the tenant (the documented purpose of this field) will process attacker-supplied data as if it originated from the victim shop, constituting cross-tenant access/data injection.

### Likelihood Explanation
High. `WebhookMetadata#shop` is the primary attribute apps are expected to use to route webhook data to the correct merchant record, so this pattern is very likely to be relied upon downstream. Obtaining a valid `(body, hmac)` pair requires nothing more than installing the (presumably public) app on an attacker-owned development/trial shop — no access token, no `api_secret_key`, and no privileged account is required.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the HMAC-verified content, or otherwise cryptographically tie the header values to the signed body (e.g., include them in the signable string, or require the caller to separately verify header-to-body binding via a nonce/id embedded in both). At minimum, document/require host apps to independently authenticate `shop` against an existing, already-installed session before trusting `WebhookMetadata#shop`, and update `VerifiableQuery#to_signable_string` for webhooks to incorporate the header fields it currently ignores.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g., `orders/create`, with body `B` and header `X-Shopify-Hmac-SHA256: H` (valid for secret `S`).
2. Attacker sends a new HTTP POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes HMAC over `B` only, matches `H`, and returns `true` ( [4](#0-3) ).
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` ( [6](#0-5) ), causing the app to process attacker-controlled order data as if it belongs to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-38)
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
