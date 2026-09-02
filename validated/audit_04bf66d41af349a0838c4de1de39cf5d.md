### Title
Webhook shop identity is trusted from an unauthenticated header while only the raw body is HMAC-verified - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from `@raw_body` only, but exposes `shop` (and `topic`, `webhook_id`, `api_version`) directly from HTTP headers that are never included in that signable string. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then unconditionally forwards the header-derived, unauthenticated `shop` value to the app's handler as the tenant identity for the webhook.

### Finding Description
The HMAC binding this gem enforces is:

`OpenSSL.secure_compare(HMAC(api_secret_key, raw_body), received_hmac)` [1](#0-0) 

but `to_signable_string` for a webhook request only ever returns `@raw_body`: [2](#0-1) 

Meanwhile `shop` (and `topic`, `webhook_id`, `api_version`) are read straight from request headers, none of which participate in the signature: [3](#0-2) 

`Registry.process` validates only the body/HMAC pair, then passes the *header-derived* `request.shop` on to the handler as the authoritative tenant identity, with no cross-check that the shop matches anything cryptographically tied to the signed payload: [4](#0-3) 

The broken identity binding is: `shop header value == the shop that produced/authorized this HMAC-signed body`. In reality the HMAC only proves "this body was signed by the app's `api_secret_key`" — it says nothing about which shop the body belongs to, because `shop` is never part of `to_signable_string`.

### Impact Explanation
Any entity that can obtain one genuinely-signed webhook body+HMAC pair for a shop it controls (e.g., a merchant who has installed the app themselves, an ordinary unprivileged operator of the app) can replay that exact `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and `topic`/`webhook-id`) header for a different, victim shop. `Utils::HmacValidator.validate` will still succeed because it only checks `raw_body` against the HMAC, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the body came from the victim shop: [5](#0-4) 

Any host application that uses the `shop` field from `WebhookMetadata` to route processing to a specific tenant's data/session (the intended and documented use of this field) can be made to apply data belonging to one shop against another shop's tenant context — a cross-tenant identity-binding break using only the app's own currently-installed, unprivileged access, with no theft of `api_secret_key` or access tokens required.

### Likelihood Explanation
Any legitimate but unprivileged/malicious merchant using the app can generate an arbitrary number of genuinely-signed webhook bodies for their own shop (by triggering real store events), then replay the raw body and its HMAC header to the app's public webhook endpoint with a forged `shop-domain` header. No secret material beyond what a normal merchant naturally receives is needed, and the gem performs no verification tying the header-derived `shop` to the signed content.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-covered signable string, or independently verify that the header-derived shop is one the receiving app currently has a valid session/installation for a body that was actually signed for that shop (e.g., require the raw body to embed the shop domain and verify it matches the header before dispatching to handlers).

### Proof of Concept
1. As a merchant, install the app and trigger a webhook so the app receives a legitimate `(raw_body, X-Shopify-Hmac-Sha256, X-Shopify-Shop-Domain: attacker-shop.myshopify.com)` triple, correctly signed with the app's `api_secret_key`.
2. Resend the exact same `raw_body` and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` in `Registry.process` succeeds because it only checks `raw_body`, so `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...))`, causing the app to process attacker-controlled body content under the victim shop's identity. [4](#0-3)

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

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
