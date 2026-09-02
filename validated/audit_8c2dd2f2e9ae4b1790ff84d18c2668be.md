### Title
Webhook shop identity (`X-Shopify-Shop-Domain`) is not covered by the HMAC signature, allowing cross-tenant spoofing of the trusted shop - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the app's webhook handler from the `X-Shopify-Shop-Domain` header, while the HMAC signature that `HmacValidator` checks only covers the raw request body. The `shop` field is therefore acted upon by the host application (as the tenant key) without being bound by the cryptographic check that is supposed to authenticate the request.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhook requests `to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` attribute, however, is read straight from the `shop-domain` header, which is never included in the signed string: [2](#0-1) 

`Registry.process` validates the HMAC over the body and then forwards `request.shop` — the unauthenticated header value — as the tenant identity to the app's handler: [3](#0-2) 

The equality that should hold is: `shop bound by HMAC == shop acted upon by handler`. In this gem it is instead: `shop verified by HMAC (∅, not present in signable string) ≠ shop used to route/act on data (shop-domain header)`. Any attacker who can obtain one genuine `(raw_body, hmac)` pair from Shopify — trivially available to anyone who installs the app on their own store and lets Shopify deliver a real webhook to the app's public endpoint — can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header value naming a victim shop. `HmacValidator.validate` will still succeed because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is meant to enforce for webhook delivery: the `shop` value that host applications commonly use to look up sessions/access tokens or to record cross-tenant events (e.g. `shop/redact`, `customers/redact`, `orders/paid`, app-uninstalled) is attacker-controlled despite HMAC validation succeeding. Depending on how the host app uses `WebhookMetadata#shop` (a very common pattern demonstrated in the gem's own webhook usage docs), this enables cross-tenant data corruption/confusion — e.g. triggering another merchant's uninstall/redact logic, or associating attacker-supplied payload data with a victim shop record. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires the attacker to have legitimately received one valid webhook for their own shop (any merchant installing the app can do this — no privileged credentials, no access to `client_secret`, and no compromise of Shopify's systems needed), then replay the identical body/signature with a forged shop-domain header at the app's public webhook endpoint. This is a realistic, low-effort attack path reachable from an unprivileged, external attacker.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values in the signed material checked against the HMAC, or otherwise cryptographically bind the shop domain to the payload before trusting it (e.g., require the host application to cross-check `request.shop` against the shop associated with the currently active/stored session before acting on the webhook, and document this requirement prominently). At minimum, `Request#to_signable_string` should not silently omit identity fields the gem itself surfaces as trusted (`shop`, `topic`, `webhook_id`) to `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own development store `attacker.myshopify.com` and triggers any webhook topic the app subscribes to (e.g. `orders/create`). Shopify delivers a real request to the app's public webhook endpoint with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's `client_secret`.
2. Attacker captures this `(raw_body, hmac_header)` pair.
3. Attacker replays the exact same `raw_body` and `hmac_header` to the same endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the signature only covers `raw_body` (unchanged): [4](#0-3) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the body/HMAC only ever proved authenticity for `attacker.myshopify.com`'s webhook, allowing the host app to act on victim-shop data/state using attacker-supplied payload content.

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
