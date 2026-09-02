Found it: `Webhooks::Request` — the `shop` field returned to the caller (used to identify the tenant/shop for the webhook) is read directly from the `x-shopify-shop-domain` header, but the HMAC signature (`to_signable_string`) only covers the raw request body, not the `shop-domain` header.

### Title
Webhook shop identity not bound to HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that host applications use to determine which merchant/tenant a webhook belongs to, but this value is taken from an unauthenticated HTTP header (`x-shopify-shop-domain`) that is never included in the HMAC-verified payload.

### Finding Description
The verification contract for this class is defined by `Utils::VerifiableQuery`: `hmac` and `to_signable_string` are the only two values that get compared against each other during verification. In `Request#to_signable_string` the signable content is exactly `@raw_body` [1](#0-0) . The `shop` value, however, is read straight out of the `shopify-shop-domain` / `x-shopify-shop-domain` header via `shopify_header("shop-domain")` [2](#0-1) , and headers are never mixed into `to_signable_string`. The HMAC (`hmac-sha256` header, base64-decoded) only proves that the attacker who sent the request possesses (or can compute with) the request body's HMAC — it says nothing about which shop the body "belongs" to, because `shop` is not part of the signed material.

The equality the gem is implicitly claiming to enforce is:
`hmac == HMAC(secret, body) AND shop == the shop that produced this body`

But only the left half is checked. `shop` is an independent, attacker-controlled header value that rides along with a validly-signed body without being cryptographically bound to it.

### Impact Explanation
Any host application that trusts `Webhooks::Request#shop` to select/authenticate the merchant tenant for whom the webhook payload should be processed (a supported and documented usage of this class — it is the only exposed accessor for tenant identity) is exposed to cross-tenant data confusion: an attacker who can obtain one validly-HMAC-signed webhook body (e.g., by triggering a real webhook against their own trial/dev shop, since apps typically share one `client_secret`/webhook secret across all installations) can resend that same body with an arbitrary `x-shopify-shop-domain` header, and this gem will report `valid == true` while `shop` returns the attacker-chosen domain. This can lead the host app to associate replayed/attacker payloads with a victim shop, corrupting per-tenant records — a cross-tenant boundary violation.

### Likelihood Explanation
Requires the attacker to already have one legitimately-signed webhook body (achievable by installing the app on their own store, since the webhook signing secret is shared across all shops using the same app), plus knowledge that the host reads `.shop` from this object without independently cross-checking it against routing/registration state. This is a realistic but not trivial precondition — moderate likelihood.

### Recommendation
Include the `shop-domain` header (and ideally `topic` and `api-version`) in the signable string so that the shop identity is cryptographically bound to the HMAC, e.g. concatenate `shop|topic|raw_body` before signing verification, or document explicitly and loudly that `Request#shop` must never be trusted without an independent lookup (e.g., confirming the shop is an actively installed tenant) even when `HmacValidator.validate` returns true.

### Proof of Concept
1. App merchant A installs the app; app receives a legitimate webhook for shop A with body `B` and a valid `hmac-sha256` header `H = HMAC(secret, B)`.
2. Attacker (who is also a merchant, or intercepts their own webhook) captures `B` and `H`.
3. Attacker replays a POST to the app's webhook endpoint with the same `B` and `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(secret, B) == H` [3](#0-2) .
5. `request.shop` returns `"victim-shop.myshopify.com"` [2](#0-1) , and the host application processes attacker-controlled payload `B` as if it were data belonging to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
