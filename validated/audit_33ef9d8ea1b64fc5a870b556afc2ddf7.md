### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted despite not being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so `Utils::HmacValidator.validate` authenticates nothing except the byte content of the body. The `shop`, `topic`, `webhook_id`, and `api_version` values are all pulled directly from unauthenticated HTTP headers and are handed to the application's webhook handler as if they were verified, which breaks the identity binding: `hmac_valid(raw_body) == true` does **not** imply `shop_header == genuine_source_shop`.

### Finding Description
`Registry.process` gates the whole flow on a single check: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that string is defined as just `@raw_body`: [2](#0-1) 

`shop`, `topic`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the HMAC-signed content: [3](#0-2) 

Despite this, `Registry.process` forwards these unauthenticated header values directly into `WebhookMetadata` and calls the app's handler with them, and the gem's own documentation claims the whole request is verified as coming from Shopify ("This will verify the request did indeed come from Shopify and then call the specified handler") and shows the handler using `data.shop` to key merchant-specific work (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [4](#0-3) [5](#0-4) 

The equality that should hold but does not: `shop_used_by_handler == shop_that_produced_the_HMAC-signed_body`. Any actor who can obtain one valid `(raw_body, hmac)` pair for a topic (e.g. by installing the app on their own shop and receiving a genuine webhook, or by finding a topic/body combination whose HMAC is otherwise learnable) can resend that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` passes the attacker-chosen `shop` on to the handler as `WebhookMetadata#shop`.

### Impact Explanation
This crosses a tenant boundary: an unprivileged actor (any merchant who has installed the app, or anyone able to capture one valid signed webhook body) can cause the host application to act as if a webhook event originated from a different, victim shop. Because `data.shop` is documented and shown as the natural key applications use to route/attribute webhook processing (session lookup, per-tenant data writes, billing/inventory updates, GDPR redaction flows, etc.), this enables cross-tenant data corruption/spoofing without possessing any credential belonging to the victim shop.

### Likelihood Explanation
Exploitation requires only (a) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint, and (b) possession of one legitimately-signed `(raw_body, hmac)` pair — trivially obtainable by installing the target app on an attacker-controlled shop and letting Shopify deliver any real webhook, or by resending previously captured webhook traffic. No access token, `client_secret`, or privileged account is required, matching the "unprivileged internet user" threat model.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., verify the signature over a canonical string that concatenates the headers and the raw body, or require the application to additionally verify `shop` against a Shopify-issued value tied to the webhook subscription itself). At minimum, update `WebhookHandler`/documentation so that `data.shop` is never treated as authenticated, and provide an API to verify the shop against a known/allow-listed session before invoking the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers/receives any HTTP webhook (e.g. `orders/create`) — this produces a body `B` and Shopify-computed header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`.
2. Attacker resends the exact same `B` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed by the host app exactly as documented:
```ruby
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
)
```
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, B) == received_hmac`, ignoring the forged `shop-domain` header (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/webhooks/request.rb:36-38`).
5. The registered handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: ..., body: JSON.parse(B), ...)`, causing the host application to process attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
