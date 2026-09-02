### Title
Webhook `shop-domain` header is trusted for tenant identity without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw body alone, while the `shop` (tenant identifier) is read from the `x-shopify-shop-domain` HTTP header, which is never included in the signed bytes. `Registry#process` trusts this unauthenticated `shop` value to route the webhook to the app's handler as the tenant of record.

### Finding Description
`VerifiableQuery#to_signable_string` is the field set that `Utils::HmacValidator.validate` checks against the HMAC. For webhooks, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `Request#shop` — the value used to identify which merchant/tenant the webhook belongs to — is pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the body or the HMAC: [2](#0-1) [3](#0-2) 

`Registry#process` validates the HMAC (over the body only) and then unconditionally forwards `request.shop` to the app's handler as the authoritative tenant identity, alongside the body content: [4](#0-3) 

This is the exact bug class described in the report: an identity-binding field (`shop`) is *acted on* (used to route/attribute the webhook to a tenant) but is *not covered by* the HMAC that is supposed to authenticate the request. The equality that should hold — `hmac_signed_bytes == bytes_that_determine_shop` — is broken: `hmac` authenticates `raw_body` only, while `shop` is parsed from a header outside that authenticated scope.

Because the `client_secret`/API secret used to compute the webhook HMAC is shared by Shopify across *every* shop that installs the app, any shop that installs the app receives genuinely-signed webhooks (signed with the same app secret) for its own tenant. An attacker who controls one installed shop ("Shop A") can capture a webhook whose body they control the content of (e.g., by editing an order note, product title, etc. to embed attacker-chosen data) with a valid Shopify-issued HMAC for that body, and then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header value to a victim tenant "Shop B". `HmacValidator.validate` will still pass (the raw body and its signature are unchanged), but the handler will process the payload under Shop B's identity.

### Impact Explanation
This satisfies "Critical - cross-tenant access": the webhook processing pipeline attributes attacker-controlled webhook content to an arbitrary victim shop, since `shop` never participates in the HMAC binding. Depending on how the host app's webhook handlers use `WebhookMetadata#shop` (e.g., to look up/update per-tenant records, sync data, or trigger tenant-scoped side effects), this allows injecting or corrupting another merchant's data using a signature that was never issued for that merchant.

### Likelihood Explanation
The only prerequisite is the ability to install the app on one's own store (a normal merchant install flow, not a "privileged account" or leaked credential) and the ability to send an HTTP POST to the app's public webhook endpoint with a modified header — both are unprivileged, internet-reachable actions. No access token, `api_secret_key`, or TLS interception is required.

### Recommendation
Include the `shop` (and ideally `topic`, `api_version`, `webhook_id`) in the bytes that are HMAC-verified, or otherwise cryptographically bind the tenant identity to the signed payload before `Registry#process` uses `request.shop` for routing. At minimum, `to_signable_string` should not diverge from the set of fields later trusted as authoritative tenant/routing data.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop "attacker.myshopify.com". Cause Shopify to send a webhook (e.g., `orders/updated`) whose body content is attacker-chosen (e.g., set an order note to arbitrary JSON-embeddable text). Shopify signs this webhook with `HMAC-SHA256(raw_body, api_secret_key)` — a secret shared across all installs of the app — and sends headers including `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture this raw HTTP request (body + `x-shopify-hmac-sha256` header) — the attacker legitimately receives their own webhook and can only intercept it at their own edge, which is not "TLS interception" of a third party.
3. Replay the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` in `Registry#process` recomputes the HMAC over `@raw_body` only [1](#0-0)  — unchanged from step 1 — so validation succeeds.
5. `Registry#process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` [5](#0-4)  using `shop = "victim.myshopify.com"`, and dispatches attacker-controlled body content to the handler under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L65-70)
```ruby
      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
