## Analysis

The reported class of bug is: a security-critical field is *acted upon* by the code but is **not included in the cryptographic binding** (HMAC) that is supposed to authenticate the request. In OptimismPortal this was the withdrawal target field; in this Ruby gem the same pattern exists in the **webhook processing pipeline**.

### Root cause

`ShopifyAPI::Webhooks::Request` computes the signable content only from the raw HTTP body: [1](#0-0) 

But the `shop` (tenant identity) used downstream is read straight from an **unauthenticated HTTP header**, which is never part of the HMAC input: [2](#0-1) 

`Registry.process` validates only the body HMAC and then dispatches the handler using this unauthenticated `shop` value as the tenant identifier: [3](#0-2) 

### The broken binding (equality that should hold but doesn't)

`HMAC-verified(raw_body)` ⇏ `shop header used for tenant routing == shop that produced raw_body`

The HMAC only proves the *body bytes* were signed with the app's `api_secret_key` (i.e., "this came from Shopify, for this app"). It proves nothing about which shop/tenant the header claims to represent. Since `api_secret_key` is shared across every shop installation of the same app, a valid `(raw_body, hmac)` pair captured from one shop's webhook delivery remains a valid `(raw_body, hmac)` pair when replayed with a **different** `x-shopify-shop-domain` / `shopify-shop-domain` header — `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb#L26-L31` will still pass because it only recomputes over `to_signable_string`, which is just `@raw_body`.

### Why this matters (cross-tenant impact)

Any actor able to submit an HTTP POST to the app's public webhook endpoint (which by design must be reachable from the internet, since Shopify calls it unauthenticated aside from the HMAC) and who obtains one legitimately-signed `(body, hmac)` pair — via logging systems, webhook forwarding/proxy tooling, error trackers, browser devtools on a merchant's own store, or any other capture — can replay that exact pair while substituting an arbitrary `shop-domain` header value. `Registry.process` and the resulting `WebhookMetadata.shop` will attribute that (unmodified, correctly-signed) payload to the attacker-chosen shop, since nothing in the gem cross-checks the header against the signed body content. Multi-tenant apps that key data storage, feature entitlements, or business logic off `WebhookMetadata#shop` would process/attribute another merchant's event data under a different tenant, i.e., a cross-tenant identity confusion — directly analogous to the OptimismPortal report's core theme of a permissioned/binding check that's missing on a field that materially changes who/what an action applies to.

### Recommendation

Do not trust the `shop`, `topic`, `webhook_id`, or `api_version` headers as tenant/routing identity unless they are cryptographically bound to the signed payload. At minimum, `Registry.process` (or the consuming application) should cross-validate the header-derived `shop` against the shop context established by the specific webhook subscription/endpoint that received the callback (e.g., per-shop endpoint or a shop id embedded in and covered by the signed body), rather than trusting the header value in isolation.

---

### Title
Webhook `shop` identity is read from an unauthenticated header while only the body is HMAC-covered, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body, while `#shop` (and `#topic`, `#webhook_id`) is read from an HTTP header that is never part of the HMAC input. Since the same `api_secret_key` is used to sign webhooks across all shops that install an app, a captured legitimate `(raw_body, hmac)` pair can be replayed with a forged `shop-domain` header to misattribute event data to a different tenant.

### Finding Description
`Request#hmac` and `Request#to_signable_string` derive the HMAC input exclusively from `@raw_body` (`lib/shopify_api/webhooks/request.rb#L35-L38`), while `Request#shop` reads `shopify-shop-domain`/`x-shopify-shop-domain` directly from request headers with no cryptographic tie to the signed content (`lib/shopify_api/webhooks/request.rb#L20-L23`). `Webhooks::Registry.process` validates only the HMAC via `Utils::HmacValidator.validate(request)` and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` (`lib/shopify_api/webhooks/registry.rb#L188-L199`). `HmacValidator.validate_signature` recomputes the signature purely from `verifiable_query.to_signable_string`, i.e., the body (`lib/shopify_api/utils/hmac_validator.rb#L26-L31`).

### Impact Explanation
This breaks the intended identity binding `HMAC-authenticated payload == payload attributable to the shop header`. Because `api_secret_key` is shared across all installs of the same app, any valid `(body, hmac)` pair obtained for one shop remains valid when resubmitted with a different shop header, causing the app to process/store that webhook's data under the wrong tenant — a cross-tenant data confusion condition.

### Likelihood Explanation
Exploitation requires the attacker to obtain one legitimately-signed webhook body/HMAC pair (e.g., via logging, proxies, error trackers, or any incidental leakage) and the ability to POST to the app's public webhook endpoint, which normally has no other authentication besides this HMAC.

### Recommendation
Bind the routing identity to the signed content: derive/verify `shop` from data embedded within the signed body (or from a per-shop unique callback path/secret) rather than trusting `shop-domain` headers outright, and have `Registry.process` reject the request if header-derived identity cannot be corroborated by the signed payload.

### Proof of Concept
1. Attacker captures a legitimately-Shopify-signed webhook delivery for `shop-a.myshopify.com` (raw JSON body `B` and header `x-shopify-hmac-sha256: H`), e.g., via a logging/proxy leak.
2. Attacker POSTs the same body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` (`lib/shopify_api/utils/hmac_validator.rb#L26-L31`); `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(... shop: "shop-b.myshopify.com", body: B ...)` (`lib/shopify_api/webhooks/registry.rb#L198-L199`), attributing shop A's event data to shop B.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
