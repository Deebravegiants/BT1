### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC verified by `Registry.process` binds solely to the request body. The `shop` (and `topic`/`api_version`/`webhook_id`) values are read directly from unauthenticated headers and are never part of the signed material, yet they are trusted and forwarded to the host app's handler as the tenant identity for the webhook.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates the request by calling `Utils::HmacValidator.validate(request)`, which computes `HMAC-SHA256(secret, request.to_signable_string)` and compares it to `request.hmac`: [1](#0-0) [2](#0-1) 

`to_signable_string` only returns the raw body: [3](#0-2) 

But `shop` is read straight from the `shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed payload at all: [4](#0-3) 

`Registry.process` then passes this unauthenticated `shop` value straight into `WebhookMetadata`, which the host app's handler uses as the tenant identifier (per the gem's own documented usage): [5](#0-4) [6](#0-5) 

The binding that should hold is: `shop_bound_by_hmac == shop_used_by_handler`. In practice the signed material never includes `shop`, so this equality is broken — `shop` is fully attacker-controlled input as long as the attacker can produce *any* valid `(body, hmac)` pair for the shared `api_secret_key`.

Since `api_secret_key` is a single app-wide secret shared across all installed shops, any unprivileged user who installs the app on their own store (or otherwise triggers a legitimate webhook delivery, e.g. via `orders/create` on their own shop) can capture a genuine `(raw_body, hmac)` pair. They can then replay that exact body+hmac directly to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value for a victim shop. `HmacValidator.validate` will still pass (it only checks the body against the hmac), and `Registry.process` will hand the attacker-chosen `shop` value to the handler as if it were an authentic webhook for that victim shop.

### Impact Explanation
This breaks the tenant-identity binding for webhook processing: an unprivileged user with access to their own installed shop can forge webhook deliveries claiming to originate from any other shop, since the `shop` field is trusted but never authenticated by the HMAC. Depending on how the host app uses `data.shop` (as most integrations do, per this gem's own documented pattern of `perform_later(shop_domain: data.shop, ...)`), this enables cross-tenant data injection/corruption — e.g. triggering order/product-update processing against another merchant's tenant record using attacker-supplied body content. This matches the "cross-tenant access" criteria.

### Likelihood Explanation
Likelihood is high for any app that exposes its webhook endpoint publicly (as required by Shopify's webhook delivery model) and relies on `Request#shop` for tenant routing without independently verifying that the shop is one that installed the app and is entitled to trigger that topic. No secrets beyond the ability to install the app on one's own store (freely available to any developer) are required to obtain a valid `(body, hmac)` pair.

### Recommendation
Include `shop` (and ideally `topic`) in the signed/verified material, or independently verify that the `shop` header value corresponds to a shop with an active session/installation for the given topic before dispatching to the handler. At minimum, document prominently that `Request#shop` is unauthenticated and that host apps must not trust it without cross-checking against known installed shops.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers for `orders/create` webhooks.
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid_hmac>` and some `raw_body`.
3. Attacker captures this `(raw_body, valid_hmac)` pair (they control the receiving endpoint or can intercept it).
4. Attacker replays a POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256: <valid_hmac>`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against `valid_hmac` — validation succeeds.
6. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled body>, ...)` and processes it as if it were genuine data for `victim-shop.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** docs/usage/webhooks.md (L12-26)
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
```
