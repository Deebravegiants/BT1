### Title
Webhook shop-domain identity spoofing via HMAC that only covers the raw body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, while the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates covers only the raw request body. An attacker who possesses any body that is validly HMAC-signed by the app's secret (e.g. a webhook delivered to their own store, where they control installation) can replay it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, and the gem will pass that forged shop value straight through to the app's webhook handler as if it came from the victim.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `Request#shop` is read directly from the `shopify-shop-domain` HTTP header, with no cryptographic binding to the signed content: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only checks `to_signable_string` (i.e. the body) against the secret, and then unconditionally forwards `request.shop` to the registered handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm that only the `to_signable_string` value (the raw body) is what gets HMAC-checked: [4](#0-3) 

This is precisely the reported bug class: a field that is acted upon (`shop`, used to identify the tenant for the webhook handler) is not covered by the same authenticator (`hmac`) that is checked before trusting the request — an identity-binding gap analogous to `changeRecoveryAddress()` not invalidating pending signatures tied to a stale recovery address, except here the binding broken is `authenticated_body_owner == shop_claimed_in_header`.

### Impact Explanation
Any unprivileged internet user who can obtain one validly-signed webhook body for the target app (trivially achievable by installing the target app on their own store and receiving a real webhook, since HMAC secrets are shared across all shops using a given app) can forge the `shop-domain` header value and have the gem hand a spoofed `WebhookMetadata#shop` to the app's webhook handler as though it originated from an arbitrary victim shop. If the host app's handler logic keys any tenant-scoped action off of `data.shop` (a very common and gem-endorsed pattern, since `WebhookMetadata` explicitly exposes `shop` for that purpose), this enables cross-tenant impersonation of webhook delivery — e.g. triggering shop-scoped business logic, data deletion (`shop/redact`, `app/uninstalled`), or state changes attributed to a shop the attacker does not control. This maps to the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is High: the attacker only needs a legitimate app installation on any shop they control to obtain a validly HMAC-signed webhook body, then can freely replay it with a rewritten `shop-domain` header to the app's public webhook endpoint. No access token, `client_secret`, or privileged credentials are required — only knowledge of a public webhook endpoint URL and one genuine webhook delivery from the attacker's own (legitimately installed) shop.

### Recommendation
Bind the `shop` (and ideally `topic`/`api-version`) values into the HMAC-signed payload used for verification, or otherwise cryptographically bind the `shop-domain` header to the signed body (e.g. include header values in the signable string, matching how Shopify's own delivery HMAC scheme is defined) so that changing the header invalidates the signature. At minimum, cross-check `request.shop` against the shop associated with the session/API credentials expected to receive that topic before invoking the handler.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic (e.g. `app/uninstalled`) to receive a body `B` with a valid `x-shopify-hmac-sha256` header `H` (computed as `HMAC-SHA256(secret, B)`).
2. Send a POST request to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256`: `H` (unchanged, still valid since only body is signed)
   - Header `x-shopify-shop-domain`: `victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic`: unchanged
3. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`.
4. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop.

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
