### Title
Webhook shop-domain identity not covered by HMAC signature, enabling cross-tenant webhook impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that host applications use to identify which merchant/tenant a webhook event belongs to, but this value is read from an HTTP header that is **not** part of the data covered by the HMAC signature validated by `Utils::HmacValidator`. Any party who can obtain one legitimately-signed webhook payload (e.g., by installing the app on their own, attacker-controlled development/trial store — an unprivileged action) can replay that exact signed body to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`) header to claim the event originated from a different, victim shop. The signature will still validate because it only signs the raw body, not the shop/topic headers that establish which tenant the event applies to.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`Webhooks::Request#shop` (the tenant identity used by the host app to route/attribute the webhook) is read from a header that is completely outside that signed string: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes and compares the HMAC over `to_signable_string` (i.e., the raw body), never over the shop/topic headers: [3](#0-2) 

This breaks the identity binding: `HMAC-verified(raw_body) ≠ authenticated(shop-that-the-app-attributes-this-body-to)`. The gem's own `HmacValidator.validate(request)` call, which host applications are documented/expected to use as the sole authenticity check for a webhook, gives no assurance that `request.shop` (or `request.topic`) matches the shop the body was actually generated for. The same `hmac-sha256` header/body pair remains valid regardless of what is put in `shopify-shop-domain` and `shopify-topic` headers, because those fields are never fed into the signature computation.

### Impact Explanation
An attacker who operates their own Shopify development/trial store (no privileged credentials, no access token, no `client_secret` required — installing the app on a store they control is an unprivileged action available to any internet user) can:
1. Trigger a legitimate webhook event on their own store (e.g., an `orders/create` or `app/uninstalled` event), capturing the exact `raw_body` and its valid `hmac-sha256` signature.
2. Replay that same body/HMAC pair to the target app's webhook endpoint, but with the `X-Shopify-Shop-Domain` header changed to a victim merchant's `myshopify.com` domain.
3. Because `HmacValidator.validate` only checks the body signature and never binds it to the shop header, the host application built on this gem will treat the payload as an authentic event for the victim's shop — this is cross-tenant confusion: attacker-controlled data is attributed to another tenant's session/store. Depending on how the host app processes the webhook (e.g., updating stored order data, disabling the app, deleting resources, or acting on `app/uninstalled`/`shop/redact` for the wrong tenant), this can result in unauthorized cross-tenant state changes or data exposure, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that relies on `ShopifyAPI::Webhooks::Request#shop` (or `#topic`) in combination with `HmacValidator.validate` as its complete authenticity check, since that is the documented verification path exposed by this gem. Obtaining a valid signed sample requires nothing more than operating one's own store and installing the target app — an unprivileged, self-service action, not requiring the app's `client_secret`, an access token, or any credential belonging to another party.

### Recommendation
Include the shop domain and topic headers as part of the value covered by HMAC verification, or otherwise require the host application to independently authenticate the shop the webhook applies to (rather than trusting `request.shop`) before using it as a tenant key. At minimum, the gem should document clearly that `request.shop` and `request.topic` are unauthenticated inputs even after `HmacValidator.validate` succeeds, so implementers do not use them as tenant-identity binding.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and lets it fire a real webhook (e.g. `orders/create`). Capture the request body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic: orders/create` (unchanged or altered)
3. The host app calls `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` then `ShopifyAPI::Utils::HmacValidator.validate(request)`, which returns `true` because it only checks `HMAC(secret, B) == H`.
4. The host app proceeds to treat `request.shop` (`victim-shop.myshopify.com`) with `request.parsed_body` (attacker's own order/data payload) as an authentic event for the victim tenant — confirming the cross-tenant identity-binding break.

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
