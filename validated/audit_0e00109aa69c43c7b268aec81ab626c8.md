### Title
Webhook shop-domain spoofing via HMAC that does not cover the tenant identifier - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw request body, then trusts the `shop-domain` HTTP header — which is *not* covered by that HMAC — as the tenant identifier passed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which plays no part in the signable string and is therefore not authenticated by the HMAC at all: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over the raw body only) and, once that passes, forwards `request.shop` unchanged to the app's webhook handler as the tenant identity for the event: [3](#0-2) 

The documented integration pattern constructs the `Request` directly from the raw HTTP headers of the inbound call and hands it to `Registry.process`, with no additional binding of `shop` to the signed payload: [4](#0-3) 

This breaks the identity binding `shop authenticated == shop used as the tenant key`: the HMAC only proves "these raw bytes were signed with the app's `client_secret`" — it says nothing about which shop the request claims to be for. The `shop` value acted upon by `WebhookMetadata` (and thus by the host app's `handle` logic, e.g. `data.shop` in the documented handler) is an independent, attacker-controllable header.

### Impact Explanation
Any party who can obtain one legitimate `raw_body` + `hmac-sha256` pair for the shared app `client_secret` (e.g., a merchant who installs the app on their own shop and observes their own webhook deliveries) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value naming a *different*, victim shop. `Utils::HmacValidator.validate(request)` will still succeed because it only checks the raw body bytes, and `Registry.process` will dispatch the (attacker-chosen, victim-attributed) `WebhookMetadata` to the app's handler. Depending on how the host app trusts `data.shop` (as most integrations, per the documented pattern, use it directly to select the tenant record to update), this enables cross-tenant data injection/corruption — a Critical-class cross-tenant access issue arising purely from this gem's webhook verification primitive.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own installation of the target app (any merchant can install most public apps) to capture one valid signed webhook, and (2) the ability to send an arbitrary HTTP request to the app's public webhook URL with a modified header — both are available to an unprivileged, uncredentialed actor with no access token, no `client_secret`, and no privileged account. The gem's `Webhooks::Request`/`Registry` API gives no mechanism to bind `shop` to the signature, so any host app that follows the documented pattern is affected.

### Recommendation
Include the shop domain (and topic/webhook id) in the HMAC-signed payload verification, or otherwise cryptographically bind `Request#shop` to the authenticated body before exposing it via `WebhookMetadata`. At minimum, document that `Request#shop` is unauthenticated data and must never be relied upon as a tenant boundary without independent verification (e.g., cross-checking against a known session/shop record) by the host application.

### Proof of Concept
1. Install the vulnerable app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) and capture the raw POST body and the `X-Shopify-Hmac-Sha256` header sent by Shopify — both are valid for the app's shared `client_secret`.
2. Replay that exact body to the app's webhook endpoint, keeping the `X-Shopify-Hmac-Sha256` header unchanged but overwriting `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` succeeds (it only hashes `raw_body`), and `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to process attacker-supplied data under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L125-136)
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
```
