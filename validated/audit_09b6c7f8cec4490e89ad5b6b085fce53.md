### Title
Webhook Shop, Topic, and Webhook-ID Headers Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the shop identity used by `Registry.process` to route webhook data (`request.shop`) is read from an HTTP header that is never included in the HMAC computation. Any user who can obtain a legitimately-signed webhook for their own shop (by simply installing the app on a store they control) can replay it against the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and `topic`/`webhook-id`) header changed to an arbitrary victim shop, and the signature will still validate. This breaks the identity binding the host app relies on to know which merchant/tenant a webhook event belongs to.

### Finding Description
`Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` as the tenant identity for dispatch: [1](#0-0) 

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns solely `@raw_body`: [3](#0-2) 

But `shop`, `topic`, and `webhook_id` are all parsed straight from HTTP headers that are never fed into the signature: [4](#0-3) 

The intended equality this code is supposed to enforce is:

`hmac_valid(raw_body) == true` implies `request.shop == the shop Shopify actually sent this webhook for`

In reality, the code only proves `hmac_valid(raw_body) == true`; the `shop` (and `topic`/`webhook_id`) fields are attacker-controlled headers with no cryptographic binding to the signed body. This is precisely the "field acted on but not covered by the HMAC" bug class described in the analog report (where `Rv32BranchLessThan256Chip` used the wrong opcode offset, decoupling the value acted upon from the value that was actually validated) — here the value validated (body bytes) is disjoint from the value acted upon (shop header).

### Impact Explanation
An unprivileged internet user can install the target app on a store they control (a normal, permitted action) and receive a genuine webhook signed by Shopify using the app's real `client_secret`, over a body they know. That HMAC remains valid no matter what the `X-Shopify-Shop-Domain` header says, because the header isn't part of the signed content. The attacker can therefore resend that exact body to the app's public webhook endpoint with the shop header rewritten to a victim's `*.myshopify.com` domain. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: ..., ...)` and dispatches it to the host app's handler as if it were a legitimate event for the victim shop: [1](#0-0) 

Handlers that key persistence, redaction, or business logic off `data.shop` (e.g. `shop/redact`, `customers/redact`, `customers/data_request`, or app-specific data-sync handlers) will act on the wrong tenant, i.e., cross-tenant data corruption/exfiltration triggered entirely from the attacker's own installation, without ever touching the victim's or the app's credentials. This matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that (a) allows public/self-serve installation, and (b) has webhook handlers that trust `WebhookMetadata#shop` for tenant-scoped effects (mandatory privacy topics `shop/redact`, `customers/redact`, `customers/data_request` are prime candidates since every embedded app must implement them). The attack requires no secrets beyond installing the app on an attacker-owned store, which is the normal onboarding flow.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed payload before they are trusted:
- Compute/verify the signature over a canonical string that includes `shop-domain` (and `topic`, `webhook-id`) in addition to the raw body, mirroring how Shopify signs the payload, or
- If Shopify's HMAC is defined only over the body (as it is today for webhooks), treat the `shop-domain` header as untrusted for authorization decisions and instead require the consuming app to independently verify that the shop from the header matches a shop with a known active installation/session before acting on the payload, and document this requirement clearly so host apps don't assume `data.shop` is authenticated by `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, subscribing to some topic (e.g. `orders/create`).
2. Shopify sends a webhook to the app's endpoint with headers such as:
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - `X-Shopify-Hmac-Sha256: <valid HMAC over raw_body>`
   - body: `{"id": 1, ...}`
3. Attacker captures this request, then replays it to the same endpoint, changing only the header:
   - `X-Shopify-Shop-Domain: victim.myshopify.com`
   - keeps the same `X-Shopify-Hmac-Sha256` and body.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `to_signable_string` (`@raw_body`), unaffected by the header change: [3](#0-2) 
5. `Registry.process` then dispatches `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: ..., ...)` to the host app's handler, which now believes this attacker-supplied event genuinely originated from `victim.myshopify.com`. [1](#0-0)

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
