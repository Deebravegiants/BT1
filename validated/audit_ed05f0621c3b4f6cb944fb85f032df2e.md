### Title
Webhook Shop Domain Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity solely from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, while the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates only covers the raw request body. Any caller who possesses one valid `(body, HMAC)` pair — trivially obtainable by installing the app on a shop they control — can resend that exact payload with the `shop-domain` header rewritten to a victim shop, and the signature still validates, causing the handler to process the payload under the victim shop's identity.

### Finding Description
`to_signable_string` for the webhook request only returns the raw body: [1](#0-0) 

The `shop` accessor is read straight from the (unsigned) header: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then hands `request.shop` directly to the app's handler as trusted metadata, with no cross-check that the shop domain is bound to the signed content: [3](#0-2) 

Because the HMAC key (`Context.api_secret_key`) is the app's single `client_secret`, shared across every shop that installs the app, a valid `(raw_body, hmac)` pair generated for one shop's webhook is verifiable for *any* shop-domain claim — the HMAC binds the body's bytes, not the tenant. This breaks the identity equality that should hold: `shop asserted to the handler == shop that produced the signed bytes`. Instead the code only enforces `hmac(body) == hmac(body)`, independent of `shop`.

The docs explicitly claim this call "will verify the request did indeed come from Shopify" and then use `data.shop` as trusted tenant context in the example handler: [4](#0-3) [5](#0-4) 

### Impact Explanation
An attacker who installs the target app on a shop they control (no elevated credentials required — just a normal, self-provisioned Shopify shop) can capture one legitimate webhook delivery (body + valid HMAC) for their own store. They can then replay that same body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for any other shop that has this app installed. The HMAC check still passes because it never covered the shop field, so the host application's handler will process attacker-controlled webhook content (e.g. `orders/create`, `app/uninstalled`, or mandatory compliance topics like `customers/data_request`/`shop/redact`) as if it belonged to the victim shop. Depending on how the host app uses `data.shop` (e.g. to look up the shop's session/access token and act on its behalf, or to fulfill GDPR data requests), this can produce cross-tenant data corruption, unauthorized triggered actions, or misdirected compliance/data-request processing — a cross-tenant integrity/confidentiality break.

### Likelihood Explanation
Obtaining a valid `(body, HMAC)` pair only requires installing the app on any shop (public apps allow free/dev store installs), which is well within reach of an unprivileged internet user. No access token, `client_secret`, or privileged account is needed. The replay itself is a simple HTTP POST to the app's publicly reachable webhook endpoint with a modified header.

### Recommendation
Bind the shop identity into the verified material: either include the shop domain in the HMAC-signable string used by `to_signable_string`, or have `Registry.process` independently verify that `request.shop` corresponds to a shop with a known, previously-established session/registration before dispatching to the handler, and document that consumers must not trust `data.shop` as authenticated purely because the overall HMAC check passed.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body `B` and its `x-shopify-hmac-sha256` header value `H` (valid because `H = HMAC_SHA256(client_secret, B)`, and `client_secret` is shared across all shops).
2. Replay to the app's webhook endpoint:
```
POST /webhook/callback HTTP/1.1
x-shopify-topic: orders/create
x-shopify-hmac-sha256: H
x-shopify-shop-domain: victim.myshopify.com
x-shopify-webhook-id: <any>

B
```
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(client_secret, B)` and matches `H` — validation succeeds because it never inspects `x-shopify-shop-domain`. [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-chosen body `B`, and the host application processes it believing it originated from `victim.myshopify.com`.

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
