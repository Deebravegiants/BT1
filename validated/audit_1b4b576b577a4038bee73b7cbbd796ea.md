### Title
Webhook `shop` (and `topic`/`webhook-id`) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then hands these unverified header values to the app's handler as if they were authenticated, breaking the binding between "bytes verified" and "bytes trusted for tenant identity."

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhooks that method returns only `@raw_body`: [1](#0-0) 

None of the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers are included in the signed string — they are parsed straight out of the raw headers hash with no cryptographic binding: [2](#0-1) 

`Registry.process` only checks the HMAC of the body, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The documented usage pattern explicitly tells integrators to key their business logic (e.g. job routing, tenant lookup) off `data.shop`, treating it as an authenticated field once `Registry.process` returns without error: [4](#0-3) [5](#0-4) 

Because the webhook signing secret (`Context.api_secret_key`, the app's `client_secret`) is the **same for every shop that has installed the app**, any unprivileged user who installs a public app on their own store receives genuinely-signed webhook deliveries (valid HMAC over some body). That user can replay the exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still succeeds because it never looks at the header, and the handler executes with `data.shop` set to the victim's domain and `data.body` fully attacker-controlled.

### Impact Explanation
This breaks the identity binding "shop authenticated == shop the app stored/processes for," letting an attacker who controls one shop's installation forge webhook events attributed to a different shop of their choosing. Depending on how the host app uses `data.shop` (e.g., to look up the tenant's session/record and merge in `data.body`), this enables cross-tenant data injection/corruption — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires no special privilege beyond being able to install the target public app on a shop the attacker controls (an "unprivileged internet user" scenario), which is the normal way any merchant obtains a validly-signed webhook body/HMAC pair for that app. No access to `api_secret_key` or the victim's tokens is needed.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed payload used by `to_signable_string`, or otherwise cryptographically bind them (e.g., by validating `shop-domain` against the app's own installed-shop store rather than trusting the header verbatim). At minimum, update documentation to make clear `data.shop` is not covered by the HMAC and must be independently authenticated by the host app before use.

### Proof of Concept
1. Attacker installs the target public app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery, e.g. `orders/create`, with body `B` and header `shopify-hmac-sha256: H` (valid because `H = HMAC_SHA256(client_secret, B)`).
2. Attacker replays the request to the app's webhook endpoint, keeping `raw_body = B` and `shopify-hmac-sha256 = H`, but changes `shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `B` and succeeds.
4. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, causing the host app to process attacker-controlled data as if it belonged to `victim.myshopify.com`.

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
