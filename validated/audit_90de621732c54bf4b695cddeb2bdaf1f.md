Found a concrete analog matching the requested bug class ("a field acted on but not covered by the HMAC").

### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) that is handed to the app's webhook handler from an HTTP header, while the HMAC signature that `HmacValidator` checks covers only the raw request body. The `shop` value is never bound into the signed material, so any bytes that carry a valid HMAC for *some* shop's webhook body can be replayed with a forged `shop-domain` header claiming to belong to a *different* shop, and the gem will accept it as authentic.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Webhooks::Request#shop` is read straight from an unauthenticated header (`x-shopify-shop-domain` / `shopify-shop-domain`), with no cryptographic tie to the body that was actually signed: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the signature over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Webhooks::Registry.process` uses this same, HMAC-unbound `shop` value to construct the `WebhookMetadata` that is dispatched to the app's registered handler as the tenant identity for the event: [4](#0-3) 

The identity binding that should hold is: `shop authenticated by HMAC == shop used to scope the webhook event`. Because `shop` is excluded from `to_signable_string`, this equality is never enforced — the gem authenticates only the body bytes, then attributes those authenticated bytes to whatever `shop-domain` header the caller supplied.

### Impact Explanation
An unprivileged internet user who controls (or is) any single legitimate Shopify shop can register a webhook to their own endpoint and capture a genuine `(raw_body, hmac)` pair signed with the app's `client_secret`-derived shared knowledge (they don't need the secret — Shopify signs it for them for their own shop's events). They can then replay that exact `(raw_body, hmac)` pair to the app's shared webhook endpoint while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` will invoke the handler believing the event legitimately originates from the victim shop. Any app logic that trusts `WebhookMetadata#shop` to select which tenant's access token, session, or database row to act on can be tricked into applying attacker-controlled webhook content to a different merchant's tenant context — a cross-tenant confusion/spoofing primitive.

### Likelihood Explanation
Exploitation requires only: (1) being any legitimate merchant able to trigger webhooks for their own store (an unprivileged, ordinary Shopify merchant — no leaked secrets, no privileged account), and (2) the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a modified header. Both are trivially available to an "unprivileged internet user" as defined by the scope rules, making this a realistic, low-effort path.

### Recommendation
Bind the shop identity into the signed material used by `Webhooks::Request#to_signable_string`, or otherwise cryptographically verify that the `shop-domain` header matches the shop encoded in/derivable from the authenticated payload/registration before dispatching to handlers, so that `HmacValidator.validate` cannot be satisfied for a `(body, shop)` pair that Shopify never actually signed together.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` and registers a webhook (e.g., `orders/create`) pointing at the target app's shared webhook endpoint.
2. Attacker triggers the event on their own store; Shopify sends a request with headers `x-shopify-hmac-sha256: <valid hmac over raw body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and the JSON body.
3. Attacker replays this exact body and HMAC header to the same endpoint but rewrites `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against `hmac`: [5](#0-4) 
5. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)` and the host app processes attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
