### Title
Webhook `shop-domain` Header Not Covered by HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` value used to attribute the webhook to a tenant is read directly from an unauthenticated HTTP header. Because the shop identity is never part of the signed payload, an attacker who can submit a request to the app's webhook endpoint with a previously observed valid `(body, hmac)` pair can freely relabel which shop the event is attributed to, breaking the binding between the cryptographic proof and the tenant identity — the same class of flaw as the reported issue, where a value acted upon (nonce/scope) was not covered by the authenticated data.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it against `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `Webhooks::Request#to_signable_string` returns only the raw request body: [2](#0-1) 

but `Webhooks::Request#shop` is derived from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is not part of the signed string at all: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then dispatches the handler using `request.shop`, which is exactly the field excluded from the signature: [4](#0-3) 

The identity binding that should hold is:
`shop attributed to the event (WebhookMetadata.shop) == shop that Shopify actually signed the event for`

Because the HMAC only proves the integrity of `@raw_body`, this equality is never enforced. An attacker who has captured a single legitimate `(raw_body, hmac)` pair (e.g., from a webhook delivered to their own shop, or any webhook payload/HMAC pair leaked via logs, browser devtools, a reverse proxy, or replay) can resend that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary value in the `shop-domain` header. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event came from the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant integrity/confusion issue: a handler that uses `WebhookMetadata#shop` to look up a session, update per-shop state, or gate merchant-specific logic (the intended and documented use of this field) can be made to act on/for the wrong tenant using a payload that was never actually signed for that tenant. This matches the Critical impact category of cross-tenant access via broken identity binding.

### Likelihood Explanation
Exploitation only requires the ability to send an HTTP POST to the app's public webhook endpoint (these endpoints are internet-reachable by design) plus knowledge of any one valid `(raw_body, hmac)` pair — which the attacker can trivially obtain by registering their own shop/app installation and receiving a legitimate webhook, or by observing one in logs/network traces. No access to `api_secret_key`, access tokens, or any privileged credential is required, and no interaction with Shopify's own signing key is needed. This does not depend on the host application misusing the gem's documented API — `Registry.process`/`Request#shop` are used exactly as designed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signed material, or otherwise cryptographically bind the shop identity to the HMAC-verified body — e.g., verify that any shop-scoped identifier used downstream is derived from data that is actually covered by `to_signable_string`, not from a bare header. At minimum, `Registry.process` should not trust `request.shop` for any authorization or tenant-selection decision unless the shop value is provably tied to the signed body (for instance, by requiring callers to check the shop against a value obtained from Shopify's servers rather than from the incoming header).

### Proof of Concept
1. Register a webhook subscription and receive one legitimate delivery, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header value for `shop-a.myshopify.com`.
2. Replay the identical HTTP request to the app's webhook endpoint, changing only the `X-Shopify-Shop-Domain` header to `shop-b.myshopify.com` (a different tenant, e.g., a real other merchant or an attacker-controlled dev store), keeping the same `raw_body` and `X-Shopify-Hmac-Sha256`.
3. `Webhooks::Request#hmac` and `#to_signable_string` are unaffected by the header change (`Request#to_signable_string` returns `@raw_body` only) — `Utils::HmacValidator.validate` in `Registry.process` succeeds.
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop == "shop-b.myshopify.com"`, even though the payload was only ever signed by Shopify for `shop-a.myshopify.com`, demonstrating the broken shop/HMAC binding. [4](#0-3)

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
