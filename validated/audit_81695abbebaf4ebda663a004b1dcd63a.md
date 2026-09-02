### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw webhook body, excluding the `shop-domain` header, yet `ShopifyAPI::Webhooks::Registry.process` trusts that same unauthenticated header to attribute the webhook to a specific tenant when invoking the app's handler.

### Finding Description
Shopify signs inbound webhooks with an HMAC-SHA256 computed over the raw request body using the app's `api_secret_key`, and this library validates that signature via `Utils::HmacValidator.validate`, which calls `verifiable_query.to_signable_string`. For webhooks, `to_signable_string` returns only `@raw_body`: [1](#0-0) 

None of the identifying headers — `shop-domain`, `topic`, `webhook-id`, `api-version` — are included in the signed bytes: [2](#0-1) 

`Registry.process` verifies the HMAC over the body only, then immediately trusts `request.shop` (parsed from the unauthenticated `shop-domain` header) to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

The binding that is broken is: **shop identity acted on (`request.shop`, from the `x-shopify-shop-domain` header) ≠ bytes actually covered by the HMAC (`@raw_body` only)**. Because the same `api_secret_key` is shared by the app across every merchant/shop that installs it, an attacker can:
1. Install the target app on their own (attacker-controlled) shop — a normal, unprivileged action.
2. Receive a real webhook from Shopify for their own shop, with a body and a valid `x-shopify-hmac-sha256` signature.
3. Replay that exact body + HMAC to the app's webhook endpoint, but swap the `x-shopify-shop-domain` header to a victim shop's domain (and/or change `topic`/`webhook-id`, which are also unsigned).
4. `HmacValidator.validate` still passes because the HMAC only covers the body, which is unmodified.
5. `Registry.process` calls the app's handler with `shop: <victim-domain>`, causing the app to process attacker-controlled payload data as if it originated from the victim tenant.

### Impact Explanation
This is a cross-tenant identity-binding break: it lets an unprivileged app installer (no `api_secret_key`, no access token, no privileged account needed) cause the host application's webhook handlers to execute tenant-scoped logic (e.g. order/customer/fulfillment processing, data writes keyed by shop) under an arbitrary victim shop's identity, using data the attacker fully controls. Depending on what the integrating app does in its webhook handler (common patterns include upserting records keyed by `shop`, triggering emails, or syncing data), this can result in cross-tenant data corruption or forged tenant events — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is meaningful: any developer/attacker can freely create a Shopify development store and install a public/dev instance of the target app to legitimately receive at least one real signed webhook, then replay it with a forged shop header against the app's public webhook endpoint. No secrets, tokens, or privileged access are required — only the ability to author raw HTTP requests to the app's webhook listener, which is exactly the class of "unprivileged internet user" attack this exercise targets.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, at minimum) in the HMAC-signable material, or otherwise cryptographically bind `request.shop`/`request.topic` to the signed body before trusting them in `Registry.process`. If Shopify's server-side signing scheme cannot be changed to sign headers, the library should mitigate by cross-checking the resolved shop domain against session/shop registration state (e.g. only accept webhooks for shops with an active, previously-established session) rather than trusting the header value outright when dispatching to handlers.

### Proof of Concept
1. Install the target app (which uses this gem) on an attacker-controlled development shop `attacker-shop.myshopify.com`.
2. Trigger any event so Shopify sends a real webhook, e.g. `orders/create`, to the app's webhook endpoint. Capture the raw body and the `x-shopify-hmac-sha256` header value — both valid and correctly signed with the app's shared `api_secret_key`.
3. Resend an HTTP POST to the same webhook endpoint with:
   - Identical raw body and `x-shopify-hmac-sha256` value from step 2 (still valid, since body is unchanged).
   - `x-shopify-shop-domain` header rewritten to `victim-shop.myshopify.com`.
4. Trace through the library:
   - `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks presence, not authenticity) — `lib/shopify_api/webhooks/request.rb` lines 45-63.
   - `Utils::HmacValidator.validate(request)` succeeds because it only hashes `@raw_body` — `lib/shopify_api/utils/hmac_validator.rb` lines 26-31, `lib/shopify_api/webhooks/request.rb` lines 35-38.
   - `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop` = `"victim-shop.myshopify.com"` — `lib/shopify_api/webhooks/registry.rb` lines 188-199.
5. The app's webhook handler executes business logic attributing the attacker-supplied payload to the victim shop, despite the victim never having sent that webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
