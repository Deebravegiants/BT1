Found the vulnerability. In `Webhooks::Request`, the `shop` field used to identify the tenant is read directly from the `X-Shopify-Shop-Domain` HTTP header, but that header is **not** included in the HMAC-signed payload — the HMAC in this class is computed over `@raw_body` only.

### Title
Webhook tenant identification bypass via unauthenticated `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (tenant identity) from the `shopify-shop-domain` HTTP header, while HMAC validation only covers the raw request body.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` [1](#0-0) , and `hmac` is computed from the `hmac-sha256` header value [2](#0-1) . `Utils::HmacValidator.validate` compares `OpenSSL::HMAC.hexdigest(secret, to_signable_string)` against the received `hmac`, i.e. it only proves that the body bytes were signed by Shopify with the app's `client_secret` [3](#0-2) . The `shop` attribute, however, is read straight from the `shopify-shop-domain` HTTP header without any cryptographic binding to the signed body: `T.cast(shopify_header("shop-domain"), String)` [4](#0-3) . The identity equality that should hold is: `shop-domain header == shop encoded inside the HMAC-covered bytes`, but the header is fully attacker-controllable and outside the signed material.

### Impact Explanation
An unprivileged attacker who can reach the app's webhook endpoint (webhook endpoints are typically public HTTP endpoints) can replay or forge an HTTP request carrying a body/HMAC pair captured from Shop A's legitimate webhook (or any request whose HMAC they can obtain, e.g. from a webhook they registered for their own trial/dev shop with the same app if the app is a public app with a shared `client_secret`), but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`. Because `shop` is never verified against the signed bytes, the host application (which typically keys session/data lookups off `request.shop`) will process the payload as if it originated from `victim-shop.myshopify.com`, resulting in cross-tenant data confusion — writes, side effects, or triggered business logic scoped to the wrong merchant. This matches the Critical "cross-tenant access" impact category since the `shop` identity used for tenant-scoped operations is not authenticated.

### Likelihood Explanation
Any app built with this gem that trusts `Webhooks::Request#shop` for tenant routing after `HmacValidator.validate` returns `true` is affected, and this is the gem's documented usage pattern for webhook processing (validate HMAC, then read `.shop`/`.topic`/`.parsed_body`). No documented API misuse is required — the gem's own class exposes `shop` this way. The main precondition is the attacker obtaining a validly-signed body+hmac pair for *some* shop under the same app (e.g., from their own dev/trial store, or via a leaked/publicly visible webhook payload), which is realistic for public multi-tenant Shopify apps.

### Recommendation
Include the shop domain (and topic/api-version) inside the HMAC-covered signable string, or otherwise cryptographically bind the `shop-domain` header value to the signed payload (e.g., verify it against a `shop` field embedded in the JSON body, or require it be part of the canonical string HMAC'd by Shopify). At minimum, document prominently that `shop` is unauthenticated and must never be used for tenant lookups without additional verification.

### Proof of Concept
1. Attacker registers/receives a legitimate webhook for their own shop `attacker-shop.myshopify.com`, capturing `raw_body` and the correct `X-Shopify-Hmac-Sha256` header (valid because it's HMAC'd with the shared `client_secret` for the app, not shop-specific).
2. Attacker replays this exact `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a `Request` whose `hmac` still matches (`to_signable_string` only checks `@raw_body`) [2](#0-1) , so `Utils::HmacValidator.validate(request)` returns `true`.
4. The host app calls `request.shop`, gets `"victim-shop.myshopify.com"` [4](#0-3) , and processes the attacker's payload as belonging to the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
