### Title
Webhook Shop Attribution Not Covered by HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) exclusively from the unauthenticated `x-shopify-shop-domain` HTTP header, while the HMAC signature used to authenticate the webhook only covers the raw request body. Any attacker who possesses one valid `(body, hmac)` pair signed with the app's shared secret — trivially obtainable by installing the app on their own store and capturing a real webhook delivery — can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header for a victim shop. The signature still validates, and the handler processes the payload attributed to the victim shop.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body, never the headers: [2](#0-1) 

Meanwhile, `shop` (and `topic`, `webhook_id`, `api_version`) are read straight from headers with no binding to the signed content: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then trusts `request.shop` (and `request.topic`) to dispatch the payload to the handler as the identity of the originating store: [4](#0-3) 

The identity binding that should hold is:
`shop claimed by header == shop cryptographically bound inside the HMAC-covered content`

Because the HMAC secret (`api_secret_key`) is shared across all shops installing the same app (it is not per-shop), any merchant who installs the app can legitimately receive a webhook with a valid `(raw_body, hmac)` pair for their own store. That exact pair remains valid under `HmacValidator.validate` regardless of which `x-shopify-shop-domain` header value accompanies it, since the header is never part of `to_signable_string`. An attacker can therefore replay the captured body+HMAC with the `shop-domain` header set to any victim shop domain, and the app will process the webhook as if it genuinely originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce and results in cross-tenant data confusion: a low-privilege actor (any user able to install the app for a trial/free store) can inject attacker-controlled but "verified" webhook payloads and topics attributed to an arbitrary victim shop. Depending on how the host application's webhook handlers use `WebhookMetadata#shop` (e.g., to look up/update per-shop records, trigger uninstall/GDPR flows, or update billing/subscription state), this can lead to cross-tenant state corruption or unauthorized actions performed against a shop the attacker does not control — meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Likelihood is meaningful: obtaining one valid `(body, hmac)` pair requires only installing the app once as an ordinary merchant (many apps allow free installs/trials), then replaying the exact same POST body and `x-shopify-hmac-sha256` header while changing `x-shopify-shop-domain` to the victim's domain. No access to `api_secret_key` or any privileged credential is required — this is fully within reach of an unprivileged internet user who can install the app.

### Recommendation
Bind the claimed `shop` (and ideally `topic`/`webhook_id`) into the HMAC-verified content instead of trusting the header value independently. Concretely, `to_signable_string` (or an additional check in `Registry.process`) should incorporate the header values that convey tenant/topic identity, or the library should document/require that host apps cross-check `request.shop` against a shop already known to be associated with this specific webhook subscription (e.g., verified via a lookup keyed by `webhook_id` obtained through the Admin API) before trusting it, rather than accepting the header value as authoritative once the body HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own development/trial store `attacker.myshopify.com`, receiving a legitimate webhook, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"id": 1, ...}
   ```
2. Attacker resends the identical body and `x-shopify-hmac-sha256` value, only changing the shop header:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-hmac-for-body>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: {"id": 1, ...}
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the (unchanged) HMAC: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., ...)`, believing the event genuinely originated from `victim-shop.myshopify.com`, even though the payload and signature were generated for the attacker's own store.

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
