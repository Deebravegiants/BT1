### Title
Webhook Shop-Domain Header Not Covered by HMAC Allows Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers—none of which are covered by that signature—when constructing the `WebhookMetadata` handed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `Utils::HmacValidator.validate` computes/compares the HMAC exclusively against that signable string: [2](#0-1) 

`Registry.process` treats a passing HMAC check as proof the request "did indeed come from Shopify" (per the gem's own documentation) and then reads `request.shop`/`request.topic`/`request.webhook_id` directly from headers to build the `WebhookMetadata` delivered to the app's handler: [3](#0-2) [4](#0-3) 

The library's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify": [5](#0-4) 

and instructs the handler to key downstream work off `data.shop` as a trusted tenant identifier: [6](#0-5) 

The equality that should hold is: *shop authenticated by the HMAC == shop attributed to the delivered payload*. Because the signable string is body-only, the `shop-domain` header is never bound to the signature, so an attacker who legitimately owns a store that receives webhooks from the same app (any unprivileged merchant who installs the app) can capture a valid `(raw_body, hmac)` pair for their own shop and shop, then replay it to the app's public webhook endpoint with the `shop-domain` header (and optionally `topic`/`webhook-id`) rewritten to a victim shop. `HmacValidator.validate` still passes because it never inspected the header, and `Registry.process` dispatches the handler with `WebhookMetadata.shop` equal to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce: an unprivileged attacker (any merchant who has installed the same public app) can inject attacker-controlled webhook bodies that are attributed to an arbitrary victim shop domain. Any host application that follows the documented pattern (queueing/reacting to work keyed by `data.shop`) will act on forged data as if it originated from the victim's store—cross-tenant data injection/confusion without needing the app's `client_secret`, an access token, or any credential belonging to the victim.

### Likelihood Explanation
Exploitation only requires: (1) being any unprivileged merchant with the target app installed on their own store to obtain a legitimately-signed `(raw_body, hmac)` pair, and (2) sending an HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header. No secrets, tokens, or privileged access are required, and the webhook endpoint is by design internet-reachable.

### Recommendation
Bind the shop domain (and topic/webhook-id) into the HMAC signable string, or otherwise cryptographically tie them to the signed body, so any header tampering invalidates the signature. At minimum, document that `shop`/`topic` on `WebhookMetadata` are unauthenticated relative to the HMAC and must be cross-checked against a known/installed-shop list before being used as a tenant key.

### Proof of Concept
1. As an unprivileged merchant, install the target app on your own store `attacker.myshopify.com` and register a webhook for a topic of interest.
2. Capture the resulting legitimate webhook POST: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because `H` is HMAC(`B`, `api_secret_key`)).
3. Replay this exact `B`/`H` pair to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` (and any desired `x-shopify-topic`/`x-shopify-webhook-id`).
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `B` against `H`; `ShopifyAPI::Webhooks::Registry.process` then invokes the app's handler with `WebhookMetadata#shop == "victim.myshopify.com"`, causing the host app to process attacker-controlled data as if it came from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L10-29)
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
