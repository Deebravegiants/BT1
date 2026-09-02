### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, then passes the `shop` value extracted from an unauthenticated HTTP header directly to the handler. The identity binding "shop that the HMAC-signed payload came from" ≠ "shop attributed to the delivered data" is broken, because the header is never part of the signed material.

### Finding Description
`Registry.process` validates a webhook using only:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only the raw body:
```
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

`request.shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header and is never included in the signable string:
```
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [3](#0-2) 

Because the HMAC only proves "this body byte-stream was signed by Shopify with the app's shared secret", not "this body belongs to this shop", the gem breaks the equality: `shop authenticated by the HMAC` (none — HMAC binds only bytes) ≠ `shop attributed by Registry.process` (the `shopify-shop-domain` header). An unprivileged Shopify merchant who installs the target app on their own store can legitimately trigger webhook events (e.g. `orders/create`, `app/uninstalled`) and receive a genuinely Shopify-signed payload (valid HMAC computed with the app's real secret, which they never need to know). They can then replay that exact signed body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim merchant's domain. The HMAC still validates (since the body bytes are unchanged), and `Registry.process` forwards `shop: <victim-domain>` to the app's handler, causing the app to process and attribute attacker-controlled event data to a different tenant.

### Impact Explanation
This crosses the tenant boundary the app relies on to key per-shop side effects (e.g. updating shop records, revoking access on `app/uninstalled`, ingesting order/customer data) without requiring the app's `client_secret` or an access token — the attacker only needs their own legitimately-installed instance of the app. Depending on which topics the host app registers handlers for, this can produce data poisoning across shops, false uninstall/reinstall processing for a victim shop, or ingestion of attacker-supplied data associated with another merchant's tenant, which falls under cross-tenant access.

### Likelihood Explanation
Low-to-medium: it requires the attacker to install the target app on their own Shopify store (which is generally allowed for any developer/merchant), capture their own genuine webhook deliveries, and replay them to the app's public webhook endpoint with a modified `shop-domain` header. No secret key, TLS interception, or privileged account is required — only the gem's own `Registry.process` logic, which never binds the shop header to the signed payload.

### Recommendation
Bind the shop identity to the verified payload. Options:
- Reject/annotate webhooks where the delivered `shop` does not match a shop the app has verified/registered an offline session for (requires host-side check, but the gem should at least expose the raw signed bytes plus the header so callers can cross-check).
- Prefer relying on the `webhook_id` returned by Shopify's Admin API registration/lookup rather than trusting the header-derived shop for any state-changing action.
- At minimum, document prominently in `Webhooks::Request`/`Registry.process` that `shop` is not authenticated by the HMAC and must not be trusted as a tenant key without additional verification (e.g., confirming the shop has an active installation/session before acting on the payload).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g., updates an order) causing Shopify to POST a signed webhook to the app's endpoint with headers `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, and a JSON body.
3. Attacker intercepts this outbound delivery to their own endpoint (they fully control the receiving server) and resubmits the identical body and HMAC header to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `@raw_body` only [2](#0-1)  — this still matches since the body/HMAC pair is untouched.
5. `Registry.process` passes `shop: "victim.myshopify.com"` to the app's `handler.handle` [1](#0-0) , causing the host app to process attacker-controlled data as belonging to the victim tenant.

### Citations

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
