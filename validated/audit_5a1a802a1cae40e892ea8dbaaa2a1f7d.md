## Title
Webhook `shop` (and `topic`/`webhook-id`) attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw HTTP body when validating a webhook, but the `shop` value that the gem hands to the app's webhook handler (used to attribute/act on the payload for a specific merchant) is taken from an unauthenticated request header and is never included in the signed data.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop`, `#topic`, `#webhook_id` and `#api_version` are read straight from caller-supplied headers with no cryptographic binding to the HMAC at all: [2](#0-1) [3](#0-2) 

`Registry.process` validates only that the body's HMAC matches (via `Utils::HmacValidator.validate`, which just compares `to_signable_string` against the secret), then dispatches the handler using the *unverified* `request.shop`/`request.topic`: [4](#0-3) 

The identity binding broken is:
`shop attributed to the processed webhook payload` ≠ `shop actually covered by the HMAC signature` (the signature covers only `raw_body`).

Because only the body bytes are signed, any party who has legitimately received one authentic webhook delivery (e.g., a merchant who has the app installed on their own store, or anyone who has captured a body+HMAC pair for a topic whose body content is constant/predictable, such as `app/uninstalled` or an empty-body topic) can replay that exact `raw_body` + `x-shopify-hmac-sha256` pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` will still pass because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the attacker-chosen shop.

### Impact Explanation
This crosses a tenant boundary: an unprivileged internet user, without the app's `client_secret` or any access token, can make a merchant application process/attribute webhook data to a shop of their choosing rather than the shop that actually generated it. Depending on how the host app's registered handler consumes `data.shop` (e.g., to update per-tenant records, trigger per-tenant business logic, or invalidate/refresh sessions), this enables cross-tenant data confusion/injection.

### Likelihood Explanation
Exploitation requires only one legitimately-received `(raw_body, hmac)` pair — obtainable by installing the app on any shop the attacker controls (a normal, unprivileged action) — and a single unauthenticated POST to the app's public webhook endpoint with a forged `shop-domain` header. No secret material, access token, or privileged access is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the data verified by the HMAC, or otherwise cryptographically bind the `shop` value that's exposed to handlers to the same trust boundary as the body signature, so a valid signature for shop A's payload cannot be replayed and attributed to shop B.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker-shop.myshopify.com`; capture a genuine webhook delivery, its raw body, and its `x-shopify-hmac-sha256` header (both are valid and verifiable with the app's secret).
2. Send a POST to the app's public webhook endpoint with the captured `raw_body` and `x-shopify-hmac-sha256` unchanged, but with `x-shopify-shop-domain` set to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` (via `Utils::HmacValidator.validate`) accepts the request because only `raw_body` is checked [1](#0-0) , and the handler is invoked with `shop: "victim-shop.myshopify.com"` [5](#0-4) , despite the payload never having been produced by or verified against that shop.

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
