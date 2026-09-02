### Title
Webhook `shop-domain` header is trusted for tenant routing but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then forwards the attacker-controlled `shop-domain` header to the app's handler as the tenant identity, without that header ever being covered by the signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signable string [2](#0-1) . `HmacValidator.validate` computes the signature purely from `to_signable_string` and compares it to the `hmac` field [3](#0-2) . `Registry.process` treats a passing `HmacValidator.validate(request)` check as full authentication of the webhook, then immediately uses `request.shop` as the tenant identity passed to the app's handler as `WebhookMetadata` [4](#0-3) .

This breaks the equality the HMAC is supposed to enforce: `shop_authenticated == shop_used_for_tenant_routing`. Because `shop` is a header field entirely outside the signed byte range (only `raw_body` is signed), an attacker who can produce (or replay/observe) *any* validly-HMAC'd webhook body — e.g., from their own installed/free-tier store, from a public webhook payload, or by intercepting one destined for their own tenant — can resubmit that exact body with the `hmac` header untouched but the `shop-domain` header rewritten to an arbitrary victim shop domain. The signature still validates because the signature only ever covered the body bytes, not the shop claim, so `Utils::HmacValidator.validate` returns `true` for a request now falsely attributed to a different shop.

### Impact Explanation
This is a cross-tenant identity-spoofing primitive: the merchant-identity binding (`shop`) that host applications rely on to select the correct tenant/session/data record is derived from bytes that are not authenticated by the same mechanism that gates "is this really Shopify" for the request. Any host application using `Registry.process`/`WebhookMetadata#shop` to key updates in a database, invalidate sessions, or perform tenant-scoped side effects can be made to act on the wrong merchant's tenant using an attacker-supplied `shop` value while the library still reports the request as HMAC-valid. This matches the report's High-impact category of a scope/identity check that answers permissively across a tenant boundary.

### Likelihood Explanation
Exploitability only requires (a) any body+HMAC pair the attacker can obtain honestly (e.g. from their own store's webhook deliveries, which any developer/merchant can generate at will without needing the app's `client_secret`), and (b) the ability to POST arbitrary headers to the app's webhook endpoint, which is a normal unauthenticated HTTP capability for any internet-reachable webhook receiver. No possession of `api_secret_key` or any privileged credential is required — the attacker never needs to forge a signature, only to relabel the tenant while reusing a legitimately-signed body.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) values in the HMAC-signed payload used for verification, or otherwise cryptographically bind the `shop-domain` header to the signed body before `Registry.process` trusts `request.shop` for tenant routing. At minimum, document/require callers to independently corroborate `request.shop` against an already-authenticated session before using it as a tenant key.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery: body `{"id":123}` with a correctly computed `x-shopify-hmac-sha256` header (computed by Shopify using the app's real secret over that body) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same body and `hmac` header to the app's webhook endpoint but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `Webhooks::Request.new` parses this into a `Request` whose `to_signable_string` is still the same raw body [1](#0-0) ; `HmacValidator.validate` recomputes the HMAC over the same body/secret and it matches [3](#0-2) .
4. `Registry.process` treats the request as valid and calls the app handler with `shop: request.shop == "victim.myshopify.com"` [5](#0-4) , causing the app to apply the webhook payload against the victim tenant even though it originated from, and was signed for, the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
