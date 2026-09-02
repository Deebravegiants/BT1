### Title
Webhook shop identity spoofing — HMAC covers only the raw body, not the `shop-domain` header used to route the webhook - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (and `topic`) values used by the host application to route/attribute the webhook are taken directly from unauthenticated HTTP headers. This breaks the equality that should hold between "the shop the HMAC authenticates" and "the shop the application acts on," analogous to the reward-accounting mismatch in the external report where the quantity used for payout (`YT`) diverged from the quantity actually authenticated (`SY`).

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` verifies the HMAC strictly against `to_signable_string`, i.e., only the raw bytes of the body: [2](#0-1) 

But `Request#shop` and `Request#topic` — the values a host application uses to decide *which merchant* and *which handler* the webhook belongs to — are read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in the signed bytes: [3](#0-2) 

The identity binding that should hold is:
`shop_authenticated_by_hmac == shop_the_app_attributes_the_payload_to`

Here that equality does not hold: the HMAC only proves "this body byte-sequence was produced with our `client_secret`," it proves nothing about which shop header accompanies it. An attacker who can capture or replay one legitimately-signed webhook body (e.g., from their own installed/test shop, which they legitimately receive) can resend it with a forged `shopify-shop-domain` header pointing at a different tenant. Since `HmacValidator.validate` only checks the raw body bytes and never binds the header to the signature, the request still validates successfully, but `Request#shop` now returns an attacker-controlled value.

### Impact Explanation
This allows cross-tenant data injection into a host application's webhook processing pipeline: a request carrying a validly-signed payload can be attributed to an arbitrary shop domain chosen by the attacker, letting them inject "shop B" against the merchant/tenant record of "shop A" (or of an unrelated shop the attacker doesn't own), or trigger tenant-scoped business logic under a spoofed shop identity. This matches the "cross-tenant access" criterion for Critical severity, since the shop attribution — the tenant boundary — is not actually protected by the cryptographic check the library performs.

### Likelihood Explanation
Exploitation requires the attacker to already possess one validly-HMAC-signed webhook payload (trivial to obtain by installing the app on their own development/test shop and capturing the resulting webhook delivery), after which they can replay it to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header. No access to `client_secret`, tokens, or Shopify infrastructure is needed — only network access to the app's public webhook endpoint. This does not require ignoring a documented API; `Request#shop` is the library's own documented accessor and is expected to be trustworthy once `hmac`/`validate` succeeds.

### Recommendation
Include `shop` (and ideally `topic`) in the HMAC-signable string, or otherwise cryptographically bind the header values to the body before exposing `Request#shop`/`Request#topic` as trusted values, so that `HmacValidator.validate` cannot succeed unless the shop-domain header matches what was actually signed.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimately Shopify-signed webhook, capturing `raw_body` and the valid `hmac-sha256` header.
2. Attacker POSTs the same `raw_body` and `hmac-sha256` header to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. The host application, trusting `request.shop`, processes/records the payload against `victim-shop.myshopify.com` even though the attacker controls the shop-domain claim.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
