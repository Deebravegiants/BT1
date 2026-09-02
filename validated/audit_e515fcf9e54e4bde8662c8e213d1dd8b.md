### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers and are never included in the HMAC-signed data. `Webhooks::Registry.process` verifies the HMAC over the body only and then hands the header-derived `shop` value to the app's handler as the trusted tenant identity, breaking the binding `verified_bytes == acted_on_field`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `shop`, `topic`, `webhook_id` are pulled purely from headers with no cryptographic tie to the body: [2](#0-1) 

`Registry.process` validates the HMAC (which covers only `@raw_body`) and then constructs the metadata handed to the app's handler using the *unverified* `request.shop` header value: [3](#0-2) 

The identity binding that should hold is:
`HMAC-verified bytes (body) == bytes that determine which shop/tenant the payload is attributed to (shop header)`

This equality does not hold: the HMAC only proves "this body was produced with the app's secret," it says nothing about which shop the body belongs to. `shop-domain`/`x-shopify-shop-domain` is attacker-controllable header data that the gem trusts and forwards to the handler as `WebhookMetadata#shop` without any check that it matches the shop that actually produced the signed body.

### Impact Explanation
An unprivileged internet user who has legitimately installed the app on their own shop (Shop A) can receive one genuine, validly-HMAC-signed webhook delivery (body + hmac) from Shopify for Shop A. Because the HMAC signs only the body and never the `shop-domain` header, the attacker can replay that exact `(raw_body, hmac)` pair against the app's public webhook endpoint while substituting the `shop-domain` header with a victim shop's domain (Shop B). `Utils::HmacValidator.validate` still succeeds (body/hmac unchanged), and `Registry.process` forwards `shop: "B.myshopify.com"` to the app's handler together with Shop A's attacker-controlled body content. Any app that uses `WebhookMetadata#shop` to select the tenant record to update (the documented, intended use of this field) will apply attacker-supplied data to the wrong tenant — a cross-tenant data-integrity/access violation achievable with no credentials beyond a legitimate self-signup on the attacker's own shop.

### Likelihood Explanation
High. Webhook endpoints are public URLs by design; an attacker only needs their own (free/trial) shop installation to harvest one valid `(body, hmac)` pair, then can replay it indefinitely with an arbitrary spoofed `shop-domain` header. No secrets, tokens, or privileged access are required — only the gem's own signing scope (body-only) is the root cause.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material, or otherwise cryptographically bind the header-derived `shop` value to the verified payload before it is trusted (e.g., verify the resolved shop against an existing, previously-established session/installation record keyed by a value derived from the HMAC-covered content, not from raw headers). At minimum, document/require that the `shop-domain` header be validated against the app's own known installations before being used to route or attribute the webhook payload.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com`, triggers a webhook event, and captures the raw POST: headers (including `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker-shop.myshopify.com`) and body `B`.
2. Attacker resends the exact same body `B` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate(request)` succeeds because it only checks `Digest.hexencode(...)` against `to_signable_string` (`@raw_body`), which is unchanged. [4](#0-3) 
4. `Registry.process` invokes the app handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` where `request.shop` is `"victim-shop.myshopify.com"` — the app now attributes attacker-controlled body `B` to the victim shop. [5](#0-4)

### Citations

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
