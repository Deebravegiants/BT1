### Title
Webhook `shop` Identity Is Not Bound by the HMAC Signature, Enabling Cross-Tenant Webhook Forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, but the `shop` (tenant) identity used by host applications to route/process the webhook is read from an unauthenticated HTTP header. This breaks the binding `verified_bytes == identity_bytes` and lets an attacker who controls one legitimate shop replay a genuinely-signed webhook body while claiming it originated from a different, victim shop.

### Finding Description
`Request#hmac` and `Request#to_signable_string` compute/verify the signature strictly over `@raw_body`: [1](#0-0) [2](#0-1) 

Meanwhile `Request#shop`, the value applications use to identify which merchant/tenant the webhook belongs to, is taken directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, with no cryptographic linkage to the signed body: [3](#0-2) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` (the raw body) against the HMAC; it never incorporates `shop`, `topic`, or any other header into the signed material: [4](#0-3) 

Because the app's `api_secret_key` (webhook signing secret) is shared across *all* shops that install the app, any shop is able to generate genuinely HMAC-valid webhook deliveries for events it triggers on its own store. Since the `shop-domain` header sits entirely outside the HMAC's scope, an attacker who controls their own installation can take a body+HMAC pair that Shopify legitimately produced for their own shop and resubmit it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a victim shop. `Request#hmac` will still validate successfully because the signature only ever covered `@raw_body`.

This is a direct analog to the report's root cause: a field that is acted upon (here, the `shop` used to select the tenant/session that processes the webhook payload) is not covered by the authentication mechanism (here, the HMAC), so the two can be made to diverge by an attacker who supplies inconsistent values on either side of the check.

### Impact Explanation
If the host application trusts `request.shop` to select which merchant's session/data the webhook body is applied to (the gem's own documentation and typical usage pattern for webhook processing), an attacker can forge a cross-tenant webhook: a validly-signed payload that the application believes originates from and applies to a victim shop, while the content was actually produced by the attacker's own shop. Depending on the webhook topic (e.g. `app/uninstalled`, `shop/update`, `customers/data_request`, order/product mutation webhooks), this enables cross-tenant data corruption, unauthorized state changes, or triggering of privileged app logic (like uninstall/session teardown) against a shop the attacker does not control — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high in any app that (a) accepts a webhook signed with the app's own shared secret from any of its many installed shops, and (b) uses `Request#shop` post-HMAC-validation to key persistence/session lookups without separately re-verifying shop consistency against the signed body content. An attacker needs only to be an ordinary merchant/installer of the target app (an "unprivileged internet user" from the app's perspective) capable of triggering webhook-generating events on their own store and replaying the HTTP request with a modified header — no access token, `client_secret`, or victim credentials required.

### Recommendation
Bind the tenant identity into the verified material, not just the body: incorporate the `shop-domain` (and ideally `topic`/`webhook-id`) header into `to_signable_string`, or independently verify that the `shop` claimed in the header matches the `myshopify_domain`/shop identifier embedded in the parsed body payload before trusting `Request#shop` for routing. At minimum, document prominently that `Request#shop` is unauthenticated and must not be used as the sole tenant selector without corroborating it against signed payload content.

### Proof of Concept
1. App installs `ShopifyAPI` and exposes a webhook endpoint that does:
   ```ruby
   request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
   raise "invalid" unless ShopifyAPI::Utils::HmacValidator.validate(request)
   MyApp::Tenant.find_by(shop: request.shop).apply_webhook(request.parsed_body)
   ```
2. Attacker installs the same app on `attacker-shop.myshopify.com` and triggers an event (e.g., updates a product) causing Shopify to deliver a webhook to the app with body `B` and header `X-Shopify-Hmac-SHA256: H`, where `H = HMAC_SHA256(api_secret_key, B)`.
3. Attacker intercepts/replays this HTTP request to the same endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`, keeping body `B` and `X-Shopify-Hmac-SHA256: H` unchanged.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC_SHA256(api_secret_key, B)`, which still equals `H`, so validation passes.
5. `request.shop` returns `"victim-shop.myshopify.com"` from the (unverified) header, and the app applies attacker-controlled body `B` to the victim tenant's data/session — cross-tenant forgery achieved with no credentials belonging to the victim.

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
