## Finding

### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body. The `shop` (and `topic`/`api_version`/`webhook_id`) values that the handler receives and acts on come from separate, unsigned HTTP headers that are never included in the signed payload. This breaks the identity binding `signed_bytes == acted_upon_shop`, allowing any user who can obtain one genuinely-signed webhook (e.g., by installing the app on their own store) to relabel it as originating from a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers that are not part of the signed content: [2](#0-1) 

`Registry.process` verifies authenticity using only this body-based HMAC and then immediately dispatches the (header-derived, unverified) `shop` to the application handler: [3](#0-2) 

`HmacValidator.validate` confirms the HMAC over `verifiable_query.to_signable_string` (the raw body only), using the app's shared `api_secret_key`: [4](#0-3) 

Because the same `api_secret_key` is used to sign webhooks for every shop that installs the app, a body+HMAC pair generated for one shop's genuine webhook event remains cryptographically valid regardless of which `shop`/`shopify-shop-domain` header value accompanies it. The equality that should hold — "the shop the HMAC authenticates" == "the shop the handler is told this event is about" — does not, because the shop identity is never part of the signed bytes.

### Impact Explanation
An attacker who installs the target app on their own (attacker-controlled) shop can trigger a genuine webhook (e.g., `orders/create`) and capture the resulting `raw_body` and its valid `X-Shopify-Hmac-Sha256` value. They can then POST that identical body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (the body bytes it authenticates are unchanged), and `Registry.process` forwards `shop: <victim-shop>` to the registered handler. Any handler logic that trusts `WebhookMetadata#shop` to attribute or persist data for that shop (the officially recommended and only way this gem exposes the shop to the handler) is deceived into cross-tenant data injection/confusion — a Critical-class cross-tenant access issue per the class of impact defined for this scan.

### Likelihood Explanation
Exploitation requires no credential, access token, or `api_secret_key` — merely the ability to install the target app on any (even the attacker's own) shop to obtain one valid signed webhook, and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a forged `shop` header. Both are available to any unprivileged internet user/merchant, and the webhook endpoint is by design internet-reachable, making this readily reachable.

### Recommendation
Bind shop identity to the signed payload rather than trusting the header value alone: either include the shop domain in the signable string used for HMAC verification, or require host applications to cross-check `WebhookMetadata#shop` against an independently known/expected shop (e.g., the shop associated with the registered webhook subscription id) before acting on it. At minimum, document prominently that `shop`, `topic`, and `webhook_id` are not covered by the HMAC and must not be trusted for authorization decisions without additional verification.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger an event so Shopify sends a real webhook with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's `api_secret_key`).
2. Replay to the app's webhook endpoint:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: H
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Webhook-Id: <any>
   Body: B
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only checks body `B`.
4. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, attributing attacker-controlled order data to the victim shop. [3](#0-2) [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
