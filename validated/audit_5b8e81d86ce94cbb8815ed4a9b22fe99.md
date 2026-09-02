## Title
Webhook shop identity spoofing due to HMAC not covering the `shop-domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while the `shop` identity used by webhook consumers is taken from an unauthenticated HTTP header. `Registry.process` validates the HMAC and then blindly trusts `request.shop` to construct `WebhookMetadata` passed to the app's handler, so an attacker who can obtain one valid `(body, hmac)` pair can replay it against the same endpoint with a forged `shop-domain` header, causing the host app to attribute the payload to a different (victim) shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

but `#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signed material: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC only against `verifiable_query.to_signable_string` (i.e., the raw body): [3](#0-2) 

`Webhooks::Registry.process` validates that HMAC and then, without any further binding check, forwards `request.shop` (from the unauthenticated header) to the handler: [4](#0-3) 

This breaks the intended identity binding: `hmac-signed-bytes == bytes trusted for shop attribution` does not hold, because `shop` is a field acted on (used to route/attribute webhook data to a tenant) but not covered by the HMAC.

### Impact Explanation
An unprivileged Shopify merchant who installs the app on their own store (shop A) is a legitimate holder of a validly-HMAC-signed webhook body for shop A (since Shopify signs the webhook with the app's `client_secret` before delivering it — the attacker only needs to *observe* a delivery, not know the secret). By replaying that exact same body/HMAC pair to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain (shop B), the signature check still passes (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` with attacker-controlled body content. Any app that persists or acts on this data keyed by `data.shop` (as documented/intended usage of this gem) will store or process attacker-supplied data under the victim tenant's identity — a cross-tenant data injection into another merchant's account context. This matches the "Critical - cross-tenant access" impact category since the tenant boundary asserted by the shop identifier is not authenticated.

### Likelihood Explanation
Likelihood is moderate: the attacker needs to be an app installer themselves (any Shopify merchant can install a public app), receive one legitimate webhook delivery for a topic of their choosing, and can then replay that captured HTTP request with a modified header to the app's public webhook endpoint. No secrets, tokens, or privileged access are required — only observing traffic to one's own webhook receiver and crafting a replay, which is achievable by any unprivileged internet user with a Shopify dev store.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is cryptographically verified, or otherwise cross-check the header-derived shop against an independently trusted source (e.g., look up the webhook subscription owner by `webhook_id` via the Admin API, or maintain a nonce/replay cache keyed by `(shop, webhook_id)`). At minimum, document and encourage host apps to treat `data.shop` from webhooks as a routing hint rather than an authenticated identity, and add replay protection (e.g., de-duplicating by `webhook_id`).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook, capturing the raw body `B` and the `X-Shopify-Hmac-Sha256` header `H` (valid because Shopify itself signed `B` with the app's `client_secret`).
2. Attacker sends a new HTTP POST to the app's webhook endpoint with the same body `B`, the same `H`, but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Request.new` parses the forged headers; `Registry.process` calls `HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(B, secret) == H`, per `lib/shopify_api/utils/hmac_validator.rb`.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, per `lib/shopify_api/webhooks/registry.rb` lines 188-200 — the host app now processes attacker-controlled data as if it belonged to the victim shop.

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
