Found it. In `ShopifyAPI::Webhooks::Request` (`lib/shopify_api/webhooks/request.rb`), the `shop` value used to identify the tenant is taken directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header, while `to_signable_string` for HMAC verification only covers `@raw_body`:

```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end

def to_signable_string
  @raw_body
end
``` [1](#0-0) 

### Title
Webhook `shop` identity not bound by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates HMAC over `@raw_body` only [2](#0-1) , but exposes `shop` (the tenant identifier used to look up/act on merchant data) straight from the `shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed bytes [3](#0-2) . This breaks the intended equality "the shop that is HMAC-authenticated == the shop the host application acts on."

### Finding Description
`HmacValidator`/`VerifiableQuery` pattern used elsewhere in this gem (e.g. OAuth `AuthQuery`) explicitly folds `shop` into `to_signable_string` so a forged/replayed request cannot change `shop` without invalidating the signature [4](#0-3) . `Webhooks::Request`, however, signs only the raw JSON body and reads `shop` from an HTTP header that is never covered by that signature [2](#0-1) . Two requests with identical bodies but different `shop-domain` headers produce the same valid HMAC, so `Request#shop` can be set to any value independent of what was actually signed.

### Impact Explanation
If a host application follows this gem's own API and uses `Request#hmac` to authenticate the payload and `Request#shop` to select which merchant/session the payload applies to (a documented, intended usage pattern, not a documented misuse), an attacker who can reach the webhook endpoint could replay a body with a valid HMAC (e.g. by reusing/observing any prior legitimately-signed body for a different, less sensitive event) while supplying an arbitrary `shop-domain` header, causing the host app to attribute/act on that payload under the wrong tenant. This is a cross-tenant identity-binding break of exactly the same class as the ERC20 report's "field acted on but not covered by the integrity check."

### Likelihood Explanation
Requires the attacker to control HTTP headers on a request to the app's public webhook endpoint (headers are attacker-controlled by construction) and to know or capture at least one validly-signed raw body/HMAC pair for the target `api_secret_key`'s webhook stream (e.g., from a webhook the app previously received for a different, low-privilege shop, since HMAC only depends on body+secret, not shop). This does not require the `api_secret_key` itself.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`) inside the signed bytes checked against the HMAC, or otherwise cryptographically bind the shop-domain header to the HMAC-verified payload before exposing `Request#shop`, mirroring the pattern already used in `Auth::Oauth::AuthQuery#to_signable_string`.

### Proof of Concept
1. Capture any legitimate webhook delivery to the app (raw body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: shop-a.myshopify.com`) — `H` is valid for body `B` under the app's secret regardless of shop.
2. Replay a request with the same body `B` and same `H`, but set `x-shopify-shop-domain: shop-victim.myshopify.com`.
3. Build `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: replayed_headers)`; `Utils::HmacValidator.validate(request)` (via `request.hmac` vs `Context.api_secret_key`) still returns `true` because validation only checks `B` [5](#0-4) , while `request.shop` now reports `shop-victim.myshopify.com` [3](#0-2) , causing any host logic keyed on `request.shop` to process the event under the wrong tenant despite HMAC "passing."

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
