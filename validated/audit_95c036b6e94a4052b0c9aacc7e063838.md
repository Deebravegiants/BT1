### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `#shop` is read directly from the unauthenticated `X-Shopify-Shop-Domain` / `shopify-shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then forwards the unauthenticated `shop` value to the app's webhook handler as the trusted tenant identifier. Because Shopify signs webhooks with the app-wide `api_secret_key` (the same key for every shop that installs the app), the signature proves only "this body was signed with our app secret," not "this body came from shop X." This breaks the identity binding `authenticated(body) == tenant(shop)` that host apps are told to rely on.

### Finding Description
The webhook signature verification path is:
- `Utils::HmacValidator.validate(request)` computes the HMAC using `request.to_signable_string`, which is defined as just `@raw_body`: [1](#0-0) 
- `#shop` is parsed straight from request headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 
- `Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed into the handler: [3](#0-2) 
- `WebhookMetadata.shop` is the field host apps are explicitly told to use to route/attribute the webhook to a shop: [4](#0-3) 
- The gem's own documentation instructs apps to key persisted/queued work off `data.shop` as the authoritative shop identifier: [5](#0-4) 

Since the HMAC secret (`api_secret_key`) is per-app, not per-shop, any merchant who has installed the app can obtain genuinely-signed webhook bodies for their own shop (by performing ordinary actions that trigger webhooks, e.g. updating a product/order with attacker-chosen field values) and then replay that exact signed body to the app's webhook endpoint while swapping only the `shop-domain` header to name a different shop that also has the app installed. `Utils::HmacValidator.validate` still passes because the signature only covers the body, and `Registry.process` hands the forged `shop` value to the app's handler as if Shopify itself vouched for it.

### Impact Explanation
This is a cross-tenant identity-binding break: data validated as authentic (the HMAC-signed body) is decoupled from the identity acted upon (the `shop` field the handler trusts for tenant attribution). An attacker-controlled merchant install can cause the app to process attacker-influenced webhook content under another merchant's shop identity, corrupting or exfiltrating cross-tenant state in any app that follows this gem's documented pattern of trusting `data.shop`. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is High for any app built on this gem: no privileged credentials, TLS interception, or social engineering are required — only a standard, unprivileged merchant installation of the target app (which by design can be done by any Shopify merchant), plus the ability to replay a captured HTTP request with one header changed. The vulnerable code path (`to_signable_string` excluding headers) is exercised on every webhook the gem processes.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-verified signable string, or otherwise cryptographically tie the claimed shop to the signed payload, so that `Utils::HmacValidator.validate` fails if the shop header is altered independently of the signed body. At minimum, document prominently that `data.shop` is not authenticated by the HMAC and must not be used as a sole tenant boundary, and cross-check it against the shop associated with the specific webhook subscription/session when dispatching to handlers.

### Proof of Concept
1. App is installed on Shop A and Shop B (both legitimate, unprivileged installs of the same app).
2. Attacker controls Shop A. They perform an action (e.g. update an order note) that causes Shopify to send a genuinely HMAC-signed webhook body `B` with header `X-Shopify-Shop-Domain: shop-a.myshopify.com` to the app's webhook endpoint.
3. Attacker intercepts/replays this exact request to the same endpoint, changing only the header to `X-Shopify-Shop-Domain: shop-b.myshopify.com`, leaving `raw_body` (and thus the HMAC) untouched.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only checks `raw_body`: [1](#0-0) 
5. `Registry.process` constructs `WebhookMetadata.new(... shop: request.shop ...)` using the forged header, and the app's handler processes attacker-supplied content as if it were legitimately from Shop B: [6](#0-5)

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

**File:** docs/usage/webhooks.md (L12-29)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
