### Title
Webhook shop identity not bound to HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, while the `shop` identity that the app's handler relies on for tenant attribution is read directly from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then passes this unauthenticated `shop` value straight into the handler, breaking the binding between "verified as genuinely from Shopify" and "verified as belonging to this shop."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is taken verbatim from an HTTP header that is never part of the signed content: [2](#0-1) 

`HmacValidator.validate_signature` confirms only that the *body* matches a signature computed with the app's secret — it has no knowledge of, and does not bind, the `shop` header: [3](#0-2) 

`Registry.process` performs this HMAC check and then forwards the unauthenticated `request.shop` directly to the app's handler as the trusted tenant identity: [4](#0-3) 

The gem's own documentation reinforces this false guarantee, stating that `Registry.process` "will verify the request did indeed come from Shopify" and describing `data.shop` simply as "The shop domain of the webhook" with no caveat that it is unauthenticated, and shows an example (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`) that treats `data.shop` as a trustworthy tenant key: [5](#0-4) [6](#0-5) 

This is the identity-binding failure described by the bug class: `shop` is "a field acted on but not covered by the HMAC." The equality that should hold — `hmac_valid(body, secret) ⟺ (body, shop_header)` genuinely originated together from Shopify for that shop — does not hold; only the body is bound to the secret, the `shop` header floats free.

### Impact Explanation
An attacker who has legitimately installed the app on their **own** shop (an ordinary, unprivileged action) can trigger any subscribed webhook event (e.g. `orders/create`) for their own store. Shopify will deliver a request to the app's public webhook endpoint with a body and HMAC signed using the app's `client_secret` — content the attacker fully controls indirectly (their own order data) and can capture (it is delivered to an endpoint they control or can proxy/replay from). The attacker can then re-send that exact body+HMAC pair to the same public endpoint while substituting the `X-Shopify-Shop-Domain` header for an arbitrary victim shop's domain. `HmacValidator.validate` still passes (the body and secret are unchanged), so `Registry.process` invokes the handler with `data.shop` set to the victim's domain and `data.body` containing attacker-controlled content. Any host app following the documented pattern of using `data.shop` to select the tenant/session under which the webhook payload is processed will apply attacker-controlled data under a victim shop's identity — a cross-tenant data-injection/confusion primitive, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
No possession of `api_secret_key`, access tokens, or privileged credentials is required — only the ability to install the app on any shop (which any Shopify merchant can do) and to send a direct HTTP request to the app's public webhook callback URL with attacker-chosen headers, something not restricted by this gem. The victim's shop domain is a public string.

### Recommendation
Include the `shop` (and `topic`/`webhook_id`) values in the HMAC-signed content, or otherwise cryptographically bind the header-derived shop to the signed body (e.g., verify the shop against a shop known to have a currently active webhook registration/session before dispatching), rather than trusting `X-Shopify-Shop-Domain` unconditionally once only the body's HMAC validates.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and registers a webhook for a topic (e.g. `orders/create`).
2. Attacker triggers the event on their own store; Shopify sends `POST /callback/orders/create` to the app with a valid `X-Shopify-Hmac-Sha256` computed over the raw JSON body using the app's `client_secret`.
3. Attacker captures this request (body + HMAC) and re-issues an identical `POST` to the same endpoint, only replacing header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` and `Registry.process` validate the HMAC via `HmacValidator.validate`, which only checks `@raw_body` against the secret — validation succeeds.
5. The registered handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, exactly as constructed in `Registry.process`: [7](#0-6) 
6. If the host app follows the documented pattern of dispatching work keyed on `data.shop` (as shown in the gem's own docs example), attacker-controlled order/webhook data is now processed under the victim shop's tenant context.

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

**File:** docs/usage/webhooks.md (L10-27)
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
