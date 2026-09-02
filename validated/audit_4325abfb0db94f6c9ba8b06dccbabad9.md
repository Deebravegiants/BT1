### Title
Webhook shop identity is not bound to HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the request's `to_signable_string`, then immediately trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler: [1](#0-0) 

The `to_signable_string` implementation only returns the raw JSON body: [2](#0-1) 

But `shop` is read straight from the unauthenticated HTTP header `x-shopify-shop-domain` / `shopify-shop-domain`, which is never included in the HMAC-signed content: [3](#0-2) 

The equality the library implicitly relies on is:
`verified(HMAC over raw_body) == identity used for dispatch (shop header)`

but the actual state is:
`verified(HMAC) covers only raw_body bytes`, while `identity used for dispatch (request.shop) is taken from an out-of-band header never covered by that signature`.

Because the HMAC secret (`api_secret_key`) is shared across every installation of a given app, any user who has legitimately installed the app (e.g., on their own development/trial store) can capture one authentic `(raw_body, hmac)` pair delivered to them by Shopify. They can then replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed (it only re-computes the HMAC of the raw body), and `Registry.process` will dispatch to the handler with `data.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the shop field is supposed to establish: the host application's handler (per the gem's own documented usage pattern) uses `data.shop` as the authoritative merchant/tenant identifier to store or act on webhook data (see `docs/usage/webhooks.md`, which instructs handlers to key work off `data.shop`). An attacker can inject data attributed to a shop they do not own/operate, achieving cross-tenant data poisoning/confusion through the webhook path this gem exposes as its trusted authentication primitive.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate (even free-trial) installer of the target app, obtain one webhook delivery, and replay it with a modified header to the public webhook endpoint — no access to `api_secret_key`, access tokens, or the target shop's credentials is needed, and it does not depend on the host app doing anything beyond following the gem's documented `Registry.process` usage.

### Recommendation
Bind the shop identity (and topic) into the value that is cryptographically verified, e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or independently verify that the resolved `shop` corresponds to a shop with a currently registered/active session for this app) before constructing `WebhookMetadata`, rather than trusting the raw header value once the body-only HMAC succeeds.

### Proof of Concept
1. Attacker installs the target app on their own dev store `attacker.myshopify.com` and receives a genuine webhook: raw body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` with the app's `api_secret_key`), header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker POSTs the same body `B` and same header `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over `B` only (per `Request#to_signable_string`) — validation passes.
4. `ShopifyAPI::Webhooks::Registry.process` calls the app's handler with `WebhookMetadata` where `shop == "victim.myshopify.com"`, even though the payload actually originated from the attacker's own shop, causing the host app to process/store the attacker's data under the victim's tenant identity.

### Citations

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
