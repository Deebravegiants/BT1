This confirms the vulnerability: `WebhookMetadata.shop` is the field the host application uses to attribute webhook data to a tenant (merchant), and it's populated directly from the `shop` header accessor at [1](#0-0) , while the HMAC only ever signs `@raw_body` per `Request#to_signable_string` and `VerifiableQuery`'s contract.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop`-domain HTTP header — which is never part of the signed material — to decide which tenant the payload belongs to.

### Finding Description
The webhook `Request` class implements the `VerifiableQuery` interface. Its `to_signable_string` returns only the raw body: [2](#0-1) 
The `shop` accessor, by contrast, reads directly and unauthenticated from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header: [3](#0-2) 
`Registry.process` validates only the HMAC (which covers the body) and then constructs `WebhookMetadata` using that unauthenticated `shop` header value, handing it to the app's registered handler as the tenant identifier: [4](#0-3) 

This breaks the intended identity binding: `hmac(body, client_secret) == valid` is treated as proof that `shop header == authentic tenant of this body`, but the header is never part of the signable string, so `shop` is fully attacker-controllable independent of the HMAC-verified body.

Because the `client_secret` (and thus the HMAC key) is shared across every shop that installs the app, any merchant who has legitimately installed the app can obtain a body+HMAC pair that is valid for the app's webhook endpoint (e.g., by triggering an event on their own store and capturing the resulting webhook POST, since they control the network path to their own app installation/endpoint or can otherwise replay a delivery). They can then resend that exact `(raw_body, hmac-sha256)` pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed (it only checks the body against the shared secret), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding break: an app built on this gem cannot distinguish "authentic body for shop A" from "same authentic body attributed to shop B" using only the primitives this gem provides (`HmacValidator` + `Request#shop`). Any host application that follows the documented pattern of trusting `WebhookMetadata.shop` (as shown in the gem's own webhook handler interface and tests) to select which tenant's records to create/update/delete is exposed to cross-tenant data injection/corruption — data ostensibly from shop A being processed and stored/attributed as belonging to shop B. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires the attacker to be a merchant who has installed the target app (no elevated privileges, no possession of `api_secret_key` needed) plus the ability to send an arbitrary HTTP request to the app's public webhook endpoint with attacker-chosen headers and a previously-observed valid body/HMAC pair — both are within reach of an ordinary unprivileged internet user interacting with a public app installation.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind the shop identity to the signed body (e.g., derive/validate the shop domain from a per-shop secret or from Shopify's TLS-terminated request metadata rather than a client-supplied header) before constructing `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata.shop` is unauthenticated and must not be trusted for tenant attribution without additional verification (such as confirming the shop has an active, matching offline session/access token on file).

### Proof of Concept
1. App "AppX" is installed on `attacker.myshopify.com` and `victim.myshopify.com`, both sharing the same `client_secret`/`api_secret_key` configured in `ShopifyAPI::Context`.
2. Attacker triggers an event on their own shop (e.g., updates a product), causing Shopify to POST a webhook to AppX's endpoint with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and the JSON body.
3. Attacker captures this exact `raw_body` and `X-Shopify-Hmac-Sha256` value (they receive the delivery to infrastructure/logs they control, or can otherwise observe/replay it).
4. Attacker sends a new HTTP POST to AppX's public webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (the raw body) against the shared secret — this succeeds because the body/HMAC pair is genuinely valid. [4](#0-3) 
6. The registered handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's data>, ...)` and processes/stores the attacker's payload as if it originated from the victim's shop, achieving cross-tenant data injection.

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
