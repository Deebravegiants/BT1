### Title
Webhook HMAC only covers the raw body, allowing tenant (`shop`) spoofing via unauthenticated headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verified by `Registry.process` never covers the `shop`, `topic`, `api-version`, or `webhook-id` values, even though those are the exact values the gem hands to the app's webhook handler for tenant routing.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

so the only bytes protected by the HMAC are `@raw_body`. Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC over that signable string, then immediately trusts `request.shop`/`request.topic`/etc. to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The webhook HMAC secret (`api_secret_key`) is a single shared secret for the whole app, not per-shop. This means: for any *(raw_body, hmac)* pair that is valid for one shop's webhook delivery, that same pair remains a valid `(raw_body, hmac)` pair regardless of what value is placed in the `shopify-shop-domain` header, because the header is never part of the signed content. The documented usage pattern explicitly routes app-side tenant logic using this unauthenticated field: [4](#0-3) 

This breaks the intended identity binding: `HMAC-verified bytes == shop attributed to the request` no longer holds — the equality that should hold is `to_signable_string ⊇ {shop}` but instead `to_signable_string == {raw_body only}`.

### Impact Explanation
Any actor who can obtain one genuine, validly-HMAC'd webhook delivery (trivially achievable by installing the app on their own store, a capability available to any unprivileged internet user for public/dev apps) can replay the identical `raw_body` + `hmac-sha256` header pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value. Because `Registry.process` only checks the HMAC of the body and then unconditionally forwards `request.shop` to the app's handler, this is a cross-tenant spoofing primitive: the app will process attacker-controlled webhook data attributed to a victim shop it does not control, satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires no possession of `api_secret_key`, tokens, or privileged accounts — only (a) the ability to install the target app once on an attacker-owned shop to harvest one legitimately signed webhook body/HMAC pair, and (b) the ability to POST to the app's public webhook endpoint with forged headers, both of which are available to any unprivileged internet user/merchant.

### Recommendation
Include the identity-relevant header fields (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the HMAC-signed payload used for verification (or otherwise cryptographically bind them, e.g. by concatenating them into `to_signable_string`), so that `Registry.process` cannot be fed a webhook whose attributed `shop`/`topic` differ from what was actually signed by Shopify.

### Proof of Concept
1. Install the vulnerable app on attacker-owned shop `attacker.myshopify.com`; capture a genuine webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's shared `api_secret_key`).
2. Replay a POST to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks `H` against `B` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb`).
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `shop: "victim.myshopify.com"`, causing the app to process/attribute attacker-controlled webhook data as belonging to the victim tenant.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
