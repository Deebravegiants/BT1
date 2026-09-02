Confirmed: `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which only signs `request.to_signable_string` (the raw body) at [1](#0-0) , yet the tenant identity `request.shop` is read from the unsigned `x-shopify-shop-domain` header at [2](#0-1)  and passed directly into the handler as the authoritative tenant at [3](#0-2) .

### Title
Webhook shop-domain header is not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw body only, while the `shop` (tenant) attribute consumed by `Registry.process` is taken from the `x-shopify-shop-domain` header, which is not part of the signed data.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 
`Request#shop` is read independently from a header that plays no role in the HMAC computation: [2](#0-1) 
`Registry.process` validates only `Utils::HmacValidator.validate(request)`, which checks `hmac(secret, to_signable_string)` — i.e. `hmac(secret, raw_body)` — and, once that passes, forwards `request.shop` unchecked as the tenant to the handler: [3](#0-2) 

The binding the gem implicitly relies on is: `shop_bound_by_HMAC == shop_used_by_handler`. Because the `shop-domain` header is excluded from `to_signable_string`, this equality does not hold — the HMAC only proves "this exact body was signed by the app's secret," it proves nothing about which shop the body pertains to. `HmacValidator.compute_signature`/`validate_signature` operate purely on the signable string and never reference the header at all: [4](#0-3) 

Since the `api_secret_key` (the app's client secret) is identical for every shop that installs the app, any merchant who has legitimately installed the app can receive genuine `(raw_body, hmac)` pairs from Shopify for their own shop's events. Because the `shop-domain` header is unsigned, that same attacker can resend an intercepted, genuine webhook body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass (same body, same secret, same HMAC), and `Registry.process` will hand the attacker-controlled body to the app's handler tagged as belonging to the victim shop.

### Impact Explanation
This crosses a tenant boundary using data supplied by an unprivileged party who only had legitimate access to their own shop's webhook traffic (no `api_secret_key`, no access token, and no privileged account for the victim shop is required). Depending on how the host app's `WebhookHandler` implementations use `WebhookMetadata#shop` (e.g., to select the merchant record to update, to write order/customer/app-uninstall state, or to trigger data deletion), the attacker can inject or corrupt data attributed to another merchant, or trigger tenant-scoped side effects (such as GDPR/app-uninstalled handling) against a shop they do not own. This matches the "cross-tenant access" Critical impact bucket described by the rules, since the request that reaches the handler is misattributed to a different tenant than the one that actually produced it.

### Likelihood Explanation
Any merchant who installs the app is, from the app developer's perspective, an "unprivileged internet user" relative to other merchants' data. Every such merchant naturally receives genuine webhook deliveries (body + HMAC) for their own shop, which is all that's needed as replay material; forging the header requires no cryptographic material, only sending an HTTP POST with a different `X-Shopify-Shop-Domain` header value, which is entirely under attacker control at the HTTP layer, since this gem does not bind that header to the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signable string, or otherwise cryptographically bind them to the signature, so that `Registry.process` can verify that the `shop` value it forwards to handlers is the same one Shopify actually signed for. Since Shopify's webhook HMAC by design only covers the raw body, an alternative mitigation is for `Registry.process` to also verify the `webhook_id` (and/or shop) against server-side records (e.g., only accept a given `webhook_id` once, or verify it belongs to a webhook subscription created for that specific shop) before invoking the handler.

### Proof of Concept
1. App is installed on Shop A (attacker-controlled) and Shop B (victim). Both use the same app `client_secret`.
2. Shopify sends a legitimate webhook to the app for Shop A: `POST /webhooks` with headers `X-Shopify-Shop-Domain: shop-a.myshopify.com`, `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body with client_secret>`, and some `raw_body`.
3. Attacker (who owns Shop A and can observe/log this legitimate request, e.g., via their own proxy/logging middleware in front of their shop's traffic) captures `raw_body` and its `X-Shopify-Hmac-Sha256` value.
4. Attacker replays the identical `raw_body` and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [5](#0-4) , which recomputes the HMAC over `raw_body` only and finds it valid, since the header was never part of the signed data [1](#0-0) .
6. The handler is invoked with `WebhookMetadata.new(..., shop: "shop-b.myshopify.com", body: <Shop A's data>, ...)` [6](#0-5) , causing Shop A's webhook payload to be processed under Shop B's tenant identity.

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
