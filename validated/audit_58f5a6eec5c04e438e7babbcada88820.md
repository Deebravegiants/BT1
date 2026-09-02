### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are not covered by the HMAC signature, allowing shop-identity spoofing in `Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so `Utils::HmacValidator.validate` verifies nothing but body integrity. The `shop` (and `topic`, `webhook_id`, `api_version`) values, which are taken straight from unauthenticated HTTP headers, are passed on unchanged to the host application's webhook handler as the tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns `@raw_body` only — the `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from headers and are never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` directly from `request.shop`, `request.topic`, etc., handing it to the app's registered handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no further validation: [4](#0-3) 

The identity binding this breaks, expressed as an equality that should hold but doesn't:
`shop_identity_verified_by_HMAC == shop_identity_delivered_to_handler`

In fact `HMAC(body)` proves only "Shopify (or anyone knowing the app's shared `client_secret`) produced this exact body" — it says nothing about which shop the body came from. The `X-Shopify-Shop-Domain` header is the *sole* source of shop identity delivered to the handler, and it is completely unauthenticated.

Because a Shopify app's `client_secret` is shared across every shop that installs the app (it is not shop-specific), any unprivileged user who installs the app on their own store can legitimately trigger webhooks and thus obtain valid `(body, HMAC)` pairs signed with the app's secret. That attacker can then replay the exact same body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and, if useful, the topic/webhook-id headers) with an arbitrary victim shop domain. `HmacValidator.validate` will report success because it only checks the (unmodified) body against the (unmodified) HMAC — it never inspects the shop header — and the handler will be invoked believing the event originated from the victim shop.

### Impact Explanation
Most webhook-handling host applications key their persistence layer, feature flags, uninstall logic, and rate limits by the `shop` value delivered in `WebhookMetadata`. An attacker able to forge the shop attribution of a webhook can inject or manipulate data attributed to a different tenant (cross-tenant access), for example spoofing an `app/uninstalled` or `shop/redact` event for a victim shop, or feeding forged `orders/*`, `customers/*` payloads that get persisted under the victim's shop record. This is a cross-tenant data-integrity/identity break reachable by any unprivileged internet user who can install the app once on a store they control, satisfying the "Critical – cross-tenant access" bar since no credentials, access tokens, or `client_secret` need to be stolen; only the shared, non-secret app HMAC key is used the way it is designed to be used (by the attacker's own legitimately-installed shop).

### Likelihood Explanation
Likelihood is high for any deployment that relies on this gem's `Webhooks::Registry`/`WebhookHandler` for tenant identification (which is the intended, documented usage pattern). The attacker only needs to install the target app once on a shop they control (or otherwise trigger any webhook), capture the raw HTTP request, and replay it with a different `X-Shopify-Shop-Domain` header value against the same public webhook endpoint. No secret material is required.

### Recommendation
Include the shop domain (and ideally the other identifying headers) in the HMAC-signed payload rather than relying on the raw body alone, or otherwise cryptographically bind the header the handler is going to trust. If the header set genuinely cannot be changed to match Shopify's real payload signing scheme, applications must be explicitly warned in the gem's documentation that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host app against a shop it has verified out-of-band (e.g. matching the shop against a previously stored/active session before trusting the payload). At minimum, `Webhooks::Registry.process` should not silently hand the unauthenticated `shop` value to handlers without such a warning/guard.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, and captures a legitimate webhook POST, e.g. for `orders/create`, including its correctly computed `X-Shopify-Hmac-Sha256` header (computed over the raw JSON body using the app's `client_secret`, per `HmacValidator.compute_signature`).
2. Attacker resends the identical raw body and identical `X-Shopify-Hmac-Sha256` header to the same public webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (a shop the attacker does not control).
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`; because validation is computed solely against `request.to_signable_string` (`@raw_body`), it succeeds — see `lib/shopify_api/utils/hmac_validator.rb:12-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
4. `Registry.process` then invokes `handler.handle(data: WebhookMetadata.new(topic:, shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"` — see `lib/shopify_api/webhooks/registry.rb:188-200` — even though the payload actually originated from the attacker's own shop.
5. Any host application logic keyed by `WebhookMetadata#shop` (data storage, uninstall handling, redaction, billing, etc.) now operates on the victim shop's identity using attacker-supplied data.

### Citations

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
