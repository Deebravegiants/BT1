### Title
Webhook cross-tenant shop spoofing — `shop-domain` header not covered by HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` passes, and then hands the request's `shop` value to the app's handler as an authenticated tenant identifier. In reality the HMAC only covers the raw JSON body, not the `shop-domain` header, so the `shop` value is fully attacker-controllable independent of the signature check.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cross-check against anything cryptographically bound to the signature: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, immediately forwards `request.shop` to the app's handler as the authenticated tenant identity for that payload: [3](#0-2) 

The documented app-development pattern instructs developers to trust `data.shop` coming out of `process` (e.g. to route/enqueue per-shop work), reinforcing the assumption that "HMAC valid" implies "shop field authentic": [4](#0-3) [5](#0-4) 

This breaks the intended identity binding:
`HMAC-verified(raw_body) == HMAC-verified(shop-domain header)`
which is false — the equality actually enforced is only `HMAC-verified(raw_body)`, while `shop` is parsed unauthenticated. Compare this to `Auth::Oauth::AuthQuery#to_signable_string`, where `shop` (along with `code`, `state`, `host`, `timestamp`) *is* included in the signable string and thus is properly bound to the signature: [6](#0-5) 

That contrast confirms the webhook path is the outlier: an identity field (`shop`) is acted on by the handler but excluded from the value the HMAC actually authenticates.

### Impact Explanation
Any unprivileged user can create their own store, install the app, and let Shopify deliver a genuine webhook with a body B and a valid HMAC computed over B using the app's real `api_secret_key`. The attacker does not need the secret itself — they only need to capture that one legitimately-delivered request (their own webhook, sent to their own app installation). They can then replay the identical `raw_body`/HMAC pair directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the victim's domain instead of the attacker's own. Any app logic that uses `data.shop` to select which merchant's session/record to write to, update inventory/orders for, or attribute billing/audit events to is then operating on attacker-supplied data under a spoofed tenant identity — a cross-tenant data-integrity/confidentiality violation.

### Likelihood Explanation
High for the mechanics (no cryptographic material beyond one's own legitimately-obtained webhook is required, and the endpoint is a public HTTP webhook receiver by design). The magnitude of the impact depends on how much a given host app trusts `data.shop` without additional server-side session/shop cross-validation, which the gem's own documentation encourages developers to do directly.

### Recommendation
Include the shop-domain header value in the HMAC-signable payload the gem verifies (or otherwise cryptographically bind `shop` before exposing it to handlers), e.g. by validating that the `shop` on the request corresponds to a shop with a currently valid installed session/access token before invoking the handler, rather than relying on the raw-body HMAC alone to imply the shop identity is trustworthy. At minimum, document explicitly that `data.shop` from `WebhookMetadata` is unauthenticated and must be independently verified against known installed sessions before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on their own dev/test shop `attacker.myshopify.com`, causing Shopify to send a real webhook (e.g. `orders/create`) to the app's registered callback URL with headers `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`, and JSON body `B`.
2. Attacker captures this HTTP request (e.g., via their own reverse proxy, browser devtools if same host, or a local test webhook receiver such as ngrok pointed at their own tooling instead of the real app — any means of intercepting their own outbound traffic).
3. Attacker resends the exact same body `B` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` parses `shop` as `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes HMAC over `B` — the header is never part of `to_signable_string`. [7](#0-6) 
6. The registered handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: B, ...)`, and any app logic keyed on `data.shop` now acts as though this attacker-controlled payload belongs to the victim shop.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
