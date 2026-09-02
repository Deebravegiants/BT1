### Title
Webhook shop-domain identity spoofing via unsigned header — cross-tenant webhook processing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates only the raw webhook body against the HMAC signature. The `shop` (and `topic`, `webhook_id`, `api_version`) values are read straight from HTTP headers that are never included in the signed payload. After HMAC validation succeeds, the unauthenticated `shop` header is forwarded into `WebhookMetadata#shop`, which the library's own documentation instructs developers to use as the authoritative tenant identifier for shop-scoped processing.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled from headers that are not part of the signed string: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e. the body) against the HMAC, never the shop header: [3](#0-2) 

`Registry.process` performs this HMAC check and then, without any further validation, passes `request.shop` straight into `WebhookMetadata`, which is handed to the app's handler: [4](#0-3) 

`WebhookMetadata#shop` is a plain `String` field with no cross-check against the signed body: [5](#0-4) 

The identity binding broken here is:
`shop bytes verified by HMAC` (none — HMAC covers body only) ≠ `shop value acted on by the handler` (`request.shop` / `data.shop`, taken from an unsigned header).

The gem's own docs instruct developers to trust `data.shop` for shop-scoped work (e.g. enqueuing per-shop jobs), reinforcing that this field is meant to identify the tenant: [6](#0-5) [7](#0-6) 

### Impact Explanation
An app's `api_secret_key` is shared across all shops that install the app — it is not per-shop. Any unprivileged internet user who installs the app on a shop they control receives legitimate webhooks from Shopify with a valid HMAC computed over the body using that shared secret. Because the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) headers are not covered by the signature, that same attacker can replay the captured request to the app's webhook endpoint while substituting any victim shop's domain in the shop header. `Registry.process` will accept it (HMAC still matches the unmodified body) and hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop. Any host application that follows the documented pattern of keying shop-scoped state (jobs, database writes, session lookups) off `data.shop` will attribute attacker-controlled webhook content to a different tenant — a cross-tenant integrity/data-injection issue.

### Likelihood Explanation
Requires no credentials, no access token, no TLS interception, and no social engineering — only the ability to install the target app on any shop (a normal, unprivileged action available to any merchant/developer) and replay one already-received, validly-signed webhook with a modified header. This is a low bar for an "unprivileged internet user" relative to other tenants of the same app.

### Recommendation
Include the shop domain (and topic/webhook id) in the HMAC-signed material, or otherwise cryptographically bind the shop identity to the signature verified by `HmacValidator`, so that `WebhookMetadata#shop` cannot be forged independently of the signed payload. At minimum, document explicitly that `data.shop` is unauthenticated and must be cross-validated by the host application against the shop's own subscription/session records before being trusted for tenant-scoped actions.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`, a shop they control.
2. Attacker triggers/receives a legitimate webhook, e.g. `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body computed with the app's shared secret>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - raw body: `{"id": 1, ...attacker-crafted content...}`
3. Attacker replays the exact same raw body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header set; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the (unchanged) body against the (unchanged) HMAC — validation passes.
5. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker content>, ...)` and, following the documented pattern, processes/persists the attacker's content under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
```

**File:** docs/usage/webhooks.md (L123-136)
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
```
