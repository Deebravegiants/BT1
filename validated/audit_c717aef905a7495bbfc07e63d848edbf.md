### Title
Webhook `shop` and `topic` fields are not covered by the HMAC signature, allowing shop/topic spoofing on a replayed payload - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` as plain HTTP header reads, but the HMAC signature that this gem verifies (`to_signable_string`) only covers the raw request body, not these headers. Any component that trusts `Request#shop` as an authenticated tenant identifier is relying on a value the gem never actually binds to the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC purely from `to_signable_string` and compares it to the `hmac` header: [2](#0-1) 

But `Request#shop` and `Request#topic` are read directly from the `x-shopify-shop-domain` / `x-shopify-topic` headers, which are never part of the signed bytes: [3](#0-2) 

This is exactly the "bytes verified versus bytes parsed" binding failure: the gem verifies the raw body bytes cryptographically, but the shop/topic identity that host applications use to route the webhook to the correct tenant's session/data is parsed from unauthenticated headers. Compare this to the OAuth callback path, where `shop` is explicitly included in the HMAC-signed content via `AuthQuery#to_signable_string`: [4](#0-3) 

The equality that should hold is: `shop_bound_by_hmac == shop_used_for_tenant_routing`. For OAuth this equality holds (`shop` is inside `to_signable_string`). For webhooks it does not — `Webhooks::Request.shop` is entirely outside the signed payload.

### Impact Explanation
If an attacker captures one legitimate, validly-signed webhook body+hmac pair (e.g. from network logs, a misconfigured proxy, or a shared/public endpoint), they can resend that exact body and hmac while substituting a different `x-shopify-shop-domain` header. `HmacValidator.validate` will still return `true` because the body/hmac pair is untouched, yet `Request#shop` will report an arbitrary shop of the attacker's choosing. Any host application (as this gem's documented pattern instructs) that uses `Request#shop` to look up the target tenant's session before validating and processing a webhook will process/attribute data under the wrong shop — a cross-tenant confusion driven entirely by a value the gem's own HMAC verification never protects.

### Likelihood Explanation
Requires the attacker to have obtained one legitimate signed webhook payload for any shop (their own store subscribing to a webhook is a completely legitimate, low-privilege way to obtain one), after which they can replay it indefinitely with an arbitrary spoofed `shop`/`topic` header, since `Request.new` performs no binding between headers and body content.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed content (`to_signable_string`), or otherwise cryptographically bind these header-derived fields to the verified body, so `HmacValidator.validate` cannot succeed for a payload whose asserted shop/topic differs from what Shopify actually signed.

### Proof of Concept
1. Register a webhook for your own store; capture a legitimate request with headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: T`, and body `B`.
2. Build `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers_with_shop_domain_changed_to("victim-shop.myshopify.com"))`.
3. Call `ShopifyAPI::Utils::HmacValidator.validate(request)` — it returns `true` because `to_signable_string` is unchanged (`B`), even though `request.shop` now reports `"victim-shop.myshopify.com"`. [5](#0-4)

### Citations

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
