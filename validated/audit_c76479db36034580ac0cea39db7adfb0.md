### Title
`Webhooks::Request#shop` (tenant identifier) is not covered by the webhook HMAC signature, enabling cross-shop identity spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`, but the signable string used for that HMAC is only the raw JSON body [1](#0-0) . The `shop` value that is subsequently handed to the app's handler as the trusted tenant identifier is read straight from the unauthenticated `X-Shopify-Shop-Domain`/`shopify-shop-domain` header [2](#0-1) , which is never part of the HMAC-covered bytes. The binding the gem should provide but does not is: `hmac == HMAC(secret, body ‖ shop)`; instead it only guarantees `hmac == HMAC(secret, body)`, i.e. bytes verified ≠ bytes (fields) trusted/acted upon.

### Finding Description
`Registry.process` does: verify HMAC over the request, then build `WebhookMetadata` using `request.shop` and hand it to the registered handler as the shop the event pertains to [3](#0-2) . Because `to_signable_string` for `Webhooks::Request` returns only `@raw_body` [1](#0-0) , the `shop-domain` header is fully outside of the cryptographic guarantee. Since all shops installing the same app share one `client_secret`, a valid `(body, hmac)` pair captured from a legitimate webhook delivered for one shop (e.g. the attacker's own installed dev/test store) remains a valid HMAC for that exact body regardless of which `X-Shopify-Shop-Domain` header accompanies it. An attacker who controls a shop installed on the target app can capture one authentic webhook (body + hmac) from their own store, then replay that same body/hmac pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `HmacValidator.validate` will report success because it only checks the body bytes, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain.

This directly matches the report's underlying bug class: "a field acted on but not covered by the HMAC" — here the acted-upon field is the tenant identity (`shop`), and it is disjoint from the HMAC-covered field (`body`).

The gem's own documentation compounds the risk by asserting the check fully authenticates the request's origin: `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [4](#0-3) , and instructs consuming apps to trust `data.shop` as "The shop domain of the webhook" [5](#0-4)  without any caveat that this field is unauthenticated relative to the HMAC.

### Impact Explanation
This is a cross-tenant identity confusion vector: an app built strictly per this gem's documented API can be made to process a webhook body under the wrong shop's identity. Depending on what the handler does with `data.shop` (e.g., look up that shop's stored session/access token to process/react to the payload, or write data keyed by shop), this can lead the app to act with one merchant's stored credentials/session on behalf of an attacker-chosen "shop" label, or to inject/associate attacker-controlled payload data into a victim tenant's records — a cross-tenant access outcome purely through this gem's own verification API and documented contract.

### Likelihood Explanation
Requires the attacker to control at least one shop that has installed the same app (a normal, low-privilege position: any merchant can install a public/dev app and capture its own legitimate webhook traffic), plus the ability to POST to the app's public webhook endpoint with a forged header — both are within reach of an unprivileged, unauthenticated-to-other-tenants attacker. No access to `api_secret_key`, another shop's access token, or the app owner's credentials is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signable string, or otherwise require the caller to separately verify `request.shop` against a known/installed shop list before trusting it, and correct the documentation in `docs/usage/webhooks.md` to state precisely that only the body is authenticated by `hmac-sha256`, not the shop-domain header, so host apps do not conflate "HMAC passed" with "shop is verified."

### Proof of Concept
1. App installs on Shop A and Shop B (attacker controls Shop A).
2. Shopify sends a legitimate webhook to the app for Shop A: body `B`, header `X-Shopify-Shop-Domain: shop-a.myshopify.com`, header `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)`.
3. Attacker (as Shop A owner) intercepts/records `(B, H)` from their own delivered webhook (e.g., via a proxy they control on their own server, or logs).
4. Attacker POSTs to the app's webhook endpoint with the same body `B` and same header `H`, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com` (a victim shop they do not control).
5. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` — matches `H` — validation passes, per `lib/shopify_api/utils/hmac_validator.rb` lines 26-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38 (signable string = body only).
6. `Registry.process` invokes the app handler with `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: <attacker-controlled B>, ...)`, per `lib/shopify_api/webhooks/registry.rb` lines 198-199 — the app now believes attacker-supplied data belongs to Shop B.

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

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
