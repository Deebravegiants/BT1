### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) header fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields are read directly from unauthenticated HTTP headers. `Registry.process` validates only the body-derived HMAC and then forwards the header-derived `shop` value, unverified, to the host application's webhook handler as the tenant identity for the event.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `hmac` is derived from the `hmac-sha256` header: [2](#0-1) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are all read straight from HTTP headers, none of which participate in the signature: [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. the raw body: [4](#0-3) 

`Registry.process` performs this HMAC check and then immediately trusts `request.shop` (and the other header-derived fields) to build the `WebhookMetadata` that is handed to the application's handler: [5](#0-4) 

The documented contract for `Registry.process` explicitly states it "will verify the request did indeed come from Shopify" before invoking the handler: [6](#0-5) 

and the handler docs instruct developers to key their downstream processing directly off `data.shop`: [7](#0-6) 

This creates the identity-binding break required by this analog: `hmac_verified(body)` ≠ `shop_used_for_tenant_dispatch(header)`. Because the same `api_secret_key` is shared across every shop that has installed a given app, any unprivileged user who installs the app on their own store can capture one of their own legitimately-signed webhook deliveries (valid body + valid HMAC for their own shop). They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and, since it's equally unauthenticated, `x-shopify-topic`/`webhook-id`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (it never looked at the shop header), so `Registry.process` dispatches the attacker's payload to the handler labeled as having originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity-confusion vector inside the gem's own webhook verification primitive: the gem advertises that `process` "verifies the request did indeed come from Shopify," but the verified bytes (body) and the acted-upon identity (shop header) are disjoint. Any host application that follows the gem's documented pattern of using `data.shop` from a processed webhook to select which tenant's session/record to update is at risk of writing attacker-controlled webhook content into another merchant's account context — a cross-tenant access outcome.

### Likelihood Explanation
Any user capable of installing the app on their own store (a normal, unprivileged OAuth install, requiring no leaked credentials) can obtain a validly-signed webhook body/HMAC pair for their own shop and immediately replay it with a modified `shop-domain` header to the same public webhook endpoint. No secret material beyond what Shopify already legitimately delivers to that installer is required.

### Recommendation
Include the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed body (e.g., verify `shop` against the session/store that is expected to be receiving that specific webhook subscription, rather than trusting the header value directly). At minimum, update `Request#to_signable_string` and `HmacValidator` so the shop/topic identity used for dispatch is provably derived from Shopify-signed content, and document that `data.shop` from `WebhookMetadata` must not be trusted as authenticated tenant identity unless this binding exists.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook (e.g. `orders/create`) so Shopify sends a POST with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture `B` and the HMAC header value.
3. Replay the identical POST to the app's webhook endpoint, keeping `B` and the HMAC header unchanged, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks `B` against the HMAC.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) builds `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's body, and invokes the app's handler as if `victim.myshopify.com` sent this event — demonstrating the identity-binding break.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
