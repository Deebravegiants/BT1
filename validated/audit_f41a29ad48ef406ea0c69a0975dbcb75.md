Found it. The critical binding gap is in `ShopifyAPI::Webhooks::Request`: the `shop` and `topic` fields used by the app to route/authorize the webhook are read directly from HTTP headers, while the HMAC signature (`to_signable_string`) covers **only the raw request body**, never the headers.

### Title
Webhook `shop`/`topic` headers are not covered by HMAC verification, allowing shop/topic spoofing with a replayed valid body signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while the `shop`, `topic`, `api_version`, and `webhook_id` values that a consuming app relies on for tenant identification and handler dispatch are read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) with no cryptographic binding to those headers [2](#0-1) .

### Finding Description
`Utils::HmacValidator.validate` computes an HMAC over whatever `to_signable_string` returns and compares it to the `hmac` value from `Digest.hexencode(Base64.decode64(shopify_header("hmac-sha256")))` [3](#0-2) [4](#0-3) . For OAuth callbacks, `AuthQuery#to_signable_string` includes `code`, `host`, `shop`, `state`, and `timestamp` — i.e., every field the app trusts is inside the signed string [5](#0-4) . The webhook `Request` object breaks this pattern: `shop`, `topic`, `api_version`, and `webhook_id` are all read from headers [6](#0-5)  but `to_signable_string` signs only the body bytes, not the headers. The equality that should hold — "bytes verified == bytes an app trusts for identity" — is broken: `hmac` verifies `@raw_body` only, but the app trusts `shop` (tenant) and `topic` (handler dispatch) from unauthenticated header bytes.

### Impact Explanation
An unprivileged attacker who has legitimately received (or replayed) one valid webhook delivery for a given body — e.g., from their own store, or a body that happens to validate against the app's secret for any reason — can resend the exact same body with a *different* `shopify-shop-domain` and/or `shopify-topic` header while keeping the original (still-valid, since unrelated to headers) HMAC signature. Because the constructor only asserts the required headers are *present*, not that they match what was signed, `Request#shop` and `Request#topic` will return attacker-chosen values that pass HMAC validation. Any consuming app that follows this gem's documented flow — validate then dispatch/store by `shop`/`topic` — can be tricked into processing a webhook body under the wrong shop or wrong topic handler, leading to cross-tenant data being associated with an attacker-chosen shop identifier.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one genuinely-signed webhook body (trivial for an app owner/merchant on their own store, since webhook bodies for identical resource states/topics can be predictable or replayed across shops using the same app), then simply alter the two headers before replay to a receiving endpoint that has no additional freshness/nonce/timestamp check beyond what this gem provides. This is a direct root-cause library gap (not a host misuse) since the gem's own `to_signable_string` and header-exposure design is what allows the split between signed bytes and trusted identity fields.

### Recommendation
Include the `shop`, `topic`, `api_version`, and `webhook_id` header values in the signable string (or otherwise cryptographically bind them to the HMAC-covered payload) so `Request#shop`/`#topic` cannot diverge from what was actually signed by Shopify.

### Proof of Concept
1. Capture a legitimate webhook delivery for `shop=victim.myshopify.com`, `topic=orders/create`, with body `B` and valid `hmac-sha256` header `H` (computed over `B` only).
2. Replay a new HTTP request to the app's webhook endpoint with the same body `B` and same header `H`, but change `shopify-shop-domain` to `attacker.myshopify.com` and/or `shopify-topic` to a different topic.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` still returns `true` because `to_signable_string` returns `B`, unchanged [1](#0-0) .
4. `request.shop` and `request.topic` now return the attacker-supplied values [7](#0-6) , causing the host app (following documented usage) to process/store the payload under the wrong tenant or topic.

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
