### Title
Webhook `shop` header is trusted for tenant identification but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` validates a webhook's authenticity by HMAC-signing only the raw request body, while the `shop` (tenant identifier), `topic`, and `webhook_id` are taken directly from unauthenticated HTTP headers and forwarded to the app's handler as trusted values. Because the HMAC does not bind the `shop` field, a request whose body/HMAC pair was legitimately obtained for one shop can be replayed with a different `shop-domain` header, and it will still pass validation while asserting a different tenant.

### Finding Description
`Registry.process` verifies a webhook exclusively via:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
``` [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature over `request.to_signable_string`, which for `Webhooks::Request` is defined as:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers that are entirely outside the signed data:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [3](#0-2) 

After the HMAC check succeeds, `process` passes this unauthenticated `shop` value straight into the handler as an already-"validated" tenant identifier:
```ruby
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [4](#0-3) 

The identity binding the gem implicitly asserts is:
`hmac_valid(raw_body, secret) == true` ⇒ `shop_header == originating_shop`

but the actual guarantee provided is only:
`hmac_valid(raw_body, secret) == true` ⇒ `raw_body` was produced by an entity holding `api_secret_key` (i.e., Shopify, for *some* shop that installed this app) — nothing about `shop_header` is proven.

Documentation instructs handler authors to trust `data.shop` directly (`puts "... shop: #{data.shop} ..."`), reinforcing that this library-level guarantee is exactly what's broken. [5](#0-4) 

### Impact Explanation
An attacker who can install the same app on their own (attacker-controlled) shop receives legitimate webhook deliveries with a valid HMAC computed over the body using the shared `api_secret_key`. Because `shop-domain` is not part of the signed payload, the attacker can capture one such `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim merchant's domain). The request still passes `Utils::HmacValidator.validate`, and the handler receives `data.shop` set to the attacker-chosen victim domain. If the host app uses `data.shop` to look up per-tenant state, trigger actions, or write data keyed by shop (as the documented usage pattern suggests), this results in cross-tenant data confusion/corruption — an app processing data as if it came from a different merchant than actually sent it. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is bounded by the requirement that the attacker be able to install the app on a shop they control (a normal, low-privilege action for any Shopify Partner/developer testing an app, or any store owner who installs a public app) in order to harvest a valid `(body, hmac)` pair. No possession of `api_secret_key`, access tokens, or victim credentials is required — only the ability to receive one webhook delivery and replay it with a forged header, both of which are within reach of an unprivileged internet user interacting with the app's public webhook endpoint.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-verified surface (or independently re-derive/verify the shop from a Shopify-issued, signed source such as the API version negotiation or a lookup against the app's own known-installed-shops list) before trusting `request.shop` in `Webhooks::Request`/`Registry.process`. At minimum, the gem should document clearly that `shop` is unauthenticated relative to the webhook HMAC and must be cross-checked by the host app against its own shop/session store before being used for any tenant-scoped action.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` (any unprivileged developer/store action) and capture a legitimate webhook POST, e.g. `orders/create`, noting the raw body `B` and header `x-shopify-hmac-sha256: H` (valid for secret `S` since `H = HMAC-SHA256(S, B)`).
2. Replay the exact same body `B` and header `H` to the app's registered webhook path, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(S, B)` — since only `B` is signed — and it matches `H`, so [2](#0-1)  validation passes.
4. `Registry.process` invokes the handler with `WebhookMetadata` where `shop == "victim-shop.myshopify.com"` [4](#0-3) , even though the payload actually originated from `attacker-shop.myshopify.com`, achieving cross-tenant confusion in the host application's webhook handling.

### Citations

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
