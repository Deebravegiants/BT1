## Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) for an incoming webhook from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that authenticates the webhook is computed **only over the raw request body**. The shop domain is never part of the signed payload, so the binding `hmac_authenticates(shop)` does not hold: the HMAC only authenticates `body`, not `(body, shop)`.

### Finding Description
`Request#to_signable_string` returns solely the raw body: [1](#0-0) [1](#0-0) 

`Request#shop` is read straight from a header that is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then hands the header-derived `shop` value straight to the app's handler as the authenticated tenant identifier: [3](#0-2) 

`Utils::HmacValidator.validate` confirms only that the signature matches `verifiable_query.to_signable_string` (the body) with `Context.api_secret_key`: [4](#0-3) 

Since `api_secret_key` is a single, app-wide secret shared across **every shop** that installs the app (not a per-shop secret), any merchant who has installed the app can obtain a body + HMAC pair that is valid for the app's secret (either from a genuine webhook Shopify sent to their own shop, or by locally computing `HMAC-SHA256(body, api_secret_key)` once they have observed one valid signed webhook — Shopify's algorithm and secret are otherwise identical for all tenants of the same app). That attacker can then replay the exact same `(body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `HmacValidator.validate` still succeeds because it checks the body/HMAC pair only, and `Registry.process` will invoke the app's handler with `WebhookMetadata#shop` set to the victim's domain, `topic`, and the attacker-supplied `body`. This breaks the identity binding `verified_signature == (shop, body)` down to `verified_signature == body`, allowing cross-tenant impersonation of webhook events.

### Impact Explanation
This lets an attacker who controls their own (or any) app installation forge webhook events that the host application will process as if they originated from a completely different, victim shop — i.e., cross-tenant access/spoofing of trusted webhook data. Depending on how the host app's webhook handlers consume `WebhookMetadata#shop` (e.g., to look up/update a merchant's session, orders, or settings), this can result in cross-tenant data corruption or unauthorized actions attributed to another merchant's shop, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be an app installer on any shop (a normal, unprivileged use of the app — no access token, no `client_secret`, and no compromise of the victim is needed) and the ability to send an HTTP POST to the app's public webhook endpoint with a modified header. This is realistically achievable by any merchant who installs the app being targeted.

### Recommendation
Bind the shop identity into the authenticated material. Either:
- Include the shop domain in `to_signable_string` (if verifying per-shop secrets is not feasible, at minimum cross-check the header's shop domain against an expected/allow-listed value tied to the session the webhook claims to originate from), or
- Look up the receiving shop's own webhook secret (Shopify supports per-topic/per-shop verification patterns) rather than trusting the `X-Shopify-Shop-Domain` header as an authenticated value, and never treat it as verified merely because the body's HMAC matches the app-wide secret.

### Proof of Concept
1. App merchant "attacker.myshopify.com" installs the vulnerable app and receives a genuine webhook: body `B`, header `X-Shopify-Hmac-Sha256: H = HMAC-SHA256(api_secret_key, B)`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends a POST to the app's webhook endpoint with the same body `B` and same `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and matches `H` — validation passes (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
