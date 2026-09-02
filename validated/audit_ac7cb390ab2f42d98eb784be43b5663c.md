This confirms the finding. The webhook `topic` and `shop-domain` headers are used to route data and identify the tenant but are excluded from the HMAC signature, which covers only the raw body.### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body. The `shop` and `topic` values that the library then hands to the host application's webhook handler are read from HTTP headers that are never included in the signed payload, breaking the intended binding `authenticated_body == authenticated_tenant`.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC using `verifiable_query.to_signable_string` as the signed material [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from unauthenticated headers (`shopify-shop-domain`, `shopify-topic`, etc.) [2](#0-1) .

`Registry.process` validates only this body-bound HMAC, then immediately trusts `request.shop` and `request.topic` to build the `WebhookMetadata` object dispatched to the app's handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no cryptographic binding to the body or its HMAC [4](#0-3) .

Because the HMAC secret (`api_secret_key`) never signs the `shop-domain` header, any body+HMAC pair that was legitimately produced by Shopify for one shop (e.g., a webhook the attacker's own store received, which the attacker fully controls and can trigger/observe) remains a valid signature when replayed with a forged `shopify-shop-domain` (and/or `shopify-topic`) header claiming a different tenant. The equality the gem is supposed to enforce - "the shop this body was authenticated for" == "the shop the handler is told it came from" - does not hold.

### Impact Explanation
This is a cross-tenant identity-binding break: a body cryptographically authenticated as originating from Shopify for shop A can be relabeled as belonging to shop B (or to a different topic) purely by manipulating unauthenticated headers, since `Registry.process` performs no shop/topic authentication beyond the body HMAC. Any host application that uses `request.shop`/`data.shop` (as encouraged by this library's own webhook API) to key data storage, route to per-tenant handlers, or scope side effects can be made to attribute attacker-supplied webhook content to an arbitrary victim shop, i.e., cross-tenant data injection/confusion.

### Likelihood Explanation
Exploitation requires only: (1) the ability to trigger or capture one legitimate Shopify webhook delivery for any shop the attacker controls (any merchant/app installer can do this by taking normal store actions), and (2) the ability to POST directly to the app's public webhook endpoint with modified headers, which is a normal unprivileged HTTP capability since webhook endpoints are internet-reachable by design. No access token, `api_secret_key`, or privileged account is needed.

### Recommendation
Include the `shop` (and ideally `topic`) header values in the signed material used by `Utils::HmacValidator`, or independently verify that the `shopify-shop-domain` header matches an expected/registered shop before dispatching to the handler, so that the identity used for tenant routing is cryptographically bound to the same HMAC that authenticates the payload.

### Proof of Concept
1. Attacker installs the app on their own store (`attacker-shop.myshopify.com`) and triggers any webhook (e.g., `orders/create`), capturing the resulting `raw_body` and the corresponding `x-shopify-hmac-sha256` value from a real Shopify delivery.
2. Attacker POSTs to the victim app's webhook endpoint reusing that exact `raw_body` and `hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`).
3. `HmacValidator.validate` recomputes the HMAC over `raw_body` only [1](#0-0)  - it still matches, since the shop header was never part of the signed string.
4. `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [5](#0-4) , causing the host application to process attacker-controlled webhook content under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
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
