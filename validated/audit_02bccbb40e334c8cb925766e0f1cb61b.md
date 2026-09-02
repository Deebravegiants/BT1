Based on my investigation, this confirms a solid finding: the webhook `shop` field is documented and used by host apps as the tenant identifier (`data.shop`, `shop_domain`), while the HMAC only ever covers the raw body bytes, not the `shop-domain` header.

### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant shop-identity spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook is authentic by validating an HMAC over the raw request body only. The `shop` (and `topic`, `webhook_id`, `api_version`) values are pulled from separate, unauthenticated HTTP headers and are never included in the signed payload. Any party who can obtain one valid `(raw_body, hmac)` pair signed by Shopify — trivially available to anyone who installs the app on a shop they control — can replay that exact body/HMAC pair to the app's single shared webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. The signature still validates, but the shop identity delivered to the handler is attacker-controlled.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhooks that method returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are extracted straight from HTTP headers with no cryptographic binding to the HMAC at all: [2](#0-1) 

`Registry.process` trusts `request.shop` unconditionally once the HMAC check passes and forwards it to the app's handler as the tenant identifier: [3](#0-2) 

The identity binding that should hold is: `shop header == shop that the HMAC-signed body actually originated from`. This does not hold — the HMAC only proves "these bytes were signed with `api_secret_key`," not "this body belongs to shop X." Since all shops share the exact same callback URL for a given app (the `path` is registered once per app, not per shop), an attacker who legitimately installs the app on their own store (a normal, unprivileged action any internet user can perform for a public app) will receive a genuinely Shopify-signed `(raw_body, hmac)` webhook at their own server. They can then POST that identical body and HMAC to the app's shared webhook endpoint with a forged `x-shopify-shop-domain` header naming a different, victim shop. `HmacValidator.validate` passes (the body/HMAC pair is valid), and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain, `WebhookMetadata.body` containing attacker-controlled content from their own store's webhook.

This is documented as the primary way host apps are meant to consume this data: [4](#0-3) 

### Impact Explanation
Any host application that uses `data.shop` to route processing to per-tenant state (e.g., look up which shop's records to update, which store's job queue to enqueue into, or which merchant's database row to write) can be made to attribute attacker-supplied webhook content to an arbitrary victim shop domain, without the attacker ever possessing the app's `client_secret` or any merchant's access token. This is a cross-tenant data/identity confusion vulnerability rooted entirely in this gem's webhook verification logic, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the app once on an attacker-controlled/dev shop to receive one legitimately signed webhook (available to any internet user for public apps), and (2) sending a single crafted HTTP POST to the app's known webhook path with a substituted `x-shopify-shop-domain` header. No secrets, tokens, or privileged access are required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signable string used for HMAC verification, or otherwise cryptographically tie the shop identity to the signed payload, so that a valid HMAC for one shop's webhook cannot be replayed under a different shop's identity. At minimum, `Registry.process`/`HmacValidator` should reject requests where the header-derived shop cannot be independently corroborated against a known, previously-registered webhook subscription tied to that specific signed payload.

### Proof of Concept
1. Attacker installs the target public app on `attacker.myshopify.com` (any internet user can do this).
2. Shopify sends a legitimate webhook to the app's shared endpoint: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`, header `x-shopify-shop-domain = attacker.myshopify.com`.
3. Attacker's own server (or a MITM-free network capture of their own traffic, which they fully control) records `B` and the HMAC value.
4. Attacker issues a new POST to the app's same webhook path, reusing `raw_body = B` and the same `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` builds a request object with `shop = "victim-shop.myshopify.com"`.
6. `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` and it matches — validation passes because only `B` is checked.
7. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)`, causing the app to attribute attacker-controlled webhook content to the victim shop.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
