### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook impersonation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string from only the raw request body, while the `shop` (tenant identifier) is read from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header, which is never included in that signable string. `Registry.process` validates the HMAC over the body only and then unconditionally trusts the unauthenticated `shop` header value to build the `WebhookMetadata` passed to the app's handler. This breaks the identity binding: `hmac_valid(raw_body)` ≠ `hmac_valid(raw_body, shop)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from an HTTP header that is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC strictly against `to_signable_string` (i.e., the raw body) using the app's shared `client_secret`: [3](#0-2) 

`Registry.process` performs the HMAC check and then immediately trusts `request.shop` (the unauthenticated header) to construct `WebhookMetadata`, which is handed to the app's webhook handler as the authoritative tenant identifier: [4](#0-3) 

Because a single `client_secret` is shared by the app across *all* installed shops, any merchant who has installed the app can receive a genuinely Shopify-signed webhook for their own store (valid HMAC over that raw body, since HMAC = HMAC(secret, raw_body) with no shop binding). That same attacker can then replay the identical raw body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` invokes the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain, even though the signed payload never vouched for that shop.

The stated identity binding that should hold is:
`hmac_over(raw_body) authenticates (raw_body, shop)` — but in the code it only authenticates `raw_body`, so `shop` can be substituted freely by anyone who can produce (or capture) any validly-signed body for the app.

### Impact Explanation
This is a cross-tenant confusion vulnerability: an attacker who is a legitimate (even low-privilege) merchant/installer of the target app can cause the app to process webhook events "as if" they originated from a different, victim shop. Depending on how the host app's `WebhookHandler` uses `WebhookMetadata#shop` (e.g., to look up the victim's session/access token, update the victim's data, or trigger `shop/redact`/`customers/redact` compliance flows for the wrong tenant), this can lead to cross-tenant data corruption or disclosure. This satisfies the "cross-tenant access" criterion in the reward rules, since the `shop` value is used as the tenant/session key downstream without being bound to the cryptographic proof of authenticity.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one genuinely-signed webhook body/HMAC pair for the same app (trivially available to any merchant who installs the app on their own store and receives real webhook traffic, or via any topic whose body content is attacker-influenceable/predictable). No access to `client_secret`, access tokens, or privileged accounts is needed — only the ability to send an HTTP request with attacker-controlled headers alongside a previously-observed valid `(raw_body, hmac)` pair, which is fully within reach of an "unprivileged" but app-installing internet user.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) values in the HMAC-signable string, or otherwise cryptographically bind the header-derived `shop` to the payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that host applications cannot rely on `request.shop` as an authenticated tenant identifier unless it is verified against Shopify's out-of-band webhook registration records (e.g., cross-checking against the shop associated with the currently stored session for that webhook subscription).

### Proof of Concept
1. App merchant A installs the target Shopify app; Shopify sends a legitimate webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`, and `X-Shopify-Shop-Domain: shopA.myshopify.com`.
2. Attacker (merchant A, or anyone who can observe/capture this request) resends the same body `B` and same `H` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shopB.myshopify.com` (victim shop).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which recomputes `HMAC-SHA256(client_secret, B)` and compares it to `H` — this still matches because the shop header plays no role in signature computation (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` then builds `WebhookMetadata.new(... shop: request.shop ...)` using the attacker-controlled `shopB.myshopify.com` value and invokes the handler as if the event genuinely originated from shop B (`lib/shopify_api/webhooks/registry.rb:198-199`).

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
