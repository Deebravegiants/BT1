Confirmed. This matches the analog bug class exactly: an identity field (`shop`) is acted on by the app's webhook dispatch, but is not covered by the HMAC signature that authenticates the request.

### Title
Webhook `shop` (and `topic`/`webhook-id`) header spoofing via HMAC that only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `HmacValidator.validate` authenticates the payload bytes but never binds the `shop`, `topic`, or `webhook_id` HTTP headers to that signature. `Registry.process` then trusts `request.shop` (and `request.topic`) taken straight from unauthenticated headers to build the `WebhookMetadata` passed to the host app's handler.

### Finding Description
The identity binding that should hold is: `shop authenticated by HMAC == shop acted on by the handler`. Instead:

- `Request#to_signable_string` only returns `@raw_body` [1](#0-0) .
- `Request#shop`, `#topic`, and `#webhook_id` are read directly from HTTP headers with no cryptographic binding to the signed content [2](#0-1) .
- `Registry.process` validates only `Utils::HmacValidator.validate(request)` (which checks the body signature) and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to construct `WebhookMetadata` delivered to the app's `WebhookHandler` [3](#0-2) .
- `WebhookMetadata.shop` is a plain `String` field with no further verification, and this is exactly the value host applications rely on to key their per-tenant data [4](#0-3) .

Because `Context.api_secret_key` is a single, app-wide secret shared across every shop that has installed the app (not a per-shop secret), any merchant who has installed the app can legitimately receive a webhook with a valid `x-shopify-hmac-sha256` value for some body. That attacker-controlled merchant can then replay the same body and valid HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header for a victim shop. `HmacValidator.validate` still passes because it only checks the body bytes, and `Registry.process` forwards the forged `shop` value to the handler as if it were authentic.

### Impact Explanation
This breaks the `shop` binding that host applications depend on for tenant isolation: a request that is only proven to originate from *some* installed shop is delivered to the handler tagged with an arbitrary victim `shop` value. Depending on how the host app keys its per-shop side effects (e.g., "if topic == orders/create for shop X, mark order paid" or GDPR-style `customers/redact`/`shop/redact` mandatory webhooks), this enables cross-tenant data corruption or spoofed mandatory-compliance actions attributed to a shop the attacker doesn't control — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker has installed the app on their own shop (a normal, unprivileged merchant), letting them capture one legitimately signed webhook body/HMAC pair and replay it with modified `shop`/`topic` headers against the app's public webhook endpoint. No access to `api_secret_key`, tokens, or the target shop is needed.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string used by `HmacValidator`, or otherwise require the host application to independently verify that the `shop` header matches a shop with an active session for that specific webhook body, rather than trusting header values that sit outside the HMAC-covered payload. At minimum, document that `request.shop`/`request.topic` are unauthenticated and must not be trusted to key tenant-specific side effects.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com`, receiving a legitimately signed webhook: body `B`, `x-shopify-hmac-sha256: H = HMAC(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and same `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which recomputes HMAC over `B` only and succeeds [5](#0-4) .
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` and passed to the host handler [6](#0-5) , even though the payload was never produced by or for `victim.myshopify.com`.

### Citations

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
