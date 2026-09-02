### Title
Webhook Shop-Domain Header Not Covered by HMAC Signature Enables Cross-Tenant Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor sourced from the `X-Shopify-Shop-Domain` HTTP header, which host apps use to identify the tenant a webhook belongs to. However, the HMAC verification performed via `ShopifyAPI::Utils::HmacValidator.validate` only signs the raw request body (`to_signable_string` returns `@raw_body`), never the `shop-domain`, `topic`, or `webhook-id` headers. This breaks the intended binding: `shop` (acted upon by the host app to key per-tenant data) ≠ `shop` (bytes actually covered by the HMAC).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop` is read straight from the `shopify-shop-domain` header, independent of the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [3](#0-2) 

Contrast this with the OAuth callback flow, where `shop` (along with `host`, `code`, `state`, `timestamp`) is explicitly part of the signed query string via `AuthQuery#to_signable_string`: [4](#0-3) 

Because the webhook HMAC never covers the shop-domain header, any party capable of producing a body+HMAC pair that legitimately validates (e.g., the operator of their own attacker-controlled Shopify store, who receives real webhooks with real signatures from Shopify for their own shop) can freely relabel the `X-Shopify-Shop-Domain` header to any other tenant's domain when forwarding/replaying the request to the app's webhook endpoint. The signature will still validate because it never checked that header, so the app will process the payload under the attacker-chosen `shop` identity while the cryptographic proof only ever attested to the attacker's own shop and body content.

### Impact Explanation
This breaks the tenant identity binding `shop == HMAC-verified shop`, which is exactly the class of cross-tenant boundary violation called out as in-scope (Critical: cross-tenant access). A host application that uses `Request#shop` to decide which merchant's records to create/update/delete based on a verified webhook is vulnerable to cross-tenant data injection or corruption, since the "verified" shop identity is not actually bound to the signature.

### Likelihood Explanation
Any unprivileged internet user can operate their own free/dev Shopify store, subscribe it to webhooks for topics the app registers, and receive genuine `hmac-sha256` + body pairs from Shopify for their own store. Because the header carrying the tenant identity is untouched by the signature, forging a request that reuses that valid signature/body but with an attacker-chosen `shop-domain` header requires no cryptographic secret — only the ability to relay HTTP requests to the target app's public webhook endpoint.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) headers as part of the signed material verified against the HMAC, or otherwise cryptographically bind the header-derived `shop` value to the payload before exposing it via `Request#shop`. At minimum, document/enforce that consumers must not trust `Request#shop` for tenant routing without independent verification (e.g., cross-checking against a shop this app is actually installed on with a matching stored access token).

### Proof of Concept
Conceptual PoC (cannot be executed without a live app instance and registered shop, out of scope for unit test file per rules, but conceptually):
1. Attacker registers a normal dev/partner Shopify store `attacker-shop.myshopify.com` and installs the target app so Shopify sends genuine webhooks to the app's endpoint, each with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's real `client_secret`.
2. Attacker captures one such request (`raw_body`, `hmac` header) for a topic/body they can influence (e.g., `orders/create` with attacker-controlled order data in their own store).
3. Attacker replays the same `raw_body`/`hmac` pair to the app's webhook endpoint, but rewrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` is constructed and `HmacValidator.validate` succeeds, because it only checks `raw_body` against `hmac` — the forged `shop-domain` header is never covered. [5](#0-4) [6](#0-5) 
5. The host app, trusting `request.shop == "victim-shop.myshopify.com"` because "HMAC validated", processes the attacker's payload against the victim tenant's data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
