## Finding

### Title
Webhook `shop` identity is trusted without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body, then forwards the `shop` value taken from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header to the app's handler as the tenant identity. The `shop` field is never included in the bytes that are HMAC-verified, so it can be swapped without invalidating the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shop-domain` header, independent of the signable string: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` computes the HMAC only over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` header value: [3](#0-2) 

`Registry.process` trusts this validation as sufficient proof of authenticity, then builds `WebhookMetadata` using `request.shop` — a value that was never part of the signed bytes: [4](#0-3) 

The broken identity binding is:
`HMAC-verified bytes (raw_body) ≠ bytes that determine tenant identity (shop-domain header)`

Because the `shop` header sits outside the HMAC-covered payload, any request whose `raw_body` + `hmac` pair is valid for the app's shared `client_secret` (e.g., one legitimately received by an attacker who has installed the same app on their own store) can be replayed with the `shop-domain` header rewritten to any other merchant's `myshopify.com` domain. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the body originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem's webhook processing API is supposed to enforce: `Registry.process` and `WebhookMetadata` are the app's sole cross-tenant identity signal for a webhook. An attacker holding a merchant account with the same app installed can generate real, validly-signed webhook payloads (topic/body of their choosing among the topics they can trigger, e.g. `orders/create` on their own store) and replay them at the app's webhook endpoint with a forged `shop-domain`, causing the host application to process attacker-controlled data under another tenant's identity — a cross-tenant access/data-confusion condition.

### Likelihood Explanation
Requires only an account on any shop with the vulnerable app installed (no elevated privileges, no leaked secret, no TLS interception) — an "unprivileged internet user" relative to the victim tenant. The header is not validated against a shop registry or the raw body in `Request` or `Registry`, so exploitation only requires observing one's own real webhook deliveries and modifying one HTTP header on replay.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header value in the bytes covered by the HMAC comparison, or independently verify that the shop asserted in the header matches a shop already associated with a valid session/installation known to the host app before dispatching to handlers. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted as a tenant boundary without additional verification by the consuming application.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`), receiving a real request with headers `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same `raw_body` and `hmac` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` recomputes the HMAC over `raw_body` only [3](#0-2)  — it matches, since `shop` isn't part of the signed content.
4. `Registry.process` proceeds and calls the app's handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` [5](#0-4) , causing the host app to act on attacker data as if it belonged to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
