### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant data injection - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `X-Shopify-Shop-Domain` header to determine which tenant the payload belongs to. Because the shop identity is never part of the signed content, a party who possesses one validly-signed webhook (body + HMAC) — trivially obtainable by installing the app on their own store — can replay that same body/HMAC pair while substituting an arbitrary victim shop's domain in the header, and the gem will accept it as an authentic webhook for the victim shop.

### Finding Description
`Registry.process` performs authentication like this: [1](#0-0) 

The HMAC check calls `Utils::HmacValidator.validate(request)`, which in turn calls `request.to_signable_string` to build the bytes that are HMAC'd: [2](#0-1) 

`to_signable_string` returns only `@raw_body` — the shop domain is excluded from the signed material. Yet immediately after the HMAC check passes, `request.shop` (read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header with no cross-check against the signed body) is used as the tenant identifier passed to the handler: [3](#0-2) [4](#0-3) 

The binding that should hold is: `shop attribution used by the handler == shop covered by the HMAC-verified bytes`. Because the header is outside `to_signable_string`, this equality does not hold — `HMAC(secret, raw_body)` is valid for *any* value of the `shop-domain` header, since it plays no role in the digest computation. Critically, the HMAC secret (`Context.api_secret_key`) is the app's single shared client secret, common across *all* shops that have installed the app — it is not shop-specific. Therefore any unprivileged party who installs the app on their own store will legitimately receive webhooks whose body+HMAC pair is valid under this same shared secret. They can capture that pair and POST it directly to the app's public webhook endpoint with a forged `shop-domain` header naming any other merchant, and `Registry.process` will accept it, invoke the handler, and hand it fabricated `WebhookMetadata` claiming it came from the victim shop.

### Impact Explanation
This breaks per-tenant isolation: a malicious app-installing shop can inject attacker-chosen webhook payloads (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`, etc.) that the host application will process as if they originated from a different, victim merchant's store. Depending on how the host app's webhook handlers use `WebhookMetadata#shop` (e.g., to key data writes, trigger session/token revocation flows, or fulfill compliance webhooks), this enables cross-tenant data corruption or spoofed lifecycle events attributed to a shop the attacker does not control — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
High. The prerequisite — installing the target app on a shop the attacker controls — is normal, unprivileged use of any public Shopify app; no credentials, tokens, or privileged access are required. Capturing one genuine webhook delivery (body + `x-shopify-hmac-sha256`) is trivial by simply triggering the relevant Shopify event in the attacker's own store, and replaying it with a different `shop-domain` header against the app's public webhook endpoint requires no special tooling.

### Recommendation
Bind the shop identity to the authenticated content instead of trusting an unauthenticated header:
- Include the shop domain in the bytes that are HMAC-verified (Shopify does not natively sign the shop header, so the app must independently validate that the header's shop matches a shop the app expects to receive this specific event for — e.g., cross-check `request.shop` against the shop associated with the specific webhook subscription/registration record if that's tracked, or otherwise avoid relying on the header alone for authorization decisions).
- At minimum, treat `request.shop` as untrusted input for security-sensitive decisions and require handlers to independently verify shop legitimacy (e.g., confirm the shop has an active session/install record) before acting on the payload, rather than assuming HMAC validity implies the shop header is authentic.

### Proof of Concept
1. Attacker installs the target Shopify app on their own development/test store (`attacker-shop.myshopify.com`), which is a normal, unprivileged action any Shopify user can take.
2. Attacker triggers a webhook event (e.g. creates an order) in their own store, and captures the raw POST body and the `x-shopify-hmac-sha256` header sent by Shopify to the app's webhook endpoint. This HMAC is valid because it is computed with the app's single shared `client_secret`, not a per-shop secret.
3. Attacker replays the exact same body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but overwrites the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, raw_body)` — unaffected by the header change: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, where `shop` is `"victim-shop.myshopify.com"` — the host application processes attacker-controlled data as if it belongs to the victim shop. [4](#0-3)

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
