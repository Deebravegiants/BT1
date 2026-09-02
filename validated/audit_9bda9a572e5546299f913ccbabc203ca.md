### Title
Webhook `shop-domain` header is trusted for tenant routing but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The yVault report is a class of bug where a value that is *acted upon* is not the same value that was *cryptographically bound/verified*. In `ShopifyAPI::Webhooks::Request`, the HMAC signature only authenticates the raw JSON body, while the `shop` (tenant identifier) and `topic` used for routing and business logic come from unauthenticated HTTP headers.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the signature exclusively against that signable string [2](#0-1) . The `shop` value, however, is read directly and unauthenticated from the `shopify-shop-domain`/`x-shopify-shop-domain` header: `def shop; T.cast(shopify_header("shop-domain"), String); end` [3](#0-2) . The `topic` and `webhook_id` values are likewise taken from headers with no cryptographic binding [4](#0-3) .

The binding that should hold is: `shop_used_for_tenant_dispatch == shop_bound_by_hmac(secret, body)`. Here it does not — the HMAC only proves "this body's bytes were signed by someone holding `client_secret`"; it proves nothing about which shop or topic that body belongs to, because those fields are never part of `to_signable_string`.

### Impact Explanation
This is the exact "field acted on but not covered by the HMAC" pattern named in the analog rules. If any mechanism allows the header values to diverge from the values Shopify intended for a given signed body (e.g., a proxy, load balancer, or any component that lets header and body be recombined, or a webhook handler that trusts headers for tenant selection before/instead of re-deriving shop from the parsed, authenticated body), tenant data could be misattributed — a cross-tenant confusion (Critical: cross-tenant access) is structurally possible because the gem's own signature-validation code (`HmacValidator.validate`, `Request#to_signable_string`) never ties `shop-domain` to the signed content at all. This is a genuine gap in this gem's own API surface (`ShopifyAPI::Webhooks::Request`/`Registry`), not merely a host-application misuse, since the gem exposes `request.shop` as the trusted routing key alongside `hmac`-validated status without linking the two.

### Likelihood Explanation
Exploitation requires a scenario where an attacker (or a compromised intermediary) can deliver a validly-HMAC'd body (still requires Shopify to have signed *some* body with the real secret) paired with attacker-chosen `shop-domain`/`topic` headers to the app's webhook endpoint — e.g., replaying a previously captured legitimate webhook body for shop A while substituting headers for shop B, since nothing in this gem ties the header to the signed payload. This does not require knowledge of `client_secret`; it only requires access to one legitimately-signed webhook body (which is regularly delivered to internet-facing endpoints) and the ability to set arbitrary headers on a request to the app's public webhook endpoint. Likelihood is therefore plausible for apps that use `request.shop`/`request.topic` for dispatch logic (as the built-in `Registry.process` does), which is the gem-documented usage pattern.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the signed material, or otherwise verify them against the authenticated body (e.g., require the payload's own `shop_id`/`shop_domain` field, if present in the JSON, to match the header value before dispatch). At minimum, document and enforce that `shop`/`topic` header values must never be trusted for authorization decisions independent of body content, and consider extending `to_signable_string` to include a canonicalized header set that Shopify also HMACs, matching the same header+body binding model used for OAuth's `AuthQuery#to_signable_string`.

### Proof of Concept
1. Capture (or have Shopify deliver) one legitimate webhook POST for shop `victim-shop.myshopify.com`: valid `X-Shopify-Hmac-Sha256`, `X-Shopify-Topic`, `X-Shopify-Shop-Domain: victim-shop.myshopify.com`, and raw JSON body `B`.
2. Resend the same raw body `B` and same valid HMAC value to the app's webhook endpoint, but change the header `X-Shopify-Shop-Domain` to `attacker-shop.myshopify.com` (and/or `X-Shopify-Topic` to a different registered topic).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers)` is constructed; `HmacValidator.validate(request)` still returns `true` because `to_signable_string` only depends on `@raw_body`, which is unchanged [1](#0-0) [5](#0-4) .
4. `Registry.process` (or any handler using `request.shop`/`request.topic`) will treat the payload as authentically belonging to `attacker-shop.myshopify.com`, even though only the body — not the tenant/topic association — was ever cryptographically verified.

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
