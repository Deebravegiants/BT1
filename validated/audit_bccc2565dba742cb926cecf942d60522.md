### Title
Webhook HMAC signs only the raw body, letting an attacker with any valid webhook forge the `shop`, `topic`, and `webhook_id` identity claims trusted by `Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify" before handing the webhook to the app's handler, but the HMAC signature it validates only covers the raw JSON body. The `shop`, `topic`, `webhook_id`, and `api_version` values — which are read straight from HTTP headers and passed to the handler as trusted, verified identity fields — are never part of the signed material, so any actor able to replay one legitimately-signed body can reattribute it to an arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But the same `Request` object exposes `shop`, `topic`, `webhook_id`, and `api_version` read directly from unauthenticated headers: [2](#0-1) 

`HmacValidator.validate` computes the signature exclusively over `to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this HMAC check as its only authenticity gate, then immediately forwards the *header-derived* `shop`, `topic`, and `webhook_id` to the app's handler as if they had been verified: [4](#0-3) 

The identity binding that should hold is: `shop header value == shop that produced/authorized this signed body`. Because the signature never covers the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers, that equality is not enforced by this gem. An attacker who legitimately receives one valid signed webhook (e.g., for their own installed/trial shop — this requires no privilege beyond installing the app on any store) can replay the exact same signed body to the app's webhook endpoint while substituting a different value for `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`). The HMAC check still passes because it only re-hashes the unchanged body, so `Registry.process` calls the handler with `WebhookMetadata.shop` set to the attacker-chosen value, `topic` set to an attacker-chosen value, while the body content is unrelated to that shop.

This is not a caveat the host application is expected to already guard against: the documentation explicitly states `Registry.process` "will verify the request did indeed come from Shopify" and instructs apps to trust `data.shop` for shop-scoped operations, with no mention that `shop`/`topic`/`webhook_id` fall outside the signed payload: [5](#0-4) [6](#0-5) 

This matches the listed analog class directly: "a field acted on but not covered by the HMAC."

### Impact Explanation
Any app that uses `data.shop` (or `data.topic`/`data.webhook_id`) from `WebhookMetadata` to select which tenant's records to update, dedupe, or act on — exactly as the gem's own documented example does (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) — can be tricked into attributing a genuine, signature-valid payload to a shop that never sent it. Depending on the topic (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`), this enables cross-tenant data corruption or triggering shop-scoped side effects (session/token revocation, data deletion flows) against a victim shop the attacker does not control, which is a cross-tenant boundary violation.

### Likelihood Explanation
Exploitation requires only the ability to install the target app on some Shopify store (or otherwise obtain one legitimately-signed webhook body) and to send an arbitrary HTTP POST with attacker-controlled headers to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is needed. This is reachable by any unprivileged internet user who can install a free/dev app.

### Recommendation
Include the `shop-domain`, `topic`, `webhook-id`, and `api-version` header values in the HMAC-signed material (or otherwise bind them cryptographically to the signature), so that `HmacValidator.validate` fails if any of these fields are altered independently of the body. At minimum, document prominently that `Registry.process`'s HMAC check does not authenticate these header-derived fields, so host applications know they must independently corroborate `data.shop` against a known/installed session before acting on it.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled store `attacker-shop.myshopify.com`; Shopify sends a real webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H`, computed as `HMAC-SHA256(secret, B)`.
2. Capture the raw request: body `B`, headers including `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-webhook-id: <id>`.
3. Replay this exact request to the same app endpoint, unchanged except `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(secret, B)` — identical to `H` since `B` is untouched — and returns `true`.
5. `Registry.process` calls the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: B, ...)`, and the host app (following the gem's documented pattern) processes body `B` as belonging to `victim-shop`, even though `victim-shop` never sent or authorized it.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
