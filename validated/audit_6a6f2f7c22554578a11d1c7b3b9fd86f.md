### Title
Webhook `shop` identity is read from an unauthenticated header and is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw request body, then hands the host application a `WebhookMetadata` struct whose `shop` field is populated from the `x-shopify-shop-domain` HTTP header — a value that is never included in the HMAC computation. The identity binding "HMAC-verified bytes == the shop the payload is attributed to" does not hold, because the HMAC only binds the body, not the shop header.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`hmac` is derived from the `hmac-sha256` header, and `to_signable_string` returns only `@raw_body`: [2](#0-1) 

`shop` is read independently from the `shop-domain` header, which is never part of the signable string: [3](#0-2) 

`HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` (i.e., the raw body only) and compares it against the received signature: [4](#0-3) 

`Registry.process` gates only on this body HMAC, then forwards `request.shop` — an unauthenticated header value — directly into the `WebhookMetadata` passed to the app's registered handler: [5](#0-4) [6](#0-5) 

**The broken equality**: the gem's documented contract implies `verified(hmac_over_body) == verified(shop_identity)`. In reality, `hmac` binds only `raw_body`, while `shop` is parsed from a sibling header that carries no cryptographic binding to that body or to the HMAC signature at all. An unprivileged internet user who has ever received (or can otherwise observe) one legitimate webhook delivery for topic `T` — including deliveries the attacker's own installed/test shop receives, since Shopify sends this HMAC using the app's fixed `client_secret` regardless of shop — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value (e.g., a victim shop's domain). `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` will invoke the app's handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This satisfies the "Critical - cross-tenant access" bar: any host application implementation that follows this gem's documented API and uses `WebhookMetadata#shop` to select/scope the tenant session, tenant-specific data store, or webhook idempotency bucket (which is precisely what the field is for — it is the only per-request tenant identifier the library exposes to handlers) will process, store, or act on webhook data under the wrong shop's tenant boundary. This can lead to cross-tenant data corruption/leakage (e.g., an `orders/create` or GDPR redact payload processed against the wrong merchant's records) purely from replaying a body the attacker already legitimately received once, with a forged shop header — no access token, `client_secret`, or privileged account required.

### Likelihood Explanation
Requires only network access to the app's public webhook endpoint plus possession of one legitimate `(raw_body, hmac)` pair (trivially obtainable by installing the app on an attacker-controlled test shop and capturing its own webhook delivery, or intercepting any delivery). The shop header is fully attacker-controlled at replay time and is not validated against anything else in the request. This is directly reachable through the gem's only documented webhook-verification entry point, `Registry.process`, with no gem-level mitigation (no nonce/replay window enforcement, no binding of `shop` into the signable string).

### Recommendation
Include the shop-domain (and ideally webhook-id/topic) in the value that is HMAC-verified, or otherwise cryptographically bind `request.shop` to the authenticated payload before exposing it via `WebhookMetadata`. At minimum, document that `shop` in `WebhookMetadata` is unauthenticated and must be cross-checked by the host application against a known/installed shop list before being used as a tenant key; better, extend `VerifiableQuery#to_signable_string` (or `HmacValidator`) to incorporate the shop header so tampering with it invalidates the signature.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com` and capture a legitimate webhook delivery for a subscribed topic, e.g.:
   ```
   x-shopify-topic: customers/data_request
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: <id>
   body: {"...": "..."}
   ```
2. Replay the identical `body` and `x-shopify-hmac-sha256` to the same app endpoint, changing only:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
3. `Utils::HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb#L13-L22) succeeds because it only checks `body` against the unchanged HMAC.
4. `Registry.process` (lib/shopify_api/webhooks/registry.rb#L188-L200) invokes the app's `WebhookHandler#handle` with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to process the attacker's payload under the victim shop's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
