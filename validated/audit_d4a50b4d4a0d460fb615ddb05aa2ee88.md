### Title
Webhook `shop-domain` Header Is Not Bound to the HMAC-Verified Payload, Allowing Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies the authenticity of an incoming webhook by computing an HMAC over the raw request body only, but the `shop` (tenant identity) is read from a separate, unauthenticated HTTP header that is never included in the signed content. This mirrors the reported `BatchTrade` bug class: an attacker-controllable field (`taker`/here, the claimed `shop-domain`) is not bound to the field that is cryptographically verified (the `spender`/here, the signed request body), letting an attacker present genuine, signed data under a different identity than the one it was actually signed for.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#hmac` decodes the `X-Shopify-Hmac-Sha256` header for comparison against that body [2](#0-1) . Validation is performed generically by `Utils::HmacValidator.validate`, which HMACs `to_signable_string` with the app's secret and compares it to the supplied `hmac` [3](#0-2) .

Critically, the tenant identity — `shop` — is derived from the `X-Shopify-Shop-Domain` header, which is **not** part of `to_signable_string` and therefore not covered by the HMAC at all: [4](#0-3) .

This breaks the identity binding: `hmac(raw_body) == verified` should imply `shop == tenant_that_the_body_belongs_to`, but in this implementation `shop` is an independent, unauthenticated header value while only `raw_body` is authenticated. The `VerifiableQuery` interface itself only requires `hmac` and `to_signable_string` [5](#0-4) , so nothing in the library enforces that the claimed shop is cryptographically tied to the payload it accompanies.

Contrast this with `Auth::Oauth::AuthQuery`, where `shop` **is** included in `to_signable_string` and is therefore bound by the HMAC [6](#0-5) . The webhook path lacks this equivalent binding.

### Impact Explanation
Any consumer of this gem that uses `Webhooks::Request#shop` to select the session, tenant, or shop-scoped data store (a documented and expected usage pattern, since `shop` is exposed specifically for that purpose) can be made to associate an authentic Shopify-signed payload with the wrong shop. Concretely: a merchant who legitimately installs the app on their own store (an unprivileged party, no `api_secret_key` or access token needed) receives real, correctly-signed webhook deliveries for their store. Because the HMAC never covers the `shop-domain` header, that merchant can capture one authentic `(raw_body, hmac)` pair from their own store and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. The HMAC check still passes (it only validates `raw_body`), and the host application — trusting `request.shop` to route the update — will attribute attacker-controlled webhook content to the victim tenant. This is a cross-tenant data/identity confusion: exactly the "Critical - cross-tenant access" category, since the boundary between two merchants' tenant-scoped data is crossed using only a legitimately-obtained webhook from the attacker's own shop.

### Likelihood Explanation
Likely to be reachable in practice: webhook `shop-domain` is documented and used specifically to identify the originating shop, so most integrations key session/tenant lookup off `Webhooks::Request#shop` after calling `HmacValidator.validate`. Obtaining one authentic signed payload only requires installing the app as a normal merchant (no elevated credentials, no access token, no `api_secret_key`), making this trivially reachable by an unprivileged internet user who is a legitimate app user on their own store.

### Recommendation
Bind `shop` to the HMAC-verified content instead of trusting an independent header: either require the host application to cross-check `shop-domain` against a shop value embedded in and covered by the signed payload, or extend `to_signable_string` (or a new signable representation) to bind the shop identity claim into the HMAC computation before it's trusted for tenant routing. At minimum, document prominently that `Webhooks::Request#shop` is NOT covered by HMAC verification, and encourage consumers to independently confirm the delivery's shop against a known-registered webhook (e.g., match against a locally stored expected shop/topic/webhook_id combination) rather than trusting the header value alone.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` (legitimate installation, no privileged access needed).
2. Attacker triggers/waits for a genuine webhook delivery to the app's endpoint; captures the raw body and the `X-Shopify-Hmac-Sha256` header — both valid and correctly signed for `attacker-shop.myshopify.com`.
3. Attacker resends the exact same raw body and HMAC header to the app's webhook endpoint, but replaces the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `raw_body` via `Request#to_signable_string` [1](#0-0) [7](#0-6) .
5. The host application reads `request.shop` [4](#0-3)  to route/attribute the (attacker-controlled) payload to `victim-shop.myshopify.com`, achieving cross-tenant data injection despite a "passing" signature check.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/utils/verifiable_query.rb (L11-16)
```ruby
      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
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
