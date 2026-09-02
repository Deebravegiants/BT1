### Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process` authenticate an incoming webhook solely by validating an HMAC over the raw request body. The `shop-domain` and `topic` headers — which are handed to the app's webhook handler as trusted identity fields — are never included in the signed content. Because the app's `client_secret`/`api_secret_key` is shared across every shop that has installed the app, any merchant who can trigger a legitimately-signed webhook on their own store can replay that exact `(body, hmac)` pair to the app's public webhook endpoint while forging the `shop-domain` (and/or `topic`) header to impersonate a different, unrelated tenant.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over exactly that signable string and compares it to the `hmac-sha256` header: [2](#0-1) 

`Registry.process` treats a passing HMAC check as proof the whole request "came from Shopify," then forwards `request.shop` and `request.topic` — both read straight from unauthenticated headers — into the handler: [3](#0-2) [4](#0-3) 

The gem's own documentation instructs developers to trust `data.shop` as the identifying tenant once `process` succeeds, and demonstrates using it directly to key downstream work (`shop_domain: data.shop`): [5](#0-4) [6](#0-5) 

The broken identity binding, stated as an equality: `shop authenticated by HMAC` should equal `shop delivered to the handler`, but in reality `HMAC covers = raw_body` while `shop delivered to handler = unauthenticated header value`. Since the `api_secret_key` used to compute the HMAC is a single, app-wide secret shared by all shops that install the app (not a per-shop secret), any one merchant can legitimately obtain a valid `(raw_body, hmac)` pair from a real webhook fired for their own shop, then POST that identical pair to the app's public webhook route with a forged `x-shopify-shop-domain` header naming a victim shop (and optionally a forged `x-shopify-topic`). `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` dispatches the forged identity straight to the handler.

### Impact Explanation
This is a cross-tenant identity spoofing primitive at the boundary the gem is responsible for securing (webhook authenticity). A host application that follows the gem's documented pattern — trusting `data.shop`/`data.topic` after a successful `process` call — can be made to apply attacker-supplied webhook data (order data, product data, GDPR webhook payloads, etc.) under a victim shop's identity, or attribute a forged event type to real content. This maps to "cross-tenant access," rated Critical per the given impact categories.

### Likelihood Explanation
Any user who can install the app on their own store (a normal unprivileged flow for public apps) can trigger a real webhook and capture a valid `(body, hmac)` pair for that shared secret. No access to the `api_secret_key` itself, target's access token, or TLS interception is required — only the ability to send an arbitrary HTTP POST to the app's public webhook route, which by design has no authentication other than the HMAC check being bypassed here.

### Recommendation
Bind the shop identity into the authenticated material used to accept and route webhooks. At minimum, the webhook handler contract should not accept an unauthenticated `shop` value as ground truth without cross-checking it against a shop known to have valid registration/state (e.g., verifying the shop has an active session/webhook registration in local storage before trusting `data.shop`), and the gem's documentation should not present `process` as verifying that the entire request — including the shop and topic — "did indeed come from Shopify," since only the body is signed.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker-shop.myshopify.com` and triggers a real event (e.g., creates an order) so Shopify sends a legitimately HMAC-signed webhook to the app's public endpoint:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw body>`
   - Body: `{...order json...}`
2. Attacker captures this exact raw body and HMAC value (they control network access to their own webhook receiving infrastructure, or can proxy/log it).
3. Attacker sends a new POST directly to the same public webhook route, keeping the body and `x-shopify-hmac-sha256` identical, but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over the (unchanged) body and it matches, so validation passes.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) calls the handler with `shop: "victim-shop.myshopify.com"`, and the host app — following the gem's documented pattern — processes/stores this order data as if it belonged to `victim-shop.myshopify.com`.

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
