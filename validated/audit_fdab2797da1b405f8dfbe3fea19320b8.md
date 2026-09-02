### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop` and `topic` derived directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`), but `to_signable_string` — the data actually verified by `HmacValidator` — is only the raw request body. `HmacValidator.validate` therefore proves the body's authenticity but says nothing about which shop or topic the webhook is claimed to be for.

### Finding Description
`Utils::HmacValidator.validate` computes an HMAC over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac` [1](#0-0) . For webhooks, `Request#to_signable_string` returns only `@raw_body` [2](#0-1) , while `Request#hmac` is decoded from the `X-Shopify-Hmac-Sha256` header [3](#0-2) .

However, `Request#shop` and `Request#topic` — the values the host application is expected to use to route the webhook to the correct tenant/handler — are read straight from the `shopify-shop-domain` and `shopify-topic` headers [4](#0-3) . Neither header is part of `to_signable_string`, so the HMAC signature never binds the verified body to the claimed shop or topic.

The identity binding that should hold is: `hmac_valid(raw_body) == true` should imply `shop header == shop the body actually originated from`. In this implementation, the equality is broken: HMAC validity only proves the body came from Shopify for *some* topic/shop; it does not prove the body was generated for the `shop-domain` header value attached to this particular request.

### Impact Explanation
An app that trusts `Request#shop` (as documented in the webhook registration/handler flow, e.g. `Webhooks::Registry`) to select per-tenant credentials, session data, or business logic can be made to process a webhook body as if it belonged to a different shop than the one that actually generated it, since only the body — not the shop header — is authenticated. This is a cross-tenant identity-binding gap: the header used for tenant dispatch is unauthenticated while the payload is authenticated, letting an attacker who can influence transport-level headers (e.g., a reverse proxy misconfiguration, replay through a different endpoint, or any component that forwards raw body + swapped headers) cause the app to attribute a legitimate webhook body to the wrong shop.

### Likelihood Explanation
Exploitability depends on the host application's transport layer allowing header manipulation independent of the signed body (e.g., a shared ingress point, proxy, or webhook relay that does not itself bind headers to body). This is a real gap in the gem's own verification logic — `to_signable_string` simply omits fields (`shop`, `topic`) that `Request` otherwise exposes and that documented usage relies on for dispatch — rather than a host-application misuse of a documented contract, since the gem provides no HMAC coverage over these fields at all.

### Recommendation
Include the `shopify-shop-domain` and `shopify-topic` header values in the HMAC-covered signable data (or otherwise cryptographically bind them to the payload), or at minimum document clearly that `Request#shop`/`Request#topic` are unauthenticated and must not be trusted for tenant routing without additional verification (e.g., cross-checking against a shop known to be currently registered/active).

### Proof of Concept
1. Attacker captures a legitimate webhook: raw body `B` with valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify over `B` using the app's shared secret) for shop `A`.
2. Attacker replays the same body `B` and same HMAC header `H`, but changes the `X-Shopify-Shop-Domain` header to shop `Z`, and delivers it to the same endpoint.
3. `HmacValidator.validate(request)` still returns `true`, because it only checks `H` against `HMAC(secret, B)` [2](#0-1) .
4. `request.shop` now returns `Z` [5](#0-4) , so any host code that dispatches based on `request.shop` processes shop A's payload under shop Z's tenant context, despite HMAC verification reporting success.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
