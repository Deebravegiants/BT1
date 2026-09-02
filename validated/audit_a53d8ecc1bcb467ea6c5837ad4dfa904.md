### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted from unauthenticated headers and are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies the webhook HMAC over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to dispatch and identify the tenant are read directly from HTTP headers that are excluded from the signed content.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` (which HMAC-verifies `to_signable_string`) authenticates nothing but the body bytes: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from headers via `shopify_header`, with no cryptographic binding to the body or to each other: [2](#0-1) [3](#0-2) 

`Registry.process` only checks the HMAC before dispatching, then builds `WebhookMetadata` directly from these unauthenticated header fields and hands them to the host app's handler as the trusted tenant/event identity: [4](#0-3) [5](#0-4) 

The identity-binding equality broken is: `shop header value used by handler.handle` ≠ `shop value cryptographically covered by the HMAC` (the HMAC covers `raw_body` bytes only). Since the app's `client_secret` (`api_secret_key`) is shared across every shop that installs the app, any unprivileged attacker who installs the app on their own store receives genuinely HMAC-signed webhook deliveries. They can capture one such valid `(body, hmac)` pair and replay it to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, or `x-shopify-webhook-id` header. Because none of these headers factor into `to_signable_string`, the HMAC check still passes, and `Registry.process` will dispatch the (attacker-chosen) topic/shop combination with a body that was never actually produced for that shop or topic.

### Impact Explanation
This is a cross-tenant identity binding break: the `shop` value that a host application uses to route the payload to a specific merchant's tenant record is not the same `shop` value protected by the HMAC. An attacker with a legitimate app installation (no special privilege, no leaked secret) can forge webhook events that appear to originate from an arbitrary shop domain or an arbitrary topic while smuggling body content of their choosing (subject to the constraint that it must be valid JSON they crafted for their own install, since the body itself is unauthenticated with respect to which shop it "belongs" to). Any host application that relies on `WebhookMetadata#shop` from this gem as an authenticated tenant key — which is exactly what the shipped `Request`/`Registry`/`WebhookHandler` API encourages — can be tricked into writing or acting on data under the wrong tenant, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is high for any application that trusts `WebhookMetadata.shop`/`topic` without independently re-verifying the shop against session/install records: obtaining one valid `(body, hmac)` pair only requires installing the app once (any Shopify merchant can do this), and then any unprivileged internet user can freely resend it with rewritten headers to the app's public webhook endpoint, since headers are never covered by the signature.

### Recommendation
Include the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification (or otherwise cryptographically bind them to the body), so that tampering with any of these headers invalidates the signature. Alternatively, document clearly and enforce in the gem that `shop`/`topic` must additionally be validated by the host app against the caller's authenticated session/install record before being trusted as a tenant identifier.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and receives a legitimately signed webhook, e.g.:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`
   - Body: `{"id": 1, "note": "hello"}`
2. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only hashes `@raw_body`: [1](#0-0) 
3. Attacker resends the exact same body and HMAC to the app's webhook endpoint but changes the header `x-shopify-shop-domain` to `victim-shop.myshopify.com` (or `x-shopify-topic` to a different registered topic).
4. `Registry.process` still validates because `Utils::HmacValidator.validate` never inspected the changed headers: [6](#0-5) 
5. The host application's `handle(data:)` receives `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: <attacker-chosen>, body: <attacker-crafted>)` and processes it as if it were a genuine event for `victim-shop`, breaking the tenant boundary.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
