### Title
Webhook `shop` domain is not bound to the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but hands the handler a `shop` value taken from the `x-shopify-shop-domain` HTTP header, which is never covered by that HMAC. Any party who can produce one valid `(body, hmac)` pair can replay it with an arbitrary `shop` header and have the library present it to the app's handler as if it came from that shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read directly and unauthenticated from the `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes and compares the signature only against `verifiable_query.to_signable_string` (i.e. the body), never touching the shop header: [3](#0-2) 

`Registry.process` uses this HMAC check as its sole authentication step, then constructs `WebhookMetadata` using the unauthenticated `request.shop` and dispatches it to the handler: [4](#0-3) 

The gem's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify" and describes `shop` as a trusted field of `WebhookMetadata` ("The shop domain of the webhook"), which the sample handler then uses directly to key work per merchant (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) — i.e. the documented API tells integrators to trust `data.shop` as an authenticated field: [5](#0-4) [6](#0-5) 

This exactly mirrors the reported bug class: the check that establishes trust (`Utils::HmacValidator.validate`, bound only to the body) is not the same identity that is subsequently acted upon (`request.shop`, taken from an unsigned header). The equality that should hold — "the shop the HMAC authenticates" == "the shop the handler is told to act for" — is broken, just as in the original report `msg.sender` (aliased) != `OTHER_BRIDGE` (un-aliased) broke the intended identity check.

### Impact Explanation
An attacker who can obtain any one legitimate `(body, hmac)` pair — for example by triggering a webhook on their own store, or capturing one sent by Shopify to their own endpoint — can replay that exact body and HMAC to the victim app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a different (victim) shop domain. `HmacValidator.validate` will still pass, because it only checks the body against the secret. `Registry.process` will then call the handler with `WebhookMetadata#shop` set to the victim's domain and `body` set to attacker-controlled content. Any host application that follows the documented pattern and uses `data.shop` to key which merchant's records the webhook body is applied to (exactly as shown in the gem's own docs) will apply attacker-influenced data under another tenant's identity — a cross-tenant data integrity/confidentiality break.

### Likelihood Explanation
Any internet-accessible webhook endpoint built per the gem's documented usage is affected. No secrets are required beyond obtaining one legitimately-signed body/HMAC pair, which is trivial for an attacker who owns any store that can trigger webhooks of the topic they wish to spoof (e.g. `orders/create` on their own shop, then replayed against the target app’s endpoint with a swapped shop header).

### Recommendation
Bind the `shop` domain into the value that's actually authenticated, e.g. include the `x-shopify-shop-domain` header (and ideally `topic`/`webhook-id`) in the signable string used by `HmacValidator`, or have `Registry.process` cross-check `request.shop` against the shop associated with the specific `webhook_id`/registration before dispatching to the handler. At minimum, the documentation should explicitly warn that `data.shop` is not covered by the HMAC and must be independently verified (e.g. against a known/registered shop for that `webhook_id`) before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker triggers (or otherwise obtains) a legitimate webhook delivery for topic `orders/create` from their own shop `attacker-shop.myshopify.com`, capturing the exact raw body `B` and the corresponding `x-shopify-hmac-sha256` value `H` (valid because it was computed by Shopify using the app's real secret over `B`).
2. Attacker sends a POST request directly to the victim app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid since HMAC only signs `B`)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (swapped)
   - Header `x-shopify-topic: orders/create`
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` builds successfully; `Utils::HmacValidator.validate` recomputes HMAC over `B` and it matches `H`, so validation succeeds.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app (per the documented handler pattern) to process attacker-controlled order data under `victim-shop.myshopify.com`'s tenant context.

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
