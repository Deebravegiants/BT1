## Title
Webhook shop domain is not covered by the HMAC signature, enabling cross-tenant shop-identity forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity using `Utils::HmacValidator.validate(request)`, but the HMAC signature only covers the raw request body, not the `shopify-shop-domain` header. `Request#shop` is read directly from that unauthenticated header and passed straight through to the app's webhook handler as the tenant identifier, so a valid signature for one shop's payload can be paired with an arbitrary attacker-chosen shop domain.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) 
`to_signable_string` returns only `@raw_body`: [2](#0-1) 
while `shop` is pulled straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC and, if it passes, immediately trusts `request.shop` to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop attested by the HMAC-signed payload == shop used to attribute the webhook to a tenant`

but the actual binding is:
`shop verified (HMAC over raw_body only) != shop consumed (unauthenticated header value)`

Any party that can obtain one genuinely Shopify-signed webhook body (e.g., by installing the app on their own store, a normal unprivileged action) can replay that exact body with a forged `shopify-shop-domain` header pointing at a victim shop. The signature still validates because it never covered the header, so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the victim's domain while the body is the attacker's own shop data.

The gem's own documentation reinforces that this field is expected to be trustworthy after verification: it states `process` "will verify the request did indeed come from Shopify" and lists `shop` as one of the data fields handlers can rely on, with no caveat that it must be independently re-validated against an installed-shop list: [5](#0-4) [6](#0-5) 

### Impact Explanation
Applications built on this gem's documented API (`data.shop`) commonly use the webhook's `shop` value to select which tenant's session/database record to update (e.g., `shopify_app`'s webhooks jobs key off `shop_domain`). Because the shop identity is not bound to the signed payload, an attacker who controls one legitimately-installed shop can forge webhooks that are misattributed to any other shop domain, corrupting or exfiltrating data across tenant boundaries — a cross-tenant access impact.

### Likelihood Explanation
Any unprivileged internet user can install the target app on a free/trial Shopify development store, causing Shopify to deliver at least one validly HMAC-signed webhook to the app's registered endpoint for their own shop. The attacker only needs to intercept/replay that raw body with a modified shop header value to a target endpoint they control network access to (their own webhook receiver route), since the HMAC never covers headers. No access token, `client_secret`, or privileged account is required.

### Recommendation
- Do not trust the `shopify-shop-domain` header for tenant attribution unless it is cryptographically bound to the signed content, or
- Require host applications to cross-check `request.shop` against an already-registered/installed shop record (with an offline access token on file) before processing, and document this as a mandatory step rather than implying HMAC validation alone establishes shop identity.
- Consider including the shop domain in the webhook signature verification, or exposing a helper that rejects webhooks for shops with no known installation.

### Proof of Concept
```ruby
# Attacker owns "attacker.myshopify.com" with the target app installed,
# and receives a legitimately Shopify-signed webhook:
raw_body = '{"id":1}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# Attacker replays the exact same signed body but swaps the shop header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac), # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds because it only checks raw_body,
# and the handler receives WebhookMetadata#shop == "victim-shop.myshopify.com"
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
