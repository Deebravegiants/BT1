### Title
Webhook shop identity spoofing via `X-Shopify-Shop-Domain` header not covered by HMAC verification - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor read directly from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that this gem validates (`hmac` / `to_signable_string`) only covers the raw request body, never the headers. A host application using this gem's `Request#shop` to determine which tenant a webhook belongs to is trusting an unauthenticated field alongside a cryptographically verified one.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
and `Request#hmac` is computed from the `X-Shopify-Hmac-Sha256` header: [2](#0-1) 

`Utils::HmacValidator.validate` verifies that `to_signable_string` (i.e. the raw body only) matches the HMAC computed with `Context.api_secret_key`: [3](#0-2) 

Separately, `Request#shop` simply reads the `shopify-shop-domain` header with no cryptographic binding to the signed body: [4](#0-3) 

The identity binding a host app relies on when it authenticates a webhook is effectively:
`HMAC_valid(raw_body, secret) == true` ⇒ "this body came from Shopify"
but it is silently extended to:
`request.shop == "the merchant this body is for"`
even though `shop` is never an input to the HMAC computation. These two values are not bound together — only the body is authenticated, not the header that identifies the tenant.

Because any Shopify merchant (including an attacker who owns/controls a free/dev store using the same app) legitimately receives real webhooks with a valid HMAC signed with the *app's own* `client_secret` for their own shop, they can capture such a request and resend it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Webhook-Id`, `X-Shopify-API-Version`) header rewritten to name a different, victim shop. `Utils::HmacValidator.validate` will still return `true` (raw body and HMAC are unchanged and valid), and `Request#shop` will report the victim's domain. If the host application uses `Request#shop` (as the gem's documented API surface intends) to select which merchant's session/access token/tenant context to act under, this results in cross-tenant data confusion: the attacker's own webhook body gets processed and attributed to a different merchant's tenant.

### Impact Explanation
This is a cross-tenant boundary violation: an unprivileged actor who legitimately controls one shop (no `api_secret_key`, no access token, no privileged account required — any Shopify store can install a public app and receive real webhooks for itself) can cause a webhook payload to be misattributed to a different shop id, because the field the host app uses to route/authorize per-tenant (`shop`) is not covered by the same guarantee (`hmac`) that authenticates the payload. Depending on how the host app uses `shop` (e.g., to look up a session/access token, trigger tenant-scoped side effects, or to key data writes), this can lead to cross-tenant access or data corruption — matching the "Critical - cross-tenant access" impact class.

### Likelihood Explanation
Moderate-to-high: exploitation only requires the attacker to (a) install the app on their own shop to receive one legitimately HMAC-signed webhook, and (b) replay it with a modified `Shop-Domain` header to the app's public webhook endpoint. No secrets, tokens, or privileged access are needed. The main precondition is that the host application actually keys tenant-sensitive logic off `Request#shop` rather than an out-of-band trusted route/config — which is the exact pattern this gem's minimal API (`shop` as a plain attribute, no cross-check against `hmac`) invites.

### Recommendation
Bind `shop` into the authenticated payload rather than leaving it as a bare, unauthenticated header accessor:
- Document/require that `to_signable_string` (or a companion validated attribute) include the shop domain the app expects, or
- Add a method that returns the shop domain only after re-verifying it against a value that participated in HMAC computation (e.g. cross-check against the `dest`/`shop` inside the associated webhook topic payload keys such as order/customer ids that are tenant-scoped upstream), and clearly document in `Request` that `shop` is unauthenticated header data and must not be used alone as a tenant-authorization signal.

### Proof of Concept
1. Install the target app (any public/dev Shopify app using this gem) on attacker-owned shop `attacker.myshopify.com`.
2. Trigger a webhook (e.g. `orders/create`) — Shopify sends:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC of raw_body with app's client_secret>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   X-Shopify-Webhook-Id: ...
   <raw_body>
   ```
3. Capture this request, then resend it to the app's webhook endpoint with `X-Shopify-Shop-Domain: victim.myshopify.com`, keeping `raw_body` and `X-Shopify-Hmac-Sha256` byte-for-byte identical.
4. `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` (raw body) and `hmac` are unchanged. [5](#0-4) 
5. `request.shop` now returns `"victim.myshopify.com"`. [4](#0-3) 
6. Any host-app logic that trusts `request.shop` as the tenant for this validated payload now processes attacker-controlled body content under the victim's tenant context.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
