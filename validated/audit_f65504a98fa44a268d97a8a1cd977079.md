### Title
Webhook `shop` (and `topic`) identity fields are trusted without being covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, but the HMAC in this gem is computed **only over the raw request body**, not over the `x-shopify-shop-domain` (or `x-shopify-topic`) header that the library subsequently uses as the tenant identifier passed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic` are pulled straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the body's authenticity/integrity) and then immediately hands `request.shop` and `request.topic` to the host application's handler as trusted identity data: [3](#0-2) 

The identity binding that should hold is:
`HMAC_valid(secret, signed_bytes) == true` must imply `signed_bytes ⊇ {shop, topic}` (the values acted upon). Here `signed_bytes = raw_body` only, so the equality is broken: the HMAC proves nothing about which shop/topic the event is attributed to. The library's own documentation reinforces the false assumption that `process` "will verify the request did indeed come from Shopify" as a whole, and instructs handlers to key downstream data (jobs, DB records) by `data.shop`: [4](#0-3) [5](#0-4) 

### Impact Explanation
Any user who has legitimately installed the app on their own store receives real Shopify webhooks with a valid `(body, hmac)` pair for their own shop — this pair is fully attacker-known, since the attacker controls the store generating the event. Because `shop-domain` is not part of the signed bytes, that same attacker can replay the identical body+hmac to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop). `HmacValidator.validate` still succeeds (body unchanged), and `Registry.process` forwards `shop: <victim-domain>` to the host handler, which — per this gem's own documented usage pattern — uses that value as the tenant key to persist/process data. This crosses the tenant boundary the gem is supposed to enforce, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
No credentials, access tokens, or `client_secret` are required. The only prerequisite is that the attacker can install the app on a store they control (a standard, unprivileged action for any Shopify merchant) to obtain one valid `(body, hmac)` pair, and then submit a normal unauthenticated HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header. This requires no interception of TLS traffic and no knowledge of the app's secret.

### Recommendation
Bind the identity headers into the signed material actually verified, or otherwise cryptographically tie `shop`/`topic` to the HMAC before trusting them:
- Include the `shop-domain` and `topic` header values (not just the raw body) in the string that `HmacValidator` verifies, matching Shopify's guidance that the HMAC only guarantees body integrity — the shop domain must additionally be cross-checked against a known, previously-registered shop for that webhook subscription (e.g., compare against the shop that owns the corresponding `webhook_id`/registration) before it is used as a tenant key.
- At minimum, update documentation to explicitly warn that `data.shop`/`data.topic` are **not** authenticated by the HMAC and must be independently verified by the host app (e.g., against an existing session/shop record) before being used to key any state.

### Proof of Concept
1. Install the target app on an attacker-controlled store `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) to capture a legitimate `raw_body` and its corresponding `x-shopify-hmac-sha256` value.
2. Replay that captured `(raw_body, hmac)` pair to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` (and optionally forge `x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `raw_body`.
4. The handler in `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` receives `shop: "victim.myshopify.com"`, and any host-app logic keyed on `data.shop` (as shown in the gem's own docs) now operates on attacker-supplied data under the victim's tenant identity.

### Citations

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
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
```

**File:** docs/usage/webhooks.md (L123-135)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
