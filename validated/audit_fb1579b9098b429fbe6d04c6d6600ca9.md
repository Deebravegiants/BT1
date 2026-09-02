### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only and then hands the header-derived `shop` value straight to the app's handler as the tenant identifier, breaking the binding `hmac(body) == hmac(body)` vs. `shop_used_by_handler == shop_actually_signed_for`.

### Finding Description
`HmacValidator.validate` computes the signature from `verifiable_query.to_signable_string`, and for webhooks that string is defined as just the raw JSON body: [1](#0-0) [2](#0-1) 

`Registry.process` validates only that HMAC, then immediately trusts the (unsigned) `shop` header when constructing the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

Because the HMAC secret (`api_secret_key`) is shared by the app across *all* of its installed shops, any merchant who has installed the app can legitimately receive a real `(body, hmac)` pair for their own shop from Shopify. That merchant can then replay the identical `body`/`hmac-sha256` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header for a victim shop. `HmacValidator.validate` still succeeds — it never looked at those headers — and `Registry.process` forwards the forged `shop` value to the handler as if Shopify itself attested that the payload belongs to that shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce: `shop` authenticated (none) vs. `shop` used to key data/session lookups in the handler (fully attacker-controlled). Any app that uses `WebhookMetadata#shop` to select which tenant's data/session to update (the documented and expected usage pattern) can be made to attribute a self-signed webhook to a different shop, i.e., cross-tenant data injection/confusion — Critical impact per the stated criteria.

### Likelihood Explanation
Requires only an unprivileged internet user who can install the app for one shop (trivial, apps are typically self-installable) and capture one legitimate webhook delivery for their own shop, then replay it with a forged `shop-domain` header against the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required.

### Recommendation
Bind the shop/topic identity to the signed payload: include `shop`, `topic`, `api_version`, and `webhook_id` in the signable string (mirroring Shopify's newer webhook signing recommendations), or require callers to independently verify the `shop` header against a known/registered shop for the resolved topic before trusting it, and document this requirement prominently since `to_signable_string` currently signs the body only.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, receiving a legitimate `orders/create` webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(api_secret_key, B)`).
2. Attacker replays `POST /webhooks` with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds since it only checks `B`/`H` (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-22`).
4. `Registry.process` calls the app's handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled body `B` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to process attacker data under the victim's tenant identity.

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
