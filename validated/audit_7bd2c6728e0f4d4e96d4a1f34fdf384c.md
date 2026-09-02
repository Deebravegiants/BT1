### Title
Webhook shop-domain attribution is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook only by verifying an HMAC over the raw request body, then dispatches to the app's handler using the `shop` value taken from the unauthenticated `x-shopify-shop-domain` (or `shopify-shop-domain`) header. Because the signed bytes never include the shop domain, and because a single `api_secret_key` is shared by every merchant that installs the app, any party who can obtain one genuinely-signed webhook body (e.g. by installing the app on their own store) can replay that same body/HMAC pair while substituting an arbitrary victim shop domain in the header. The HMAC check passes, and the handler processes the payload as if it belonged to the victim shop.

### Finding Description
The `HmacValidator.validate` implementation computes and compares the HMAC over `verifiable_query.to_signable_string` only: [1](#0-0) 

For webhooks, `to_signable_string` returns exclusively the raw JSON body, while `shop` is read straight from an HTTP header with no cryptographic binding to that body: [2](#0-1) 

`Registry.process` uses this unauthenticated header value directly as the tenant identifier passed to the app's handler, after only checking the HMAC on the body: [3](#0-2) 

The identity binding that should hold is:
```
hmac_verified_bytes.shop == dispatched_metadata.shop
```
but in reality:
```
hmac_verified_bytes = raw_body            (never includes shop)
dispatched_metadata.shop = header["x-shopify-shop-domain"]  (never verified)
```
Since `api_secret_key` is the same secret for every store that installs a given app, any user who legitimately installs the app on their own shop receives a validly-HMAC-signed webhook body from Shopify. That exact `(raw_body, hmac)` pair remains valid under `HmacValidator.validate` no matter what `shop` header accompanies it, because the shop header was never part of the signed content. An attacker can therefore submit that same body to the app's webhook endpoint while setting `x-shopify-shop-domain` to a victim merchant's domain, and the library will report the request as valid and hand the handler data claiming it originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the library is supposed to enforce for webhook processing: it lets an unprivileged actor who merely has their own (or any) legitimate Shopify install of the app forge webhook events attributed to a different, victim shop. Any host application that trusts `WebhookMetadata#shop` for per-tenant record updates, deduplication, GDPR/data-erasure flows, or billing/inventory sync could have data written, deleted, or exposed under the wrong shop's identity — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only: (1) knowledge of the target app's webhook endpoint (public), and (2) the ability to obtain one genuinely-signed webhook body for *any* shop using the app, which any developer/attacker can trivially do by installing the app for free on a store they control. No access token, `client_secret`, or privileged access to the victim is needed — this fits an "unprivileged internet user" threat model.

### Recommendation
Bind the shop identity to the signed content rather than trusting the header independently. Options: 
- Include the shop domain in the value that is HMAC-verified (e.g., verify it as part of a composite signable string, or independently confirm the `shop` header value is consistent with data already known to be scoped to that shop, such as looking up the webhook by `webhook_id` registered specifically for that shop).
- At minimum, document/require host applications to independently correlate the resource IDs in the body with the shop the app has on record, rather than trusting the header outright once HMAC validation passes.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Shopify sends a legitimately signed webhook, e.g. `orders/create`, with:
   - body: `{"id": 123, ...}`
   - header `x-shopify-hmac-sha256`: valid HMAC over the body using the app's shared `api_secret_key`
   - header `x-shopify-shop-domain`: `attacker.myshopify.com`
3. Attacker replays the exact same `raw_body`/`hmac` pair to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers, `HmacValidator.validate` succeeds because it only checks the (unchanged) body against the (unchanged, valid) HMAC: [4](#0-3) 
5. The host app's handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes the attacker's payload as if it belonged to the victim, breaking tenant isolation.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```
