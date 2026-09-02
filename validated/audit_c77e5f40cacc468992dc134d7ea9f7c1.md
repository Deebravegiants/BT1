Found the exact analog described in the report's bug class.

### Title
Webhook `shop` identity is read from an HTTP header not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, but exposes `shop` (and `topic`, `api_version`, `webhook_id`) from separate HTTP headers that are never included in the signature. `Registry.process` validates the HMAC and then blindly trusts `request.shop` to attribute the webhook payload to a shop/tenant, handing that value straight to the app's handler as the tenant identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#hmac` is derived purely from the `hmac-sha256` header [2](#0-1) . The `shop` accessor, however, comes from the `shop-domain` header, which is not part of the signed string at all [3](#0-2) . `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` (which only checks `hmac` against `to_signable_string`, i.e., the body) and then immediately forwards `request.shop` to the registered handler as `WebhookMetadata#shop`, treating it as the authenticated tenant identifier [4](#0-3) . `Utils::HmacValidator.validate` confirms it only compares `verifiable_query.hmac` against a signature computed from `verifiable_query.to_signable_string` [5](#0-4) .

This breaks the identity binding: `hmac_covers(bytes) == body` but `shop_used_for_tenancy == shop-domain header`, i.e. the equality `bytes_verified == bytes_used_for_tenant_attribution` does not hold. Any request forwarder, proxy, load balancer, or man-in-the-middle capable of relaying an otherwise-valid Shopify webhook body/HMAC pair (e.g., a legitimate webhook for Shop A that the attacker can replay or a proxy that lets the attacker rewrite headers before they reach the app) can substitute an arbitrary `x-shopify-shop-domain` / `shopify-shop-domain` header value while keeping the original body and HMAC intact, since the header is never part of what's signed.

### Impact Explanation
If a host application (using this gem as documented, i.e. calling `Registry.process(request)` and trusting `data.shop` in its handler, exactly as shown in the gem's own tests) uses `WebhookMetadata#shop` to select which merchant/tenant record to update, an attacker who can influence only the `shop-domain` header (not the signed body) can cause the webhook payload to be attributed to a different shop than the one that actually sent/owns it — a cross-tenant data-integrity/confusion issue. This matches the "Critical - cross-tenant access" impact category, since the tenant boundary (`shop`) is exactly the field this report's bug-class targets: a value acted upon by the app but not bound by the cryptographic check.

### Likelihood Explanation
Likelihood depends on whether an intermediary between Shopify and the host app (reverse proxy, CDN, custom ingress, or a misconfigured multi-tenant routing layer) can be induced to rewrite/duplicate the `shop-domain` header while the body and HMAC pass through unchanged. This is not exploitable by a pure internet attacker with no positioning, but it is a real, demonstrable weakness in the gem itself: the gem-provided `Request`/`Registry` abstraction never asserts that `shop` is covered by the same trust boundary as `hmac`, unlike `AuthQuery`/`HmacValidator` used for OAuth callbacks, where `shop` **is** included in `to_signable_string` [6](#0-5) . The inconsistency between the two `VerifiableQuery` implementations (`AuthQuery` binds `shop`; `Webhooks::Request` does not) shows this is a root-cause gap in the webhook path specifically.

### Recommendation
Extend `Webhooks::Request#to_signable_string` (or the signature comparison) so that `shop`, `topic`, `api_version`, and `webhook_id` are cryptographically bound the same way OAuth's `AuthQuery` binds `shop`/`host`/`code`. At minimum, canonicalize and include the `shop-domain` header value in the HMAC input, or require the caller to independently verify the `shop` against a known, previously-registered value before trusting it as tenant identity in `WebhookMetadata`.

### Proof of Concept
```ruby
raw_body = '{"id":1}'
real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# Attacker/relay changes only the shop-domain header; body+hmac stay valid because
# `to_signable_string` never included shop-domain.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(real_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # swapped from the real sender's shop
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => handler receives WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id"=>1})
#    even though the HMAC only ever certified the body, not the shop.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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
