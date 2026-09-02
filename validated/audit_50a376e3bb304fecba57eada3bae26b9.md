### Title
Webhook shop-domain header is not bound by the HMAC signature, enabling cross-tenant webhook confusion - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity used by the host application from the `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that this gem validates only covers the raw request body. The header that identifies *which tenant* the webhook belongs to is never included in the signed bytes, breaking the equality `shop_used_for_tenant_routing == shop_bound_by_hmac`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#hmac` are both derived from HTTP headers, but only `hmac` participates in verification — `shop`, `topic`, `api_version`, and `webhook_id` are read straight from headers with no cryptographic binding to the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature only from `to_signable_string` (i.e., the raw body) and compares it against the `hmac-sha256` header: [3](#0-2) 

Contrast this with the OAuth callback path, where the equivalent field (`shop`) *is* included in the signed string, so `AuthQuery#shop` is cryptographically bound to the HMAC before being trusted: [4](#0-3) 

For webhooks there is no such binding. A request whose body was legitimately signed by Shopify for shop A can have its `X-Shopify-Shop-Domain` header value swapped to shop B (or any attacker-chosen string) without invalidating the HMAC check, since the header is never part of the signed bytes. Any host application that follows this gem's documented pattern of calling `Utils::HmacValidator.validate(request)` to authenticate the webhook and then uses `request.shop` to select which merchant's local session/data the body applies to (exactly the pattern described in this project's own webhook docs) will process body content under the wrong tenant.

### Impact Explanation
This is a cross-tenant identity-binding break: the field consumed to route/attribute the webhook to a merchant (`shop-domain` header) is disjoint from the field actually protected by the HMAC (`raw_body`). An attacker who can influence or replay the header of an otherwise validly-signed request (e.g., via a proxy, load balancer misconfiguration, or any transport that lets header values be attacker-supplied while body+signature are replayed) can cause a webhook payload to be attributed to a different shop than the one Shopify actually signed it for, leading to cross-tenant data confusion. This matches the "Critical - cross-tenant access" impact category, since the gem's own verification primitive gives applications false confidence that `shop` is authenticated.

### Likelihood Explanation
Exploitation requires an attacker to control or manipulate the `shop-domain` header on a request path (e.g., a shared/replayed body with attacker-supplied headers, header injection at a proxy, or any environment where headers aren't as strictly bound to TLS/connection identity as the signed body is). This is a narrower prerequisite than a straightforward unauthenticated bypass, but it is a genuine gap in the library's own guarantee: nothing in `Request` or `HmacValidator` ties `shop` to the signature, so the library itself does not prevent this even when the host app follows the documented usage.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header value into the signed material that `HmacValidator` checks, or have `Request` re-derive/validate the shop identity from data contained within the signed body rather than trusting the header independently of the HMAC. At minimum, document prominently that `Request#shop` is not covered by the HMAC and must not be used as an authenticated tenant identifier without additional verification (e.g., cross-checking against a shop already known from an established session).

### Proof of Concept
```ruby
raw_body = '{"id":1}'
secret = ShopifyAPI::Context.api_secret_key
valid_hmac = Base64.strict_encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, raw_body)
)

# Attacker-controlled shop-domain header, body/hmac unchanged
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # swapped, not signed
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Utils::HmacValidator.validate(request) # => true, even though shop-domain was not part of what was signed
request.shop # => "victim-shop.myshopify.com" (unauthenticated value trusted by the app)
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
