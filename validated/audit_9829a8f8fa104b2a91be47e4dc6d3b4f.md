### Title
Webhook Shop-Domain Header Not Bound to HMAC Signature Enables Cross-Tenant Event Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) for an inbound webhook entirely from the unauthenticated `X-Shopify-Shop-Domain` header, while the HMAC signature that `Registry.process` verifies only ever covers the raw request body. Any actor who can obtain one validly-signed webhook body (e.g. by owning any real shop that installs the app) can replay that body/HMAC pair while substituting the `shop-domain` header for a different, victim tenant, and the gem will accept it as authentic and hand the forged shop identity to the host application's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#shop` is read straight from the (unauthenticated) header: [1](#0-0) [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which in turn calls `validate_signature`, which computes the HMAC over `verifiable_query.to_signable_string` — i.e. the raw body only: [3](#0-2) [4](#0-3) 

After the HMAC check passes, `Registry.process` builds `WebhookMetadata` directly from `request.shop`, `request.topic`, `request.parsed_body`, and hands it to the app-registered handler: [4](#0-3) 

The identity binding that should hold is: `shop header value == the shop the HMAC-signed body was actually generated for`. Because the `shop` field is never included in `to_signable_string`, that equality is never enforced by the gem — only "some body was HMAC-signed with the app's shared `api_secret_key`" is verified, not "this specific body belongs to this specific shop." Since the HMAC key (`Context.api_secret_key`) is shared across all shops for a given app, any shop that installs the app can generate a fully valid `(body, hmac)` pair (e.g. by triggering a genuine webhook on its own store), then resend that exact body/HMAC to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still succeed because it only recomputes the HMAC over the body, and `Registry.process` will dispatch the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary that host applications rely on when they trust `WebhookMetadata#shop` (or `request.shop`) to determine which merchant's data a webhook event applies to. A merchant that is otherwise an unprivileged actor with respect to other tenants of the same app can inject events that the host application will process as if they originated from a different, victim shop — e.g. spoofing `orders/create`, `app/uninstalled`, or GDPR-style webhook payloads under another tenant's identity. Depending on how the host app's handler uses `data.shop` (looking up/mutating the victim's stored session, order records, or subscription state), this results in cross-tenant data corruption or unauthorized actions attributed to another merchant — a cross-tenant integrity/authorization violation.

### Likelihood Explanation
Any actor able to install the app on their own store (a routine, unprivileged action for any Shopify merchant) can obtain at least one genuinely signed `(body, hmac)` pair from their own shop's webhook deliveries, and only needs to control the outbound HTTP request to the app's public webhook endpoint (trivial, since these endpoints are internet-reachable by design) to replay it with a modified `shop-domain` header. No access to `api_secret_key`, access tokens, or any privileged credential is required — this only requires normal, unprivileged access to a real (attacker-controlled) shop.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-signable string, or otherwise cryptographically tie the claimed shop identity to the signed payload, so that `Registry.process` can detect when a genuinely-signed body has been replayed under a different shop's identity. At minimum, document that `request.shop` is unauthenticated and must not be trusted by host applications without an out-of-band cross-check (e.g., verifying the shop against a session/store previously established via OAuth for that specific webhook subscription's `webhook_id`).

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify delivers a genuine webhook to the app's endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (where `H = HMAC-SHA256(api_secret_key, B)`), and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker captures `(B, H)` (they own this shop and can trivially trigger/observe such deliveries, e.g. via `orders/create` on their own store).
3. Attacker POSTs the same `B` and `H` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares it to `H` — this matches because the body `B` is unchanged, per: [3](#0-2) 
5. Validation succeeds; `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`, per: [4](#0-3) 
6. The host application processes attacker-controlled webhook data as though it came from `victim-shop.myshopify.com`.

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
