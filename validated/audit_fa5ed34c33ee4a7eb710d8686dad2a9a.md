### Title
Webhook HMAC covers only the raw body, not the `shop`/`topic` headers, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via `Utils::HmacValidator`, but the signable content used for that check is only the raw request body. The `shop` (tenant identity) and `topic` fields — which the gem hands to the app's `WebhookHandler` as the trusted tenant/action identifiers — are read straight from HTTP headers that are never covered by the HMAC. This breaks the intended binding: `HMAC-verified bytes == bytes the handler trusts for tenant identity`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Registry.process` gates handling solely on that HMAC check: [2](#0-1) 

but `request.shop` and `request.topic` — passed into `WebhookMetadata` and thus into the app's `handle(data:)` callback as the trusted tenant/topic — are pulled from the `shopify-shop-domain` / `shopify-topic` headers, which sit entirely outside the signed payload: [3](#0-2) 

So the equality the design relies on — `HMAC(secret, signable_bytes) == HMAC(secret, raw_body)` implying `shop header == the shop that produced this webhook` — does not hold, because `shop`/`topic` are never part of `signable_bytes`.

Any entity that can obtain one legitimately-signed webhook body+HMAC pair for a shop it controls (e.g., a merchant who installs the app themselves and receives real webhooks) can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still pass because it only recomputes the HMAC over `@raw_body`, which is unchanged. The gem then dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the app's handler with an attacker-chosen `shop`, even though only the body — not the shop attribution — was cryptographically verified.

Per the gem's own documentation, apps are expected to trust `data.shop` for tenant-scoped actions (e.g., enqueuing jobs keyed by `shop_domain`): [4](#0-3) 

This means a webhook that is truly authentic for shop A can be relayed by that same actor with a forged header claiming it originated from shop B, causing the host application to act on shop B's tenant data/state based on attacker-supplied body content that was never actually sent for shop B.

### Impact Explanation
This is a cross-tenant access vector: it lets one actor (owner/operator of shop A, or anyone who intercepts one valid webhook) cause the app to attribute arbitrary webhook payloads to a different, victim shop (shop B) while still passing HMAC validation. Depending on the handler's logic (e.g., `app/uninstalled`, billing, or data-sync handlers keyed on `data.shop`), this can corrupt or leak another tenant's state, matching the "cross-tenant access" Critical-impact category defined in scope.

### Likelihood Explanation
Medium: requires the attacker to possess a validly-HMAC'd body from Shopify (trivially available to any merchant who installs the app on their own store, since Shopify sends real signed webhooks to every installer) and the ability to POST to the app's public webhook callback endpoint with a modified `shop-domain` header — no access token, `client_secret`, or privileged account is needed. The main variable is whether the merchant/host app's own webhook route enforces additional shop-authorization outside of this gem, which is outside this gem's control but not documented as a required mitigation.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable payload used for `HmacValidator.validate`, or independently re-verify that `request.shop` corresponds to a shop for which this exact `hmac`+`raw_body` combination was actually delivered (e.g., only trust `shop` after confirming it via a side channel such as looking up the webhook subscription/shop pairing, not solely from the unauthenticated header). At minimum, document prominently that `data.shop` is not cryptographically bound to the HMAC and must not be trusted as an unforgeable tenant identifier without additional verification by the host application.

### Proof of Concept
1. App installed on `attacker.myshopify.com` registers an HTTP webhook (e.g., `orders/create`).
2. Shopify sends a legitimately signed webhook to the app: `raw_body`, headers include `shopify-hmac-sha256: <valid HMAC of raw_body>`, `shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the identical `raw_body` and `shopify-hmac-sha256` value to the same webhook endpoint, but sets `shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`@raw_body` only) — validation succeeds because the body is unchanged. [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: <attacker's data>, ...)`, and the host app acts on "victim.myshopify.com" using attacker-controlled data. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
