Found the key issue: `Webhooks::Request#shop` reads the shop identity from the `X-Shopify-Shop-Domain` header, but `to_signable_string` (used by `HmacValidator`) only signs `@raw_body` — the `shop` value is never part of the HMAC-verified bytes.

### Title
Webhook shop-domain header is trusted for tenant routing without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor read straight from the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) HTTP header, while the HMAC that `Utils::HmacValidator` verifies is computed only over the raw request body via `to_signable_string`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate`/`validate_signature` verify the HMAC solely against that signable string and the `hmac` field [2](#0-1) . The `shop` value used to identify which merchant/tenant a webhook belongs to is pulled directly from the `shop-domain` header without being included in the signed bytes [3](#0-2) . The identity binding that should hold is: `HMAC(raw_body, client_secret) valid` ⇒ `shop header == body's true origin shop`. Because the header is not part of the signed data, that equality does not hold — the HMAC only proves the body bytes are authentic, not that the accompanying `shop-domain` header corresponds to the same tenant. This mirrors the report's bug class: "bytes verified" (the raw body) diverge from "bytes acted on" (the shop header used for tenant dispatch/session lookup), i.e., a field acted on but not covered by the HMAC.

### Impact Explanation
If a host application (as the gem's documented API encourages, e.g. via `Webhooks::Registry`) uses `request.shop` to look up which merchant's session/access token to associate with the webhook payload, an attacker who can influence or replay the `shop-domain` header (e.g., through a proxy that forwards attacker-controlled headers, or a race where legitimate signed payload from shop A is replayed with header set to shop B) could get the payload processed under the wrong tenant's context — a cross-tenant confusion. However, exploitation requires: (a) a genuinely Shopify-signed body (attacker cannot forge new bodies without `client_secret`), and (b) the host app trusting the header for routing without independently cross-checking it against the body's own `shop_domain` field or session lookup by API key. This is a real gap in the identity binding this gem provides, though full compromise depends on host-app behavior that the gem does not itself validate.

### Likelihood Explanation
Moderate-to-low: exploitation isn't achievable by an anonymous attacker forging a webhook from scratch, since the HMAC still requires knowledge of `client_secret` to produce a validating signature over any body. The realistic path is header manipulation/mismatch on an otherwise-legitimately-signed request (e.g., a malicious reverse proxy, header injection point, or webhook replay across differently-configured shops) where the body is valid for shop A's secret (if shared) but the header claims shop B. This is a narrower likelihood than the original SC report but represents the same class of "verified bytes ≠ acted-upon bytes" flaw the prompt targets.

### Recommendation
Include the shop-domain (and topic/api-version) header values in the signable string used for HMAC verification, or require the gem's `Webhooks::Registry` handlers to cross-validate `request.shop` against the shop segment embedded in the verified body (when present) before using it for tenant lookup, so tenant identity is derived only from HMAC-covered bytes.

### Proof of Concept
1. Attacker (or a compromised intermediary) crafts an HTTP request to the app's webhook endpoint with a body/HMAC pair that is valid for `client_secret` (e.g., a real webhook delivery captured and replayed, or one relayed by an unstrusted proxy), but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` instead of the domain the payload actually originated from.
2. `Webhooks::Request.new` accepts the request because the three required headers (`topic`, `hmac-sha256`, `shop-domain`) are merely present, not cross-validated [4](#0-3) .
3. `HmacValidator.validate(request)` calls `to_signable_string`, which returns only `@raw_body`, so the HMAC check passes regardless of what `shop-domain` header value was supplied [1](#0-0) [5](#0-4) .
4. The host application, following the gem's documented pattern, reads `request.shop` to route/process the webhook under that tenant's session — but that value was never authenticated by the HMAC, only the body was.

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
