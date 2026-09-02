This confirms the vulnerability: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is read straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header [2](#0-1) . `HmacValidator.validate` only verifies the HMAC over `to_signable_string` (i.e., the raw body) [3](#0-2) , and `Registry.process` checks only that HMAC before dispatching `request.shop` straight to the handler [4](#0-3) .

### Title
Webhook shop attribution bypass via HMAC-unauthenticated `shop-domain` header — cross-tenant webhook spoofing (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating the HMAC-SHA256 signature, but the signature only covers the raw request body — never the `shop-domain` header that the handler later trusts as the tenant identity.

### Finding Description
The HMAC binding this gem enforces is: `HMAC(secret, raw_body) == received_hmac`, computed via `Utils::HmacValidator.validate_signature`, which hashes `verifiable_query.to_signable_string` [3](#0-2) . For webhook requests, `to_signable_string` is defined as simply `@raw_body` [1](#0-0) . The `shop` accessor, however, is pulled independently from the `x-shopify-shop-domain`/`shopify-shop-domain` header, entirely outside the signed material [2](#0-1) .

`Registry.process` performs exactly one authentication check — `Utils::HmacValidator.validate(request)` — before dispatching the handler with `shop: request.shop` taken from that unauthenticated header [4](#0-3) .

Because a single app's `api_secret_key` is shared across every shop that installs the app, the HMAC over a given raw body is valid for *any* shop, not just the shop that originally received it. This breaks the identity binding: `shop authenticated by HMAC` ≠ `shop stored/acted upon by the handler`. A merchant with a legitimate installation of the app (an unprivileged internet user with respect to other tenants) can capture one of their own genuine webhook deliveries (raw body + valid `x-shopify-hmac-sha256`), then replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value naming a *different* merchant's shop. The HMAC check still passes (it never inspected the header), and the handler receives `WebhookMetadata` attributing the payload to the victim shop [5](#0-4) .

### Impact Explanation
This is a cross-tenant confusion vulnerability: an attacker who legitimately controls one tenant (shop) of a multi-tenant app can inject attacker-chosen webhook data attributed to a victim tenant. Depending on how the host application's webhook handlers use `shop` (e.g., to look up/update per-shop records, mark orders/customers, trigger `customers/redact` or `shop/redact` GDPR flows, or update shop-scoped state), this enables cross-tenant data corruption or spoofed events against shops the attacker does not control — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation only requires the attacker to be a normal installed user of the app on their own store (no leaked secrets, no privileged access, no MITM) — they can generate arbitrary genuine webhook deliveries for their own shop by taking ordinary actions (e.g. updating their own order), capture the raw body and its valid HMAC via any HTTP proxy on their own infrastructure, then POST it to the shared public webhook endpoint with a forged `shop-domain` header naming another shop.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the header-derived `shop` value to the authenticated request: e.g., require the webhook consumer to independently verify that `request.shop` corresponds to a shop with a currently active session/installation before trusting it, and document that `request.shop` must never be treated as authenticated by `HmacValidator.validate` alone. Alternatively, expand `to_signable_string` (or add a separate check in `Registry.process`) to bind the `shop`, `topic`, and `webhook_id` headers into the HMAC verification rather than validating body bytes only.

### Proof of Concept
1. App is installed on both `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (same app, same `api_secret_key`).
2. Attacker triggers a real webhook on their own shop and captures the raw POST body and the `x-shopify-hmac-sha256` header Shopify computed for it.
3. Attacker replays the identical body/HMAC to the app's webhook endpoint, replacing only `x-shopify-shop-domain: attacker-shop.myshopify.com` with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the raw body against the shared secret [6](#0-5) .
5. The registered handler executes with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)`, causing the app to act on the victim shop using attacker-controlled body content.

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
