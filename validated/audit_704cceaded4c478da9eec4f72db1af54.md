This confirms the finding. The `Registry.process` method in `lib/shopify_api/webhooks/registry.rb` only validates the HMAC over the raw body, and separately trusts the `shop` header from `Request#shop` — which is never part of the signed bytes.### Title
Webhook `shop-domain` header is not covered by the HMAC, allowing cross-tenant shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the `shop` identity that gets handed to the app's handler is read from an HTTP header that is never included in the signed bytes. This breaks the binding: `shop verified by HMAC == shop attributed to the data`.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC exclusively from `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body`: [1](#0-0) 

The `shop` (and `topic`, `api_version`, `webhook_id`) values are pulled from HTTP headers that are completely outside the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC of the body only, then unconditionally trusts `request.shop` to build the `WebhookMetadata` passed to the app-defined handler: [3](#0-2) [4](#0-3) 

Because the same `Context.api_secret_key` (the app's single client secret) is used to sign webhooks for *every* shop that has installed the app, an unprivileged attacker can:
1. Install the target app on their own store (any internet user can do this — no privileged access required), and receive legitimately-signed webhook deliveries for their own shop (valid `raw_body` + `x-shopify-hmac-sha256`).
2. Replay that exact `raw_body`/HMAC pair to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain.
3. `HmacValidator.validate` still succeeds, because the signature only ever covered `raw_body`, which is unchanged. `Registry.process` then calls the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

This equality that the gem implicitly promises — "shop authenticated by HMAC == shop the handler processes data for" — does not hold, because the shop is verified nowhere.

### Impact Explanation
Any app built on top of this gem's webhook handling receives, from the gem itself, an unauthenticated `shop` value inside a payload the gem asserts is "HMAC verified". Handlers built following the documented pattern (`docs/usage/webhooks.md`, `BREAKING_CHANGES_FOR_V15.md`) key their side effects (data updates, session lookups, job enqueueing) off `data.shop`. An attacker can therefore inject arbitrary attacker-controlled webhook bodies "as" any other tenant (shop) of the app, leading to cross-tenant data corruption/injection — e.g., forging `orders/create`, `app/uninstalled`, or `customers/data_request` events attributed to a victim shop, potentially triggering unauthorized actions, data deletion flows, or GDPR-workflow abuse against a shop the attacker does not control. This is a cross-tenant identity-binding failure baked into the gem's core webhook API, not merely a misuse of a documented contract, since the gem exposes `request.shop` as the authenticated identity of the payload.

### Likelihood Explanation
High likelihood for exploitation feasibility: no privileged credentials, tokens, or `api_secret_key` are needed by the attacker — only the ability to install the app on their own store (a normal, self-service action for anyone) and then send an arbitrary HTTP POST with attacker-controlled headers to the app's public webhook endpoint. The gem's own header-parsing/validation logic (`Request#initialize`, `Registry.process`) provides no defense, and nothing in the library ties `shop` to the HMAC.

### Recommendation
Include the `shop` (and ideally `topic`, `api_version`, `webhook_id`) values in the signable string used for HMAC validation of webhook requests, or otherwise cryptographically bind the shop identity to the verified payload before it is handed to `WebhookMetadata`/the handler. At minimum, document/enforce that consuming apps must independently verify that `data.shop` corresponds to a shop with a currently valid, active installation/session before trusting webhook content — but since the gem currently presents `shop` as if it were validated alongside the HMAC, the safer fix is inside `Webhooks::Request#to_signable_string` in `lib/shopify_api/webhooks/request.rb` and `Webhooks::Registry.process` in `lib/shopify_api/webhooks/registry.rb`.

### Proof of Concept
1. Attacker creates a free/dev store `attacker.myshopify.com` and installs the victim app (self-service, no privilege needed).
2. App's webhook endpoint receives a legitimately Shopify-signed webhook for `attacker.myshopify.com`, e.g.:
   ```
   POST /webhooks/orders_create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-raw-body>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"id": 1, "note": "malicious payload attacker controls via own order"}
   ```
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value, then re-sends the same POST to the same endpoint, but with:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
   (body and HMAC header byte-for-byte identical to step 2).
4. `Registry.process` → `Utils::HmacValidator.validate(request)` re-computes HMAC over `raw_body` only (per `Webhooks::Request#to_signable_string`) → matches → validation passes.
5. Handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-crafted body>, ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop's Shopify webhook feed.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
