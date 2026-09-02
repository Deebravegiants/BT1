### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` (tenant identity) used to dispatch the webhook to the host application's handler is read from an HTTP header that is never included in the signed content. This breaks the intended binding: `hmac_verified_bytes == raw_body` while `tenant_identity_used_for_dispatch == shop_domain_header`, i.e. the identity actually authenticated by the HMAC does not equal the identity the gem hands to the application.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop` is derived from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is part of `@headers`, not `@raw_body`: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string` and compares against the HMAC header — so it cryptographically verifies only the body bytes, never the header set: [4](#0-3) 

`Registry.process` trusts the HMAC check and then passes the unauthenticated `request.shop` header value straight into `WebhookMetadata`, which the host application's handler uses as the tenant key: [5](#0-4) 

Because the shop-domain header sits outside the HMAC-signed payload, an unprivileged internet user who controls any single shop that has this app installed can capture one of their own legitimate webhook deliveries (valid body + valid HMAC, since the shared `client_secret`/API secret signs every merchant's webhooks identically) and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to an arbitrary victim shop domain. `Utils::HmacValidator.validate` still returns `true` because it only re-computes the signature over the untouched body, so `Registry.process` proceeds and delivers the (attacker-chosen) `shop` value to the handler as if Shopify itself had sent that webhook for the victim's store.

### Impact Explanation
This lets an attacker who is merely one of the app's own installed merchants make the application process and store webhook data under a shop identity it never authenticated — the classic cross-tenant identity confusion pattern called out by the rules ("a field acted on but not covered by the HMAC"). Any host application logic that keys persistence, entitlements, or business actions off `WebhookMetadata#shop` (the documented and expected use of this field) can be tricked into attributing attacker-supplied webhook content to a different tenant, i.e. cross-tenant access.

### Likelihood Explanation
Medium-to-High: the attacker only needs a normal merchant install of the app (no leaked secrets, no privileged access) and the ability to POST directly to the app's public webhook URL with modified headers, both of which are realistic for any app that accepts webhooks over HTTP.

### Recommendation
Bind the tenant identity into the authenticated material: either include the `shop-domain` (and `topic`, `webhook-id`) header values in the string that is HMAC-verified, or have `Registry.process` cross-check `request.shop` against a shop value independently known/authorized for that webhook subscription before dispatching to the handler, rather than trusting an unauthenticated header field for tenant routing.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; receive a legitimate webhook POST with body `B` and header `x-shopify-hmac-sha256: H` (valid signature over `B` using the app's shared secret) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay the exact same request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com`, keeping body `B` and header `H` untouched.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim.myshopify.com", "x-shopify-hmac-sha256" => H})` is constructed; `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and returns `true`.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body:, ...)`, so the application processes attacker-controlled data under the victim shop's identity despite Shopify never sending this webhook for that shop.

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
