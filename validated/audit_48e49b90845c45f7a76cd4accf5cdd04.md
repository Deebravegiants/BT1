### Title
Webhook Shop/Topic/Webhook-ID Headers Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values — all read from unauthenticated HTTP headers — are trusted and forwarded to the app's webhook handler untouched. This is the same bug class as the reported `minMarketTokens` issue: a value that is *acted upon* (here, tenant identification) is not bound to the cryptographic check that is supposed to guarantee its authenticity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which only checks `to_signable_string` (the body) against the secret, and then immediately passes `request.shop` (and `request.topic`, `request.webhook_id`) into `WebhookMetadata`, which the host app's handler uses to identify the tenant/shop the webhook belongs to: [3](#0-2) 

The identity binding that should hold is:
`shop header value == shop the HMAC-signed body actually originated from`

But since the HMAC (computed with the app's single shared `api_secret_key`, identical across every merchant that installs the app) covers only the body bytes, this equality is never checked. Any request with a `body`+`hmac` pair that is valid for *some* shop, combined with an attacker-supplied `x-shopify-shop-domain` header for a *different* shop, will pass `HmacValidator.validate` and be delivered to the app as if it came from the victim shop.

### Impact Explanation
Because the app-level `api_secret_key` is shared across all shops that install the app (not shop-specific), any merchant who has installed the app can obtain a legitimately-signed `(body, hmac)` pair from their own real Shopify webhook deliveries. They can then replay that exact payload to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to point at a different, victim shop. `Utils::HmacValidator.validate` will report success (it never examines the header values), and the app's handler will process attacker-controlled data under the victim's tenant identity — i.e., cross-tenant data injection/spoofing, satisfying the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Any user who can install the target app on their own Shopify development/trial store (a low bar — no special privilege beyond having a Shopify account) receives real webhook deliveries with valid `(body, hmac)` pairs signed with the app's shared secret. Capturing and replaying these with a modified shop-domain header requires no cryptographic secret and no access to the victim's data — only observation of one's own webhook traffic, which is trivial (proxy/log the request the app itself receives).

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signed content, or otherwise cryptographically verify that the `shop-domain` header value matches the shop the request was actually intended for (e.g., cross-check `shop` against a signed claim, or require verification against a shop-specific secret/session rather than a single global `api_secret_key`). At minimum, document that consumers of `WebhookMetadata#shop` must not treat it as an integrity-verified value and must independently confirm the shop against a value covered by the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook to the app: body `B`, header `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker captures `(B, HMAC(secret,B))` (e.g., via their own reverse proxy/logging in front of the app).
4. Attacker crafts a new HTTP request to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` — this succeeds since `B` is unchanged.
6. `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` is delivered to the app's handler, which processes attacker-controlled data as if it were `victim.myshopify.com`'s webhook.

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
