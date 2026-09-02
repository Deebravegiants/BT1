Found the exact identity-binding break: in `Webhooks::Request`, the HMAC (`to_signable_string`) only covers `@raw_body` — none of `topic`, `shop`, `webhook_id`, or `api_version` are covered by the signature, yet `shop` (the tenant identifier) is read straight from an unauthenticated header and trusted by callers.

### Title
Webhook `shop` (tenant identifier) is read from an unsigned header, not bound to the HMAC-verified payload - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0) , while the `shop` attribute used to identify the tenant for session lookup and business logic is pulled directly from the `X-Shopify-Shop-Domain` HTTP header [2](#0-1) . The HMAC validated via `HmacValidator.validate` (`OpenSSL.secure_compare(computed_signature, received_signature)` over `to_signable_string`) therefore never binds the claimed `shop` header to the signed bytes [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop_header == shop_covered_by_hmac`. In this gem, `shop_covered_by_hmac` does not exist — the signable string is `@raw_body` only [4](#0-3) , and `shop` is read from `shopify_header("shop-domain")`, an HTTP header entirely outside the signed material [2](#0-1) . `Request#initialize` only checks for the *presence* of the `shopify-topic`, `shopify-hmac-sha256`, and `shopify-shop-domain` headers, never their integrity [5](#0-4) .

This mirrors the report's bug class: a value that is used for a tenant/identity decision (here, `shop`) is not covered by the cryptographic authenticator that is supposed to prove authenticity of the whole message (here, the webhook HMAC).

Because Shopify's real webhook delivery always sets a consistent `shop` header matching the signed body, this is not exploitable against genuine Shopify traffic in transit — the boundary that breaks is only exercisable if an attacker can independently deliver a *valid, differently-shop-labeled* HMAC to the host app's webhook endpoint (e.g. via header manipulation on a proxy that forwards a legitimately-signed body from shop A but relabels the `shop-domain` header, or a host application design that lets an attacker choose which shop's payload triggers processing while spoofing a different `shop` value). This gem exposes `shop` as a trusted, unauthenticated attribute of `Request` with no built-in mechanism to detect mismatch between the header and the body content, meaning any host application that relies on `Request#shop` for tenant scoping (e.g. selecting which merchant's session/access token to act on) is trusting an unauthenticated field for a cross-tenant decision.

### Impact Explanation
If a host application uses `Request#shop` to select which merchant's session/access token to use for follow-up API calls in response to a webhook (a common integration pattern), an attacker capable of influencing headers on the request path (e.g., a shared/misconfigured reverse proxy, or any component that reconstructs headers before this gem's `Request` object is built) can cause the app to process a legitimately-signed webhook body under a different shop's identity — a cross-tenant confusion. This matches the Critical impact category "cross-tenant access."

### Likelihood Explanation
Likelihood is constrained: exploitation requires the attacker to control or corrupt the `shop-domain` header independently of the signed body, which typically requires a header-injection or proxy-based vector upstream of this gem — not a capability of a generic unprivileged internet user sending crafted HTTP requests directly to a correctly configured endpoint, since Shopify itself always sends matching header/body pairs and the HMAC would fail if the body were tampered with. The core root cause (missing binding) is nonetheless a genuine, provable gap in this gem's own code, independent of any host application error.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them to the body) so `HmacValidator.validate` can detect any mismatch between the claimed identity headers and the authenticated payload, rather than trusting `shopify_header("shop-domain")` unconditionally.

### Proof of Concept
1. Attacker or intermediary captures a legitimately-signed webhook payload/HMAC pair originally sent for `shop-a.myshopify.com`.
2. Attacker replays the same raw body and HMAC to the host app's webhook endpoint but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` still validate successfully via `HmacValidator.validate`, because only `@raw_body` is checked [6](#0-5) .
4. `Request#shop` now returns `shop-b.myshopify.com` [2](#0-1)  even though the payload was authenticated for `shop-a`, and any host code trusting `request.shop` for tenant selection acts on the wrong tenant's data/session.

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

**File:** lib/shopify_api/webhooks/request.rb (L50-59)
```ruby
        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
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
