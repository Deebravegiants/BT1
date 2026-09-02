Based on my investigation of the webhook verification code, I found a genuine identity-binding gap that matches the reported bug class (a value trusted for a security decision while not being covered by the cryptographic check that "validates" the request).

### Title
Webhook `shop-domain` Header Not Covered by HMAC Verification Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes and exposes an HMAC-verified status for an incoming webhook, but the HMAC signature only covers the raw request body — not the `shop-domain` header that the library (and downstream host apps relying on `request.shop`) treat as the authenticated tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Utils::HmacValidator.validate` computes/compares the HMAC strictly over that signable string: [1](#0-0) [2](#0-1) 

Meanwhile `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header with no cryptographic binding to the HMAC at all: [3](#0-2) 

`Webhooks::Registry.process` calls `HmacValidator.validate` against the `Request` object and, once that succeeds, dispatches to the registered handler using `request.topic` and `request.shop`, implicitly treating the whole `Request` — including `shop` — as "verified" once the HMAC check passes. Since the equality actually being checked is `hmac(raw_body) == signature`, not `hmac(raw_body ‖ shop) == signature`, the `shop` field is an "acted-on but not covered" value exactly analogous to the report's pattern (a value used for a critical calculation/decision that is not bound by the same authentication check that is presumed to cover it).

### Impact Explanation
Because the `shop` header is unauthenticated relative to the HMAC, a party who has ever received one legitimate webhook delivery for their own store (i.e., any merchant who has installed the app) can replay that exact `body` + `hmac` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value (e.g., a victim's shop domain). `HmacValidator.validate` still passes because the body is unchanged, but the host app's webhook handler — built on the assumption that a passing `ShopifyAPI::Webhooks::Registry.process` call yields a trustworthy `request.shop` — will process the payload as if it originated from the victim tenant. Depending on the handler's logic (e.g., updating shop settings, uninstall/GDPR handling, order/customer data association), this enables cross-tenant data corruption or disclosure, satisfying the Critical "cross-tenant access" impact bar.

### Likelihood Explanation
The attacker only needs to be a legitimate (even free/trial) merchant who has installed the target app to obtain one valid `(body, hmac)` pair from their own store's webhook traffic — no access to the app's `client_secret`, access tokens, or any other privileged credential is required. Replaying it with a modified header is a trivial HTTP-level operation, and it directly exploits the gem's own `Request`/`HmacValidator`/`Registry` code rather than requiring the host application to violate documented usage.

### Recommendation
Bind the `shop` (and ideally `topic`) values into the signed material checked by `HmacValidator`, or otherwise clearly document that `request.shop`/`request.topic` are NOT authenticated by the HMAC and must be independently correlated against the session/shop the webhook was registered for (e.g., cross-check `request.shop` against the shop that owns the `webhook_id`, obtained via a signed/authenticated channel) before trusting it for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook delivery (e.g., `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header value.
2. Attacker resends an HTTP POST to the app's webhook endpoint with:
   - the identical captured `raw_body`
   - the identical `hmac-sha256` header
   - `shopify-shop-domain` header rewritten to `victim.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate`, which succeeds because it only checks `hmac(raw_body)`. [1](#0-0) 
4. The registered handler receives `request.shop == "victim.myshopify.com"` and `request.parsed_body` from the attacker's own store, and performs its tenant-scoped action against the victim's data.

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
