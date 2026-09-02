Confirmed: `Registry.process` at [1](#0-0)  builds `WebhookMetadata` from `request.shop`, `request.topic`, and `request.webhook_id` — all of which are read straight from HTTP headers via `Request#shopify_header` — while the HMAC (`Request#to_signable_string`) only signs the raw body [2](#0-1) .

### Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not bound to the HMAC signature, enabling cross-tenant webhook shop-spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, and separately exposes `shop`, `topic`, `api_version`, and `webhook_id` from HTTP headers that are never included in the signed content. `Registry.process` validates the HMAC and then unconditionally trusts these header-derived fields to build `WebhookMetadata`, which the host app's handler uses as the tenant identifier for the webhook.

### Finding Description
`Request#hmac` and `Request#to_signable_string` bind the signature to `@raw_body` alone: [3](#0-2) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled from headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) with no cryptographic tie to the body or to each other: [4](#0-3) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (body signature) before handing the header-derived `shop`/`topic`/`webhook_id` straight to the handler as trusted identity fields: [1](#0-0) 

The identity binding this breaks: `shop authenticated (i.e., covered by a signature originating from Shopify for that specific shop) == shop used by the host app as the tenant/session key for the delivered payload`. Because the header carrying `shop` is never part of the signed material, the equality does not hold — the HMAC only proves "this body was signed with the api_secret_key for *some* webhook Shopify sent," not "this body belongs to the shop named in this request's header."

### Impact Explanation
Any merchant who installs the app (an unprivileged action requiring no special access) legitimately receives valid Shopify webhooks — with a body and HMAC signed for their own shop — for their own store. Because the headers are not covered by the signature, that attacker-merchant can capture one legitimate `(raw_body, hmac)` pair from their own shop's webhook delivery and replay it to the app's webhook endpoint while substituting the `shop-domain` (and/or `topic`/`webhook-id`) header with a victim shop's identifier. `HmacValidator.validate` still succeeds because it only checks the body against the secret, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload is `data.shop == victim-shop`. Any app that uses `data.shop` (as documented/intended in this gem) to key persistence, trigger `shop/redact` or `app/uninstalled`-style side effects, or fetch/update per-tenant state, can be made to act on attacker-supplied data under another tenant's identity — a cross-tenant confusion/injection primitive.

### Likelihood Explanation
Moderate-to-high: exploitation only requires the attacker to install the target app on their own shop (standard, unprivileged) and replay one captured webhook HTTP request with a modified header — no access to `api_secret_key`, TLS interception, or victim credentials is needed. The gem's documented usage pattern (`WebhookMetadata#shop` as the identity for the delivered event) makes this directly reachable through the library's own public API surface.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed material (or otherwise cryptographically bind them to the body/HMAC), or at minimum document loudly that `Request#shop`/`#topic`/`#webhook_id` are unauthenticated header values that callers must independently verify against a known/installed shop list before using them as a tenant key.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers/receives a legitimate webhook, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header (valid signature for that body, computed by Shopify with the app's `api_secret_key`).
2. Attacker resends the identical `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [5](#0-4) .
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` [6](#0-5) , causing the host app to process attacker-controlled body content under the victim shop's identity.

### Citations

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
