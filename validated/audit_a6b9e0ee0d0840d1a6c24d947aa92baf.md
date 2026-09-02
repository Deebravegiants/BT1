## Finding [1](#0-0) 

### Title
Webhook shop-domain and topic headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature verified by `Utils::HmacValidator.validate` binds nothing but the byte content of the body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from unauthenticated HTTP headers and handed to the handler as trusted identity fields, exactly mirroring the reported bug class of "a property acted on but not actually bound by the cryptographic check."

### Finding Description
`Registry.process` verifies a webhook by calling `Utils::HmacValidator.validate(request)`, which recomputes an HMAC over `request.to_signable_string` and compares it to `request.hmac`: [2](#0-1) 

`to_signable_string` is defined as `@raw_body` only: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are not part of the signed material: [3](#0-2) 

Those unauthenticated values are then passed straight into the handler as the merchant/tenant identity for the event: [4](#0-3) 

Contrast this with the OAuth `AuthQuery`, where `shop` and `host` are explicitly included inside `to_signable_string` and therefore cryptographically bound to the signature: [5](#0-4) 

This is precisely the identity-binding gap described in the report: the equality that should hold is `shop used for HMAC == shop used for authorization decision`, but here the HMAC only authenticates `raw_body`, while `shop` (the tenant identity acted upon by `WebhookHandler.handle`) is taken from a header outside that binding. An attacker who legitimately installs the app on their own shop (an unprivileged action requiring no special access) will receive genuinely-signed webhooks from Shopify for their own store. Because the signature covers only the body bytes, the attacker can replay that valid `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) for a different, victim shop domain. `Utils::HmacValidator.validate` will still succeed (same body, same secret, same signature), and `Registry.process` will invoke the handler with `WebhookMetadata` claiming the event came from the victim shop.

### Impact Explanation
Any host application built on this gem that uses `data.shop` from `WebhookMetadata` to select the tenant context for processing (exactly as the gem's own documentation example does — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to process attacker-supplied webhook bodies under another merchant's shop identity. This is a cross-tenant confusion/spoofing primitive: it lets one merchant (attacker) inject falsified webhook data attributed to another merchant's shop, which is a cross-tenant boundary violation.

### Likelihood Explanation
The prerequisite — being an installed merchant on the app, and therefore able to receive real, validly-signed webhook payload/HMAC pairs for arbitrary topics they subscribe to — is available to any unprivileged internet user who installs the target app on a store they control. Forging the header afterward requires no secret material at all, only replaying the captured `(body, hmac)` pair with a modified `shop-domain`/`topic` header, which is why this is "High" likelihood once the attacker holds a genuine sample.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` values in the signable string (or otherwise cryptographically bind them, e.g., HMAC over a canonical string of `raw_body + shop + topic`), matching the approach already used for `AuthQuery#to_signable_string`. At minimum, document that `WebhookMetadata#shop`/`#topic` are not authenticated by the HMAC and must not be used as the sole tenant-identity source without cross-checking against a shop known to have installed the app for that specific topic/webhook id.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and subscribes to a webhook topic (e.g. `orders/create`).
2. Shopify sends a legitimately signed webhook: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, header `x-shopify-shop-domain = attacker-shop.myshopify.com`.
3. Attacker captures this `(B, HMAC(secret, B))` pair and resends it to the app's webhook endpoint, replacing the header with `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or the topic header).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which recomputes the HMAC over `raw_body` only — it matches, since `raw_body` and secret are unchanged.
5. The handler executes with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: B, ...)`, so the host application treats attacker-controlled body content `B` as authoritative data belonging to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
