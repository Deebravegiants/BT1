### Title
Webhook `shop` tenant identity is taken from an HMAC-unauthenticated header, breaking `data.shop == HMAC-verified sender` binding - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
The reported ZkSync issue is a class of bug where an identity value that access-control logic trusts (`msg.sender`) is not actually bound to the entity it is assumed to represent. The same class of bug exists in this gem's webhook processing: the `shop` value delivered to app webhook handlers is read from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` HTTP header, which is **not** covered by the HMAC signature. `Registry.process` validates only the raw body against the HMAC, then unconditionally forwards the attacker-controllable header value as the trusted tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

Note that `to_signable_string` returns only `@raw_body` — the HMAC signature covers the request body bytes exclusively. The `shop` accessor, however, is read straight from the `shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates the HMAC of the body, then builds `WebhookMetadata` using `request.shop` (the header) without any cross-check against the body content or any allow-list of shops the app has installed on: [3](#0-2) 

`WebhookMetadata#shop` is then handed to the app's `WebhookHandler#handle` as the authoritative tenant identifier: [4](#0-3) 

The equality the code implicitly assumes is: **shop_header == shop_that_the_HMAC-signing_secret_authenticated**. In fact the HMAC only proves "the body was produced/known by someone possessing the app's shared `client_secret`" (a secret shared across *every* shop that has the app installed) — it says nothing about which shop the header claims. Because `client_secret` is common to all installs of the same app, an attacker who legitimately installs the app on their own shop can generate a validly-HMAC-signed webhook body (e.g., by triggering `orders/create` on their own store), then replay that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop that also has the app installed. `HmacValidator.validate` will succeed (it only recomputes HMAC over `raw_body`), and `Registry.process` will call the handler with `WebhookMetadata(shop: <victim>, body: <attacker's own data>)`.

### Impact Explanation
This breaks the tenant boundary the gem is expected to preserve for a multi-tenant app: the handler is given attacker-controlled data (chosen topic/body up to being a registered topic) tagged with a victim shop's identity, since the shop attribution is not cryptographically bound to the payload. Any app that uses `data.shop` from `WebhookMetadata` to key its per-tenant datastore, trigger per-tenant side effects (fulfillments, refunds, notifications, GDPR redaction flows, etc.) without additional shop verification can be made to write/act on the wrong tenant's records — a cross-tenant data integrity/isolation violation reachable by an unprivileged internet user who is merely a legitimate low-privilege user of the app on their own store (no access token, no leaked credential, no privileged account needed).

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker must (a) have (or create) their own shop with the app installed so they can generate one genuinely HMAC-valid webhook body/signature pair for the shared `client_secret`, and (b) know or guess a victim shop domain that also has the app installed. Both are realistic for any public/multi-tenant Shopify app (shop domains are often discoverable, and installing a free dev/trial store is trivial for anyone). No possession of the actual `api_secret_key` value is required — only a validly-signed payload obtainable through the attacker's own legitimate use of the app.

### Recommendation
Bind the shop identity to the authenticated content instead of trusting an unauthenticated header:
- Include the shop domain in the signed content the app verifies, cross-checking `request.shop` against a shop value derivable from `raw_body` (many webhook payloads already carry the shop's `myshopify.com` domain / shop id in the JSON body), or
- Require the host application to look up an existing installed `Session` for the shop asserted in the header before trusting `WebhookMetadata#shop`, and document this requirement clearly in the gem, or
- Extend `to_signable_string` / the HMAC computation to incorporate the shop-domain header so that `Utils::HmacValidator.validate` fails if the header is tampered with relative to what was actually signed by Shopify for that shop.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`. Trigger a topic the app registers (e.g. `orders/create`) to receive a genuine webhook POST with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Capture the raw POST.
3. Replay the identical body `B` and header `H` to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com` (a shop with the app installed).
4. `ShopifyAPI::Webhooks::Request#hmac` reads `H` from the header and `to_signable_string` returns `B`; `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)` and finds it equal to `H` — validation passes.
5. `Registry.process` constructs `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: JSON.parse(B), ...)` and calls the app's `handler.handle(data: ...)`, which now believes attacker-controlled order data belongs to the victim shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-24)
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

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
