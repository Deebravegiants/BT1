## Analysis

The `[M02]` report's underlying bug class is: **a value is trusted for a security decision while a related, unauthenticated value is used to act on that decision** — i.e., the "check" and the "act" are performed on different data. In `ShopifyAPI::Webhooks`, the same pattern occurs between the HMAC-verified bytes and the tenant identity used to dispatch the webhook.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

The HMAC is verified over that same raw body via `HmacValidator.validate`, comparing `request.hmac` (from the `X-Shopify-Hmac-Sha256` header) against a signature computed solely from `verifiable_query.to_signable_string`: [2](#0-1) 

However, `request.shop` — the tenant identifier that the app is expected to trust — is read directly from the `X-Shopify-Shop-Domain` / `x-shopify-shop-domain` header, which is **not included in the signable string at all**: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately hands `request.shop` (unauthenticated) to the app's handler as the trusted tenant identity, alongside `request.parsed_body` (the HMAC-covered bytes): [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no binding back to the HMAC computation: [5](#0-4) 

### The identity-binding break

The equality that should hold is:

`shop_covered_by_HMAC == shop_delivered_to_handler`

But in this code, the HMAC only covers `@raw_body`, and `shop` is sourced from a header outside that signed scope. So the equality that actually holds is only:

`HMAC(secret, raw_body) == received_hmac`

with `shop` supplied independently and unauthenticated.

### Why this is exploitable (not merely theoretical)

Any merchant can install the app on their own store (this is not a "privileged account" in the sense excluded by the rules — installing an app is the normal unprivileged onboarding flow) and thereby receive a **genuinely Shopify-signed** webhook for their own shop (valid body + valid HMAC, both computed by Shopify with the app's real secret). Because the shop domain lives in a header outside the HMAC scope, the attacker can:

1. Capture their own legitimate webhook delivery (raw body + `X-Shopify-Hmac-Sha256` + `X-Shopify-Topic`).
2. Replace only the `X-Shopify-Shop-Domain` header with a victim shop's domain.
3. Replay the request to the app's webhook endpoint.

`Registry.process` will validate successfully — the HMAC still matches the unchanged body — and will dispatch `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's own webhook payload>, ...)` to the app's handler. Any app that uses `data.shop` to key its per-tenant database writes (the officially documented and expected pattern, since `WebhookMetadata` is the only tenant signal the gem exposes to `handle`) will attribute attacker-controlled data to another merchant's tenant — a cross-tenant data-integrity/access break achieved purely by manipulating an HTTP header the gem itself never authenticates.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the trusted `shop` identity from the `X-Shopify-Shop-Domain` header, but `Utils::HmacValidator` only verifies the HMAC over the raw request body (`to_signable_string`). Any actor holding one genuinely-signed webhook (e.g., from their own installed shop) can swap the shop header and have the payload attributed to a different tenant.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only [1](#0-0) , while `shop` is parsed independently from headers [3](#0-2) . `HmacValidator.validate` only checks that the body's HMAC matches [2](#0-1) , so the shop header can be altered post-signing without invalidating the check. `Registry.process` passes this unauthenticated shop value straight into `WebhookMetadata` handed to the app's handler [4](#0-3) .

### Impact Explanation
This breaks the tenant-identity binding between the HMAC-verified content and the shop that consumes it, enabling cross-tenant data injection/impersonation in any app that trusts `WebhookMetadata#shop` for tenant scoping — the documented and only tenant signal this gem provides via `handle`.

### Likelihood Explanation
Requires only a party capable of obtaining one valid, Shopify-signed webhook delivery (trivial via installing the app on any shop) and the ability to replay an HTTP request with a modified header to the app's public webhook endpoint — no secrets, tokens, or privileged access needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them to the HMAC-covered content) so header tampering invalidates the signature, matching Shopify's documented webhook verification guidance.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; capture a real webhook delivery: raw body `B`, header `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Replay `POST /webhooks` with body `B`, `X-Shopify-Hmac-Sha256: H` (unchanged), `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `HmacValidator.validate` succeeds (body/HMAC unchanged); `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's body>)`, causing the app to process attacker data under the victim tenant's identity.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
