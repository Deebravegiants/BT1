### Title
Webhook `shop` and `topic` identity fields are read from unauthenticated headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` for webhook HMAC verification, but the signable string used for verification is only the raw request body, while the `shop` (tenant identity) and `topic` fields that a host application uses to route/scope the webhook are taken from HTTP headers that are never included in that signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `#shop` and `#topic` — the values a host application relies on to determine which merchant/tenant a webhook belongs to and which handler to dispatch to — are read directly from the `shopify-shop-domain` and `shopify-topic` headers, with no cryptographic binding to those values: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it against the `hmac-sha256` header value: [3](#0-2) 

This breaks the identity binding: `shop-header == shop-that-signed-the-payload`. Shopify's HMAC signature only proves the *body bytes* were signed with the app's `client_secret` (i.e., proves the payload came from Shopify for *some* webhook), it proves nothing about which shop or topic header accompanied that body. Because headers are fully attacker-controllable metadata sitting outside the signed envelope, any entity capable of replaying (or man-in-the-middling at the HTTP layer, e.g. a reverse proxy, shared load balancer, or a party that intercepts one legitimate webhook delivery for their own shop) can take a validly-signed raw body originally delivered for shop A/topic X and re-submit it to the app's webhook endpoint with `shopify-shop-domain: shop-B` and/or `shopify-topic: other/topic`. `Utils::HmacValidator.validate` will report the payload as valid because it never inspected the headers, and the host application (using this gem's documented `Request#shop`/`Request#topic` API) will process the (attacker's own, but validly-signed) body as if it belongs to a different tenant or a different event type.

### Impact Explanation
If a merchant (an unprivileged entity relative to other tenants of a multi-tenant app) can obtain any one validly-HMAC-signed webhook body for their own shop — which every app installation naturally receives — they can resubmit it with a forged `shop-domain` header pointing at a victim shop and/or a forged `topic` header. Any host application that trusts `Request#shop` (as documented/intended by this gene) to select or scope tenant state before processing `parsed_body` will act on attacker-supplied data under another tenant's identity: this is cross-tenant access, one of the specified Critical impacts.

### Likelihood Explanation
The attacker needs only to control or record one legitimately-delivered webhook (trivial — they operate an installed instance of the app for their own shop) and then be able to resubmit an HTTP request with modified headers and the identical, unmodified body to the app's public webhook endpoint. No possession of `client_secret`, access tokens, or any privileged credential is required — only standard use of the API as an ordinary app merchant/tenant.

### Recommendation
Include `shop`, `topic`, and any other identity-bearing header consumed by `Webhooks::Request` in the HMAC-covered signable material (or otherwise cryptographically bind them, e.g. by validating the header values are consistent with a signed field embedded in the payload) instead of relying solely on the raw body for `to_signable_string`.

### Proof of Concept
1. App merchant "Attacker" installs the app on `attacker-shop.myshopify.com`; Shopify delivers a legitimate webhook with a body `B` and a correctly computed `hmac-sha256` header `H = HMAC(client_secret, B)`, plus headers `shopify-shop-domain: attacker-shop.myshopify.com` and `shopify-topic: orders/create`.
2. Attacker captures this full raw request (body `B` and header `H`).
3. Attacker resubmits an HTTP POST to the app's public webhook endpoint using the same body `B` and the same `hmac-sha256: H`, but with headers changed to `shopify-shop-domain: victim-shop.myshopify.com` and/or `shopify-topic: customers/data_request`.
4. The app constructs `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` and calls the gem's HMAC validation; since `to_signable_string` returns only `B`, verification succeeds (`Utils::HmacValidator.validate` returns `true`) despite the shop/topic mismatch.
5. The host application, trusting `request.shop` to be `"victim-shop.myshopify.com"`, processes the attacker's payload as though it were a legitimate event for the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
