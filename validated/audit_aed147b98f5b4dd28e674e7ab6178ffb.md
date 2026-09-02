Found a legitimate analog in the webhook request verification path, structurally identical to the reported bug class: a field that off-chain/consuming logic trusts for shop/tenant identification is not covered by the HMAC signature.

### Title
`ShopifyAPI::Webhooks::Request#shop` (the tenant identity) is read from an unauthenticated header and is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request` computes its HMAC-verifiable payload (`to_signable_string`) from only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from HTTP headers that are never included in the signed material.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) , and `HmacValidator.validate`/`validate_signature` verify only that this signable string produces the expected HMAC using `Context.api_secret_key` [2](#0-1) . Meanwhile `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are read straight from the `shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, and `shopify-webhook-id` headers, with no cryptographic binding to the body or to each other [3](#0-2) . The constructor only checks that these headers are *present*, not that they are authenticated [4](#0-3) .

This mirrors the report's bug class exactly: an attacker-controllable field (`payload_type` in the Cairo report; `shop`/`topic`/headers here) is consumed by downstream logic (event emission there; webhook routing/tenant identification here) but is excluded from the message-integrity check (`message_hash` there; `to_signable_string`/HMAC here). The binding that should hold is:
`shop_authenticated_by_hmac == shop_used_for_tenant_routing`
but the gem only enforces `hmac(raw_body) == received_hmac`, leaving `shop` (and `topic`) unauthenticated and swappable independently of the signed body.

### Impact Explanation
Any consuming application built on this gem's `Webhooks::Request`/registry (documented usage pattern: `HmacValidator.validate(request)` then dispatch by `request.topic`/`request.shop`) will treat the header-supplied `shop` as trustworthy identity for a verified webhook simply because the body's HMAC checked out. Since `shop` is not part of the signed content, an attacker who obtains any single valid `(raw_body, hmac)` pair (e.g., from their own shop's legitimate webhook, or a body whose HMAC computation is otherwise satisfiable) can resend it with an arbitrary `shopify-shop-domain` header. The host application's webhook handling will process the payload as if it belongs to a victim shop, causing cross-tenant data confusion/injection — matching the "High" impact category of scope/tenant-identity bypass via an unauthenticated but trusted field.

### Likelihood Explanation
Exploitability requires the attacker to possess at least one valid `(body, hmac)` pair signed with the app's `client_secret` for *some* webhook (which Shopify legitimately delivers per-merchant), then replay it toward the app's public webhook endpoint with a forged `shop-domain` header. This is realistic wherever an app's webhook consumer (following this gem's documented pattern) uses `Request#shop` for tenant lookup/routing without independently re-validating the shop against its own installed-shop records.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (all header-derived fields consumed by application logic) in `to_signable_string`, or otherwise cryptographically bind them to the verified body, so `HmacValidator.validate` fails if any of these identity/routing fields are altered independently of the signed payload.

### Proof of Concept
1. Attacker's own shop receives a legitimate webhook: body `B`, header `shopify-hmac-sha256: H`, header `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical `B`/`H` to the victim app's webhook endpoint but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate(request)` calls `request.to_signable_string`, which returns only `B` [1](#0-0) ; the computed HMAC over `B` still matches `H`, so validation passes.
4. The application, trusting `request.shop` [5](#0-4) , processes `B`'s content under `victim-shop.myshopify.com`'s tenant context despite the payload never having been signed for that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

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

        @headers = headers
        @raw_body = raw_body
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
