This confirms the finding: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over that raw body string. However, `Registry.process` builds `WebhookMetadata` (which the app's handler uses to route/attribute data to a shop) from `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all of which are read from unauthenticated HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are never included in the signed bytes.

### Title
Webhook shop/topic/metadata headers are not covered by HMAC verification, allowing shop-identity spoofing on replayed webhook bodies - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by verifying the HMAC over the raw body bytes, but the shop, topic, webhook id, and API version that the app's `WebhookHandler` receives and acts on are parsed from separate, unsigned headers.

### Finding Description
`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string` to compute the expected signature [1](#0-0) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`, none of the Shopify headers [2](#0-1) . Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers independently of the signed content [3](#0-2) . `Registry.process` verifies only `Utils::HmacValidator.validate(request)` (i.e., the body) and then builds `WebhookMetadata` directly from those unauthenticated header-derived accessors [4](#0-3) .

This breaks the intended identity binding: `shop` (the tenant identity the handler will act on) should equal the shop that actually produced/signed the payload, but the gem only proves "these bytes were HMAC'd with our secret" — it proves nothing about which shop's header value accompanies them. Any unprivileged party who can obtain one valid `(raw_body, hmac)` pair signed with the app's secret (e.g., by installing the app on a shop they control and receiving a real webhook) can resend that exact body/HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header with an arbitrary value, since none of those fields are part of the signed string.

### Impact Explanation
Downstream handlers (per the gem's own documented usage) key their logic off `data.shop` from `WebhookMetadata` to determine which merchant's records to update, delete, or resync [5](#0-4) . Because `shop` is unauthenticated, an attacker who owns a legitimate (even free/dev) shop installation can cause the app to attribute a passing-HMAC payload to a victim shop of their choosing — a cross-tenant confusion/write primitive entirely from the gem's own verification path, without needing the app's `client_secret` or any privileged credential.

### Likelihood Explanation
The attacker only needs to run the app on any shop they control (a normal, unprivileged action for an app developer/tester) to capture one legitimate `(raw_body, hmac)` pair, then replay it against the app's public webhook endpoint with a modified `shop-domain` header. No secret material, TLS interception, or victim interaction is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed bytes checked by `HmacValidator`, or independently verify `request.shop` against a shop known to be legitimately installed/associated with the received body (e.g., cross-check against the `X-Shopify-Shop-Domain` used when computing the HMAC via Shopify's canonical process), so header values cannot be swapped independently of the verified body.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com` and trigger any subscribed webhook topic; capture the raw POST body and its `X-Shopify-Hmac-Sha256` header — this HMAC is valid because `to_signable_string` only covers `raw_body`.
2. Resend that identical `raw_body` and `hmac` header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` [6](#0-5) , which succeeds because the body/hmac pair is genuinely valid.
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload/HMAC actually originated from `attacker-shop.myshopify.com`'s installation, causing the app to process the attacker's data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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
