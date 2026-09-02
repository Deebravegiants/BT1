### Title
Webhook `shop` (and `topic`/`api-version`) identity is trusted from unauthenticated HTTP headers while the HMAC signature only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `api_version`, and `webhook_id` accessors that are read directly from HTTP headers, but the HMAC signature that the gem validates (`to_signable_string`) only ever covers `@raw_body`. This breaks the identity binding: `shop_header_value == shop_bound_by_hmac` does not hold, because the HMAC never signs the `shop-domain` header at all.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. the raw body, and compares it to the `hmac-sha256`/`x-shopify-hmac-sha256` header value: [2](#0-1) 

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from headers with no cryptographic binding: [3](#0-2) 

This is the exact bug class from the report ("a field acted on but not covered by the HMAC"): the gem lets a caller construct a `Request` object whose `shop` field can be set to anything, and the only integrity check the library provides (`HmacValidator.validate`) can pass as long as the body's HMAC matches — it says nothing about which shop the body/header claims to be from. An unprivileged internet user who obtains one valid `(raw_body, hmac)` pair for their own shop (e.g. by triggering a real webhook event on a shop they control, or via a shop they have installed the app on) can resend that exact body with an `X-Shopify-Shop-Domain` header rewritten to a victim's shop domain. `HmacValidator.validate` will still return `true` because the signature only checks the body bytes, which were untouched.

### Impact Explanation
If a host application uses this gem's `Webhooks::Request#shop` (as documented/intended — this is the field the gem exposes specifically for that purpose) to decide which merchant record to update/delete/create data for after calling `HmacValidator.validate`, an attacker can forge the tenant identity of a webhook while keeping a valid signature. This is a cross-tenant boundary violation: data intended for shop A's webhook consumption is processed under whatever `shop` value the attacker supplies, without any additional check that the header shop matches an HMAC-covered claim. This matches the "cross-tenant access" impact category, since the app can be tricked into acting on/for a shop the attacker doesn't control, purely through gem-provided verification primitives that consumers reasonably trust once `HmacValidator.validate` succeeds.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that follows the gem's own webhook documentation. The attacker only needs: (1) a body+hmac pair from a webhook belonging to any shop willing to install the app (including their own shop), and (2) the ability to send an HTTP request with attacker-controlled headers to the app's public webhook endpoint. No access token, `client_secret`, or privileged Shopify account is required — only a normal merchant installation of the target app on any shop, which is the "unprivileged internet user" scenario used throughout the report.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable string used by `HmacValidator`, or otherwise bind them cryptographically to the payload before trusting them, so that `to_signable_string` in `lib/shopify_api/webhooks/request.rb` cannot be satisfied by an HMAC that only ever covered the raw body. At minimum, document loudly (and enforce in code) that `Request#shop` must never be trusted for authorization/tenant-scoping decisions unless it is independently re-verified against a stored, per-shop webhook secret or the shop's registered domain.

### Proof of Concept
1. Register the app on `attacker-shop.myshopify.com` and capture a legitimate webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Craft a new HTTP request to the app's webhook endpoint with the identical body `B` and identical `X-Shopify-Hmac-Sha256: H`, but change `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. Construct `req = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {"x-shopify-hmac-sha256" => H, "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-topic" => <any>})`.
4. Call `ShopifyAPI::Utils::HmacValidator.validate(req)` — it returns `true` because it only recomputes the HMAC over `req.to_signable_string` (`== B`), which was untouched.
5. `req.shop` now reports `"victim-shop.myshopify.com"` despite the signature never having covered that value, demonstrating the header/HMAC identity mismatch.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
