### Title
Webhook `shop` identity is read from an unauthenticated header not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, but exposes a separate `shop` accessor that is read directly from the `X-Shopify-Shop-Domain` header. Nothing binds the verified body to the shop-domain header, so the "authenticated" webhook payload and the "authenticated" tenant identity are two independent, separately-forgeable inputs.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string` and compares it to the `hmac` value (also taken from a header): [2](#0-1) 

Meanwhile, `Request#shop` — the value the host application uses to identify which merchant/tenant the webhook belongs to — is pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, completely outside the signed material: [3](#0-2) 

This is a case of "a field acted on but not covered by the HMAC": the equality the gem should enforce is `hmac == HMAC(secret, raw_body || shop)`, but it actually enforces only `hmac == HMAC(secret, raw_body)`, while `shop` is trusted independently and unauthenticated. `topic`, `api_version`, and `webhook_id` (also read via `shopify_header`) share the same weakness.

### Impact Explanation
An entity that legitimately receives real webhooks for **its own** shop (i.e., any merchant who installs the app) can capture a genuine `(raw_body, hmac)` pair that Shopify sent to the app's webhook endpoint. Because the HMAC never binds to the shop-domain header, that same `(raw_body, hmac)` pair remains valid when replayed with an arbitrary `X-Shopify-Shop-Domain` header value pointing at a different (victim) shop. Any host application that follows the gem's documented pattern of trusting `Request#shop` to select/scope the tenant session or database record for processing the payload will process the attacker's replayed body under the victim's identity — a cross-tenant data-integrity/spoofing issue that crosses a tenant boundary the gem is supposed to enforce.

### Likelihood Explanation
Any registered/legitimate app installer (an "unprivileged" party relative to other merchants, i.e., someone who has never touched `api_secret_key` or another tenant's credentials) can trigger a real webhook for their own store to obtain a valid signature, then send a raw HTTP request to the app's public webhook endpoint with a swapped shop-domain header. No access to the app's `client_secret`/`api_secret_key`, another merchant's access token, or infrastructure interception is required — only observation of one's own legitimately-delivered webhook traffic, which is trivial for anyone with a developer/test store.

### Recommendation
Include the shop-domain (and ideally topic/api-version/webhook-id) header values in the signed material verified by `HmacValidator`, or otherwise cryptographically bind them to the body before `Request#shop` is trusted as a tenant identifier — e.g., extend `to_signable_string` to also incorporate the shop header, matching Shopify's actual webhook-verification contract, and document that consumers must not treat `shop` as authenticated unless it participates in the signature check.

### Proof of Concept
1. App developer installs the app on `attacker-shop.myshopify.com` and captures a legitimate webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid `HMAC(secret, B) == H`), along with `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker crafts a new HTTP POST to the same app webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. The app calls `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` and then `HmacValidator.validate(request)`; since validation only checks `HMAC(secret, B)` against `H`, verification succeeds: [4](#0-3) 
4. The host application, following the gem's documented pattern, reads `request.shop` (`"victim-shop.myshopify.com"`) to look up/scope the tenant and processes the (attacker-supplied) payload `B` as if it legitimately originated from the victim shop — a cross-tenant identity binding break.

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
