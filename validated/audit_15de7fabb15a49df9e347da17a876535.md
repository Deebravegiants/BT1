### Title
Webhook shop-domain identity is not bound to the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC over the raw request body only. The `shop` value that is handed to the app's webhook handler (and used by host applications to attribute the webhook payload to a tenant) comes from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is **not** covered by that HMAC. This breaks the equality the library is supposed to guarantee: `HMAC-authenticated payload == shop it is attributed to`.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` verifies authenticity with: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — the shop domain is deliberately excluded from the signed material: [3](#0-2) 

`shop` itself is read straight from an HTTP header that is not part of the signed payload: [4](#0-3) 

That unauthenticated `shop` value is then propagated verbatim into the data given to the app's handler: [5](#0-4) 

Because Shopify signs webhook bodies for *all* installed shops of an app with the **same** shared `client_secret` (not a per-shop key), any user who can install the app on their own shop can trigger a webhook, capture a valid `(raw_body, hmac)` pair from their own store, and then POST that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g., a victim shop's domain). `Registry.process` will accept it as valid, because the signature check never touches the shop field, and will invoke the handler with `data.shop` equal to whatever domain the attacker supplied. This is the same class of bug as the reported `AccountTag` collision: a value used to distinguish "which tenant/type this belongs to" is not covered by the mechanism meant to bind it to the authenticated payload, so the library will happily let one identity be mistaken for another.

### Impact Explanation
Host applications are documented to trust `data.shop` directly to key their tenant-scoped processing (per the gem's own docs example: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [6](#0-5) 

An attacker who has (legitimately) installed the app on their own shop can forge the shop attribution of an otherwise-valid webhook payload to point at a different merchant's shop domain. Depending on how the host app uses this value (e.g., to look up which tenant's session/access token to act on, or to write incoming data against a tenant record keyed by `shop`), this enables cross-tenant data confusion/write — data belonging to the attacker's own store can be injected and processed as if it belonged to a victim shop. This matches the Critical "cross-tenant access" impact category, since the library provides no way for a host app relying on the built-in verification path to detect the mismatch.

### Likelihood Explanation
Exploitation only requires the ability to install the target app on an attacker-controlled shop (a low bar — any merchant/developer can install a public app) and the ability to send a raw HTTP POST to the app's public webhook callback endpoint with attacker-chosen headers. No access to the app's `client_secret`, access tokens, or any privileged account is required — the attacker uses a validly-signed webhook they legitimately received for their own store and merely changes an unauthenticated header before replaying it.

### Recommendation
Bind the shop identity into the HMAC-protected material, or otherwise ensure the shop value handed to `WebhookMetadata`/handlers is derived from a source Shopify actually signs, rather than a freely-modifiable HTTP header. At minimum, document/enforce that `Registry.process` should also verify the `shop-domain` header is consistent with a value obtained from an authenticated channel (e.g., cross-check against the registered session before dispatching to the handler), analogous to how disjoint enum ranges were used to fix the `AccountTag` collision in the referenced patch — here, an explicit binding field (shop inside the signed payload) is what's missing.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`). Shopify sends a legitimately HMAC-signed request:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC over raw_body, signed with the app's shared client_secret>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   <raw_body>
   ```
2. Attacker captures the exact `raw_body` and `x-shopify-hmac-sha256` value.
3. Attacker replays the identical `raw_body` and `x-shopify-hmac-sha256` to the same endpoint, but sets:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only (see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`) — it matches, since the shop header was never part of the signed data.
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker's own order data>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

Note: I was unable to locate/verify the `WebhookMetadata` class file contents directly (search returned "file not found"), so its exact field list is inferred from `lib/shopify_api/webhooks/registry.rb` usage and `docs/usage/webhooks.md`; the docs confirm `shop` is a documented, trusted field passed to handlers.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
