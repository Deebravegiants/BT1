### Title
Webhook shop-domain header is not covered by HMAC signature, allowing cross-tenant impersonation in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so the HMAC signature validated by `HmacValidator` binds nothing but the JSON payload. The `shop` (and `topic`, `webhook_id`, `api_version`) values are read straight from unauthenticated HTTP headers and handed to the app's webhook handler as trusted tenant identity. Because the app's `api_secret_key` is shared across every shop that installs the app, any merchant who can get one legitimately signed webhook delivered to their own install can replay that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header, and `Registry.process` will accept it as authentic and dispatch it to the handler labeled with the forged shop.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, which for webhooks resolves to `@raw_body` only: [1](#0-0) 

The `shop` accessor is pulled directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or to any other authenticated value: [2](#0-1) 

`Registry.process` only checks the HMAC of the body before trusting the request, then constructs `WebhookMetadata` using `request.shop` verbatim and passes it to the app-supplied handler: [3](#0-2) 

The identity binding that should hold is:
`shop_header == shop_bound_by_HMAC`

but the actual binding enforced is:
`HMAC(raw_body) == received_signature`, with `shop_header` entirely outside that equality.

Since the `api_secret_key` used to sign webhooks is per-app (not per-shop), any shop that installs the app receives webhooks signed with the same secret as every other installation of that app. An attacker who controls one installation (which requires no privileged access — merely installing a public/development app on their own store) can capture one valid `(raw_body, hmac)` pair and resend it to the app's webhook endpoint with the `shopify-shop-domain` header changed to a victim shop's domain (or any other shop the attacker wants to impersonate). `HmacValidator.validate` will still succeed because it never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` object claiming the payload originated from the victim shop.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as intended and documented) to select which merchant record/session/tenant data the webhook body should update, an attacker can inject data attributed to an arbitrary shop identifier of their choosing — a cross-tenant integrity/confidentiality violation. This satisfies the Critical "cross-tenant access" bucket: the gem's own validation logic (`HmacValidator` + `Webhooks::Request`) fails to bind the tenant identifier to the authenticated bytes, so any downstream use of `data.shop` inherits a forged trust boundary.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple shops (the normal case for any Shopify public/custom app), since:
- No special privilege beyond installing the app on one's own store is required.
- The only "secret" needed to pass validation (the app's `api_secret_key`) is never exposed to the attacker; they only need one authentic delivery from their own shop to reuse the body+signature.
- The header is trivially editable by anyone who can send an HTTP POST to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material, or otherwise cryptographically bind them, e.g. by having `to_signable_string` incorporate the shop header, or by requiring the caller to cross-check `request.shop` against an independently verified session/shop record before trusting `WebhookMetadata#shop`. At minimum, document prominently that `shop` in `WebhookMetadata` is unauthenticated and must not be used as a sole tenant key without additional verification (e.g., confirming the shop has an active session/installation on record).

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) and capture the raw POST: `raw_body`, and header `x-shopify-hmac-sha256`.
2. Resend the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
3. `Registry.process` invokes `HmacValidator.validate`, which recomputes the HMAC solely from `raw_body` [1](#0-0)  and succeeds regardless of the shop header.
4. The handler executes with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: ..., ...)` [4](#0-3) , causing the app to process attacker-supplied data under the victim shop's identity.

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
