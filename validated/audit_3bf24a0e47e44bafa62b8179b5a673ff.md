Found: in `Webhooks::Request`, the `shop` field (`shop-domain` header) is **not part of the HMAC-signed bytes**. The HMAC is computed only over `@raw_body`, while `shop` (and `topic`, `webhook-id`, `api-version`) come from HTTP headers that are never covered by the signature. [1](#0-0) 

### Title
Webhook `shop-domain` header is unauthenticated / unbound to the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` to return only `@raw_body` [2](#0-1) . The `hmac` used for verification is derived from the `X-Shopify-Hmac-Sha256` header and validated (via `HmacValidator.validate`) against a signature computed only over the raw request body [3](#0-2) . However, the `shop` accessor — the tenant identity used by consuming apps to route/store webhook data — is read directly from the `shopify-shop-domain` (or `x-shopify-shop-domain`) HTTP header, which is never included in the signable string [4](#0-3) . The same applies to `topic`, `webhook_id`, and `api_version` [5](#0-4) .

This breaks the identity binding: `bytes verified` (the raw body) ≠ `bytes used to determine tenant` (the `shop` header). An attacker who can influence or spoof the `shop-domain` header on a request whose body/HMAC pair is otherwise valid (e.g., a proxy, load balancer, or any intermediary that forwards attacker-controlled headers alongside a legitimately-signed body) can cause the consuming app to attribute the webhook payload to a different shop than the one that actually produced it.

### Impact Explanation
If an application trusts `Request#shop` to select which merchant's data store to write to (a common integration pattern for multi-tenant Shopify apps), a mismatch between the signed body and the unsigned shop header enables cross-tenant data injection/confusion — writing shop A's legitimately-signed webhook payload into shop B's tenant record if the `shop-domain` header can be manipulated in the delivery path. This matches the "cross-tenant access" impact class.

### Likelihood Explanation
Exploitability depends entirely on whether an attacker can control or race headers independently of the signed body in the app's specific deployment (e.g., through a misconfigured reverse proxy, replay tooling, or an endpoint that merges multiple header sources). Within the gem's own trust boundary, this is a genuine design gap: the library gives developers no verified `shop` value, yet exposes `shop` as if it were part of the authenticated payload, encouraging misuse in host applications. The likelihood is Low-Medium since it requires a header-controllable delivery path.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the canonical signable string (or otherwise cryptographically bind them to the payload) so that `HmacValidator.validate` cannot succeed unless the tenant-identifying headers match what was actually signed by Shopify. At minimum, document clearly that `Request#shop`/`#topic` are unauthenticated metadata and must not be used for tenant routing without additional verification.

### Proof of Concept
1. Shopify sends a legitimate webhook for `shop-a.myshopify.com` with body `B` and `X-Shopify-Hmac-Sha256` = HMAC(`B`, secret).
2. An intermediary (proxy/gateway) in the app's infrastructure rewrites or duplicates the `X-Shopify-Shop-Domain` header to `shop-b.myshopify.com` while forwarding the same body `B` and HMAC.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `HmacValidator.validate` succeeds because it only checks `to_signable_string` (`B`) against the HMAC [6](#0-5) .
4. The host app reads `request.shop` (`shop-b.myshopify.com`) and applies `B`'s data to shop B's tenant, even though the payload was authored for shop A.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
