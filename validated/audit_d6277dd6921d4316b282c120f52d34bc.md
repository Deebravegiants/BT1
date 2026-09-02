## Title
Webhook shop-domain identity is unauthenticated and not bound to the HMAC-verified payload, enabling cross-tenant webhook confusion - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, then dispatches the app's handler using a `shop` value taken from an HTTP header that is never included in that HMAC computation. Because the header is unauthenticated, an attacker can pair a genuine, correctly-signed webhook body (obtainable by installing the app on a store they control) with a forged `shop-domain` header claiming to belong to a different, victim shop, and the library will pass this off to the app as an authentic webhook for that victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

The `shop` accessor, however, is read from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is completely outside the signed material: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (the body) against the HMAC secret — it never touches headers: [3](#0-2) 

`Registry.process` uses exactly this validation, then immediately trusts `request.shop` (the unauthenticated header) to build the `WebhookMetadata` handed to the app's handler, which apps use to scope the webhook payload to a specific merchant/tenant: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`shop-domain header used to attribute/process the webhook payload` ≠ `shop actually covered by the HMAC signature (none — HMAC covers body bytes only)`.

**Exploit path (no special privileges required):**
1. Attacker installs the vulnerable app on their own Shopify development/partner store (an ordinary, unprivileged action any internet user can take).
2. Attacker triggers or waits for a real webhook Shopify sends to the app for their own store. This webhook has a valid `X-Shopify-Hmac-Sha256` computed over the (attacker-controlled) body using the app's real `api_secret_key` — the attacker never needs to see or know the secret, only to capture the resulting request.
3. Attacker replays that exact body + HMAC to the app's public webhook endpoint, but swaps `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) to name a victim shop that also uses the same app.
4. `HmacValidator.validate` succeeds (body/HMAC pair is genuinely valid), and `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` while `body` is fully attacker-controlled content.
5. The host application processes attacker-controlled data as if it originated from and belongs to the victim's tenant.

### Impact Explanation
This breaks the tenant boundary the webhook system is supposed to enforce: it allows an unprivileged installer of the app to inject attacker-controlled webhook payloads that are attributed to a different, victim merchant's shop. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up the victim's session/access token and act on their store, to update per-shop billing/compliance state, or to fulfill mandatory `customers/redact`/`shop/redact` compliance webhooks against the wrong shop), this is a cross-tenant data-integrity/confusion issue reachable by any internet user who can install the app once. This matches the report's "Critical - cross-tenant access" impact category, since the vulnerability is a broken identity-binding: a value used to select/attribute tenant data is not covered by the same authentication mechanism (HMAC) that vouches for the payload.

### Likelihood Explanation
Likelihood is high for any app that trusts `WebhookMetadata#shop`/`request.shop` without independently cross-checking it (e.g., against a list of shops that are expected to send that specific webhook topic, or against the shop tied to an active session). The attack requires no credentials beyond normal, self-service app installation, and no knowledge of the `api_secret_key`.

### Recommendation
Do not treat the `shop-domain` (or `topic`/`webhook-id`) header as trusted merely because the body's HMAC validates. Either:
- Include the shop domain (and topic) in the signable string that is HMAC-verified (would require coordinating with Shopify's actual signing scheme, which currently signs only the body — so this may not be feasible unilaterally), or
- Cross-verify the header-provided `shop` against an out-of-band trusted source before dispatching (e.g., require that a session/registration already exists for that exact `shop`, and reject/flag webhooks whose claimed shop cannot be corroborated), and clearly document to consumers of `ShopifyAPI::Webhooks::Registry` that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be used as the sole tenant-scoping signal.

### Proof of Concept
```ruby
# Attacker installs app on their own store "attacker.myshopify.com" and captures
# a legitimate webhook Shopify sends them (body + valid HMAC computed with the
# app's real api_secret_key, which the attacker never needs to know).
captured_body = '{"id": 1, "malicious": "payload"}'
captured_hmac = "<value taken verbatim from the genuine X-Shopify-Hmac-Sha256 header>"

# Attacker replays it to the app's public webhook endpoint, forging the shop header:
forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => captured_hmac,          # still valid for captured_body
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # NOT covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) succeeds (body/HMAC pair genuinely matches),
#    handler is invoked with shop == "victim-shop.myshopify.com" even though the
#    payload actually originated from the attacker's own store.
```

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
