### Title
Webhook `shop` (tenant identifier) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
This is the same bug class as the referenced report: a field that downstream logic treats as an authenticated identity binding is not actually covered by the cryptographic check that is supposed to authenticate the request. In Party Governance, distribution fees applied to the "shares owed" field but not to the ragequit code path that transfers the same value. Here, the gem's webhook handling treats `shop` as the authenticated tenant identifier for a webhook, but the HMAC signature that "authenticates" the webhook is computed over the raw body only — the `shop` header is excluded.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) [2](#0-1) 

The HMAC check calls `to_signable_string` on the `Request` object, which returns only the raw body bytes: [3](#0-2) 

But the `shop` identifier used to route/attribute the webhook to a tenant is read directly, and unauthenticated, from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header: [4](#0-3) 

That header value is passed straight into the handler as the tenant identity for the event, with no verification that it matches whatever shop actually produced the signed body: [5](#0-4) 

The identity binding that should hold is:
`shop-that-produced-HMAC(secret, body) == shop-field-consumed-by-handler`

But the gem only proves `HMAC(secret, body)` is valid for *some* request signed with the app's `api_secret_key`/`old_api_secret_key` — it never binds that proof to the `shop-domain` header. Since a Shopify app's `client_secret` is shared across every shop that installs the app (it is not a per-shop secret), any body+HMAC pair that is valid for one installation of the app is *also* a valid HMAC for the exact same body under a forged `shop-domain` header claiming to be a different shop.

### Impact Explanation
An attacker who installs the target app on their own (unprivileged) shop can generate a legitimate `(raw_body, hmac)` pair by triggering any webhook topic on their own store — this requires no elevated privilege or leaked secret, since it's ordinary use of the app. They can then replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop that also has the app installed. `HmacValidator.validate` will pass (the HMAC only covers `raw_body`), and the gem will hand the handler a `WebhookMetadata` claiming the event came from the victim `shop`. Any app logic keyed off `data.shop` (e.g., writing data, updating settings, triggering side effects "for" that shop) is now attacker-controlled — this is a cross-tenant access primitive matching the "Critical: cross-tenant access" impact bucket.

### Likelihood Explanation
Likely for any app that has more than one active installation and does not perform independent shop authorization: an attacker only needs their own working (non-privileged) installation of the target app to mint a valid `(body, hmac)` pair, then send that pair to the endpoint with an arbitrary `shop-domain` header, since these are two independently-consumed but unlinked fields in `Request`.

### Recommendation
Include the `shop` (and ideally topic/timestamp/webhook id) in the value that is HMAC-verified, or otherwise cryptographically bind the header-derived `shop` to the same request that produced the signature, so that a valid HMAC for one shop cannot be replayed under another shop's identity.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) to capture `raw_body` and its `x-shopify-hmac-sha256` value — both valid under the app's shared `api_secret_key`.
2. Replay a POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189`) calls `Utils::HmacValidator.validate(request)`, which succeeds because `Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) only checks `raw_body`.
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` (`lib/shopify_api/webhooks/request.rb:20-23`, `lib/shopify_api/webhooks/registry.rb:198`), even though the payload never actually originated from that shop.

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
