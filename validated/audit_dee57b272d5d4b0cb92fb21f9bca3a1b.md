### Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies the authenticity of an incoming webhook using `Utils::HmacValidator.validate(request)`, but the HMAC signature only covers the raw request body, not the `shop-domain` header. `WebhookMetadata` (and therefore the app's webhook handler) trusts `request.shop`, which is read directly from an unauthenticated header. An attacker who can obtain one valid `(body, hmac)` pair issued for their own shop can replay it to the app's webhook endpoint with a forged `shop-domain`/`x-shopify-shop-domain` header pointing at a victim shop, and the signature check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived purely from the (unauthenticated) header: [2](#0-1) 

`Registry.process` validates the HMAC and, once it passes, hands `request.shop` straight to the handler as the tenant identifier, without any additional binding check between the signed body and the shop claim: [3](#0-2) 

`HmacValidator.validate` calls `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received signature — since `to_signable_string` for a webhook request is just the raw body, the shop-domain header is never part of the signed material: [4](#0-3) 

This breaks the intended identity binding: **shop claimed in the request header == shop covered by the HMAC**. In reality: `shop (header, attacker-controlled)` ≠ `shop (implicitly bound by HMAC, which is none)`. All shops installed under one app share the same `client_secret`/HMAC key, so any merchant who has legitimately installed the app can capture a real `(body, hmac)` pair delivered by Shopify for their own shop, then resend that exact body+hmac to the app's webhook endpoint while substituting a different shop's domain in the `shopify-shop-domain` (or `x-shopify-shop-domain`) header. `HmacValidator.validate` still returns `true` because it only checks the body against the shared secret, and `Registry.process` passes the attacker-chosen `shop` value straight through to `WebhookMetadata`/the handler.

### Impact Explanation
If the host application relies on `WebhookMetadata#shop` (as documented/exposed by this gem) to select which tenant's data/session to update in response to the webhook, an attacker can inject data or trigger tenant-scoped side effects (e.g., order/customer data processing, shop deauthorization flows, GDPR deletion webhooks) attributed to a victim shop they do not control — a cross-tenant access/confusion issue satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged user who can install the app on their own shop (or who can otherwise obtain one genuine webhook delivery, e.g. by triggering an event on a shop they control) can capture a valid `(raw_body, hmac)` pair and replay it with a forged `shop-domain` header to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or TLS interception is required — the shop header is simply never authenticated.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed material, or otherwise cryptographically tie the header-derived shop to the signed body (e.g., include shop domain as part of the signable string, or independently verify that the shop belongs to a session with the given delivery via app-level records) before dispatching `WebhookMetadata` to handlers.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger any subscribed webhook event so Shopify delivers a legitimately signed webhook `POST` (`raw_body`, `x-shopify-hmac-sha256`) to the app's endpoint.
2. Capture that `raw_body` and `hmac` value.
3. Replay the exact same `raw_body` and `hmac` to the same endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the shared `client_secret`; the handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the payload actually originated from `attacker-shop.myshopify.com`.

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
