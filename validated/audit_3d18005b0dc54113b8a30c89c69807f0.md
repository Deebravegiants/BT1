### Title
Webhook shop identity is not cryptographically bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the HMAC over the raw request body, then dispatches to the app's handler using a `shop` value taken from an HTTP header that is never included in that HMAC computation. This breaks the equality `shop bound by HMAC == shop delivered to handler`, allowing a party who possesses one valid `(raw_body, hmac)` pair to relabel it as belonging to any other shop.

### Finding Description
`Registry.process` validates authenticity like this: [1](#0-0) 

The validation call is `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`. For `Webhooks::Request`, that signable string is defined as just the raw body, not any header: [2](#0-1) [3](#0-2) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated HTTP headers: [4](#0-3) 

`process` then hands `request.shop` (an unauthenticated header value) directly to the app's handler as the identity of the tenant the payload belongs to: [5](#0-4) 

The gem's own documentation asserts that calling `Registry.process` "will verify the request did indeed come from Shopify," implying the `shop` field handed to the handler is trustworthy, when in fact only the body bytes are verified: [6](#0-5) 

Because the HMAC secret (`api_secret_key`) is shared across all shops/tenants of a single app, any legitimate webhook delivery the attacker can observe for their own shop (or any shop) yields a `(raw_body, hmac)` pair that remains valid under `HmacValidator.validate` for that exact body no matter what `shop-domain`/`topic`/`webhook-id` header values accompany it, since those fields never enter the signable string.

### Impact Explanation
An unprivileged internet user who owns any shop with the app installed (or who otherwise captures a single valid webhook body+HMAC pair) can replay that payload against the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header identifying a different, victim tenant. The app's handler (per the documented contract) trusts `data.shop` as the authenticated tenant identity and will act on it — e.g. writing data, triggering `app/uninstalled` cleanup, or updating billing/session state — under the wrong shop record. This is a cross-tenant access break: the impact matches the Critical category "cross-tenant access," since the shop boundary that should be enforced by the HMAC is not actually enforced.

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint and possession of one legitimately-signed webhook body (trivially obtainable by installing the target app on an attacker-controlled test shop, which produces genuinely-signed webhook deliveries). No access token, `client_secret`, or privileged account is needed — only the ability to send an HTTP POST with a crafted header, which is exactly the "unprivileged internet user" threat model in scope.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed payload, or otherwise independently bind the header-derived `shop` value to a value verified via a signed/authenticated channel before dispatching to handlers. At minimum, document that `data.shop` in `WebhookMetadata` is unauthenticated relative to the HMAC check, and require app authors to cross-check `data.shop` against a shop known to have been legitimately provisioned before trusting it for any state-changing action.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook delivery, e.g. `orders/create`, recording `raw_body` and the `x-shopify-hmac-sha256` header Shopify computed over that body with the app's shared `api_secret_key`.
2. Replay the exact same request to the app's webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` unchanged, but set `x-shopify-shop-domain: victim.myshopify.com` (and any desired `x-shopify-topic`).
3. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches, so `Registry.process` proceeds and calls the handler with `data.shop == "victim.myshopify.com"`, `data.body` == attacker's own order data — the app now processes attacker-supplied data as if it originated from the victim's shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** docs/usage/webhooks.md (L125-135)
```markdown
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
