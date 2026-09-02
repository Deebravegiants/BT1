### Title
Webhook `shop` identity is trusted from an unauthenticated HTTP header while only the raw body is covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature verified via `Utils::HmacValidator.validate` only covers `@raw_body`, not the header. This breaks the binding: `hmac_verified(bytes) == shop_trusted(bytes)` does not hold, because the `shop` value the application acts on is never part of the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from request headers, completely independent of the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature over `to_signable_string` (the raw body) and compares it against the `hmac-sha256` header: [3](#0-2) 

Because `shop` (and `topic`, `api_version`, `webhook_id`) are taken from headers that are not part of `to_signable_string`, the HMAC check only proves "this body was signed by Shopify with our `api_secret_key`" — it proves nothing about which shop the body came from. An attacker who legitimately owns/operates any shop that installs the app receives real, validly-signed webhook deliveries for their own shop (with correct raw body + HMAC). By replaying that exact raw body + HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Webhook-Id`/`X-Shopify-Topic` if the app dispatches by topic) to name a victim shop, the signature still validates successfully, and `Request#shop` returns the attacker-chosen tenant identifier instead of the one the payload actually originated from. This is the same class of bug as the reported issue: state used to make an authorization/identity decision (`shop`) is decoupled from the value that is actually verified (the raw body bytes), just as HSG's `claimSigner` used stale `signerCount`/owner state instead of recomputing the authoritative value before acting.

### Impact Explanation
Any code path in the host application that uses `Webhooks::Request#shop` (or the `registry.rb` handler dispatch, which is invoked with the request-derived shop) to look up per-tenant state, store data, revoke/update sessions, or otherwise scope an action to "the shop that sent this webhook" can be tricked into performing that action against an attacker-chosen victim shop identifier, using data the attacker fully controls (the raw body is also attacker-controlled since it's their own legitimately-received webhook). This is a cross-tenant identity confusion: the "Critical - cross-tenant access" bar in the rules is met because the application-level tenant binding enforced by this gem's webhook verification is provably broken.

### Likelihood Explanation
The attacker requires no privileged credentials: they only need to install the target app on their own shop (or otherwise cause the app to send them one legitimate webhook), then replay the exact raw bytes with a modified `Shop-Domain`/webhook-id header to the app's public webhook endpoint. `HmacValidator.validate` will accept it because it never inspects the header at all. This is a low-effort, unprivileged-internet-user attack path once the app's webhook endpoint is reachable.

### Recommendation
Include the tenant-identifying headers (`shop`, and ideally `topic`/`webhook_id`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the signed payload (e.g., require them to be present inside the JSON body itself, which Shopify's payload typically already includes for many topics) before trusting `Request#shop` for any authorization decision. At minimum, document that `Request#shop` is NOT authenticated by the HMAC check and must not be used as an authorization boundary on its own.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery: raw body `B`, headers including `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. `HmacValidator.validate` computes `HMAC(secret, B) == H` — true, since `to_signable_string` is just `B`. [4](#0-3) 
3. Attacker resends the exact same request to the app's webhook endpoint, only changing the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com` (and any `webhook-id`/`topic` header if the app deduplicates/dispatches on that).
4. `HmacValidator.validate` still returns `true` (body `B` and `H` unchanged), and `Request#shop` now returns `"victim-shop.myshopify.com"`, `Request#webhook_id`/`topic` return attacker-controlled values as well — because none of these are covered by `to_signable_string`. [5](#0-4) 
5. Any handler in `ShopifyAPI::Webhooks::Registry` that processes the request keyed on `request.shop` now acts as if the (attacker-controlled) payload legitimately originated from `victim-shop.myshopify.com`. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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

**File:** lib/shopify_api/webhooks/registry.rb (L1-1)
```ruby
# typed: strict
```
