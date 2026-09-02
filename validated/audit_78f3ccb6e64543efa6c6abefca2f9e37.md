This is a critical finding: in `lib/shopify_api/webhooks/request.rb`, the `shop` attribute used by host applications to key/attribute the webhook to a tenant is read directly from the `shopify-shop-domain` HTTP header [1](#0-0) , while the HMAC signature that `Utils::HmacValidator`/consumers are expected to check only covers `@raw_body` via `to_signable_string` [2](#0-1) . The `shop-domain` header is never included in the signed bytes, so an attacker who can produce a validly-HMAC'd body (e.g., replaying a legitimately captured webhook payload/signature pair, which Shopify does not bind to a specific shop header) can swap the `X-Shopify-Shop-Domain` header to a different tenant's domain while keeping the same body+HMAC, and `Request#shop` will report the attacker-chosen tenant even though `hmac` validation passes.

However, on reflection this requires the attacker to already possess a validly-signed body (same secret), which normally means they already control a webhook payload for their own shop — cross-tenant impact requires the attacker to somehow obtain another tenant's raw body+hmac pair (e.g. via logging, or if the body content is shop-agnostic/ same for multiple test payloads). This is a real gap versus the stated binding "shop authenticated versus shop stored as session key" but the exploit path depends on the host application trusting `Request#shop` to key session storage without any additional shop-in-payload cross-check — which is exactly how the library's own docs (`shop-domain` header) intend it to be used, so this isn't "ignoring documented API," it's a genuine binding gap in `to_signable_string`.

### Title
Webhook `shop` identity not covered by HMAC binding, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#shop` is derived from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature validated via `Utils::HmacValidator`/`VerifiableQuery` only covers the raw request body (`to_signable_string` returns `@raw_body`) [2](#0-1) . The `shop-domain` header is never part of the signed content, breaking the equality "shop verified by HMAC == shop used to attribute/store the webhook."

### Finding Description
`Webhooks::Request` exposes `shop` by simply reading the `shopify-shop-domain` header off the request without any cryptographic binding to that value [1](#0-0) . The `hmac` method decodes the `hmac-sha256` header for comparison [3](#0-2) , and `HmacValidator.validate` computes/compares the signature only against `to_signable_string`, i.e. the raw body bytes [4](#0-3) [2](#0-1) . Because `shop`, `topic`, `api_version`, and `webhook_id` are all sourced from headers outside the signed bytes, none of them are cryptographically bound to the verified signature — only the body content is proven authentic. Contrast this with `Auth::Oauth::AuthQuery#to_signable_string`, which explicitly includes `shop` in the signed parameters [5](#0-4) , showing that in this gem the convention elsewhere is to bind the tenant identifier into the signed material — the webhook path does not follow that convention.

### Impact Explanation
If an app relies on `Request#shop` (post-`Errors::InvalidWebhookError`-free / HMAC-validated) to determine which tenant's session/data to act on, an attacker who can obtain any single valid `(raw_body, hmac)` pair for the shared app secret (e.g., a webhook payload with generic/shared content, or one captured via a compromised/rogue installed shop under the same app) can resend it with an arbitrary `X-Shopify-Shop-Domain` header, causing the host application to process the payload as belonging to a different, victim tenant. This is a cross-tenant confusion vector because the "shop" identity presented to the application is not the one the signature actually vouches for.

### Likelihood Explanation
Likelihood is constrained by the need for the attacker to control an app-installed shop (to receive genuinely HMAC-valid payloads for that same `client_secret`) and for the body content to be usable/harmful when misattributed to another shop domain — the gem does not itself embed the shop domain in the signed payload, so this weakness is structural, not merely theoretical, but real-world exploitation depends on the specific webhook topic/body semantics and how the host app keys data off `Request#shop`.

### Recommendation
Do not derive `shop` (or `topic`/`webhook_id`) purely from headers when using it for tenant attribution; instead, verify the header value is consistent with, or drawn from, data actually inside the signed body where Shopify includes it, or update `to_signable_string` (and the validation contract in `VerifiableQuery`) to incorporate the relevant headers (e.g. shop domain) into the HMAC computation so they are covered by the verified signature. At minimum, document explicitly that `Request#shop` is unauthenticated and must not be trusted for tenant keying without an independent cross-check against the stored session's shop for the given webhook subscription.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com` with raw body `B` and a valid `X-Shopify-Hmac-Sha256` header computed over `B` with the shared `client_secret`.
2. Attacker (who also owns an app installation, or intercepts the payload) resends the same `raw_body` `B` and same `hmac-sha256` header, but sets `X-Shopify-Shop-Domain: shop-victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: attacker_headers)` is constructed; `hmac` still decodes correctly and `Utils::HmacValidator.validate(request)` returns `true` because validation only checks `B` against the secret [3](#0-2) [2](#0-1) .
4. `request.shop` now returns `shop-victim.myshopify.com` [1](#0-0) , and any host application logic keyed off "HMAC validated ⇒ trust `request.shop`" will act on the victim's tenant using attacker-controlled body content.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L34-43)
```ruby
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
