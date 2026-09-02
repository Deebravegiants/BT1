### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](), [File: lib/shopify_api/webhooks/registry.rb]())

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` header (and other headers) taken from the same request to identify which merchant the payload belongs to. Because the HMAC signing scope never includes the `shop`, `topic`, `webhook_id`, or `api_version` header values, an attacker who controls a shop where the app is installed can capture one of their own legitimately-signed webhook deliveries and resubmit it to the app's webhook endpoint with the `shop-domain` header swapped for a victim shop, producing a payload that passes signature validation but is attributed to the wrong tenant.

### Finding Description
`Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

`HmacValidator.validate` computes/compares the signature purely against that signable string: [2](#0-1) 

`Registry.process` only checks this body-only HMAC before dispatching to the app's handler, and builds the `WebhookMetadata` — including `shop` — directly from unauthenticated headers on the same request object: [3](#0-2) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read from HTTP headers that are never part of `to_signable_string`: [4](#0-3) 

The gem's own documentation instructs app authors to key merchant-scoped logic (e.g. queuing jobs, choosing which shop's record to update) directly off `data.shop` once `Registry.process` has "verified the request did indeed come from Shopify": [5](#0-4) [6](#0-5) 

The identity binding that should hold is:
`hmac_valid(raw_body, api_secret_key) == true` should imply `request.shop == the tenant that actually produced raw_body`.

In reality the binding is broken: `hmac_valid(raw_body, api_secret_key)` is a property of `raw_body` alone, while `request.shop` is an independent, unauthenticated field. Since `api_secret_key` is the same for every shop that has the app installed, any one of the app's own installed shops can obtain a `(raw_body, hmac)` pair that is valid under the shared secret, then replay it with an arbitrary `x-shopify-shop-domain` header. `Registry.process` will accept it and hand the handler a `WebhookMetadata` claiming the payload came from any shop of the attacker's choosing.

### Impact Explanation
This breaks the tenant/shop identity boundary that app developers are told they can rely on after `Registry.process` succeeds: cross-tenant data confusion becomes possible — an attacker (a merchant who installed the app) can cause the app to process a webhook body attributed to a different, victim shop domain. Depending on how the handler uses `data.shop` (as documented: to select which merchant record/job the payload applies to), this can lead to injecting forged data into a victim's tenant records, this qualifies as cross-tenant access per the given impact classification.

### Likelihood Explanation
Likelihood is Low-to-Medium: it requires the attacker to already be a legitimate, installed merchant of the target app (so they can capture at least one validly-signed webhook body under the shared `api_secret_key`), and requires the app's own webhook handler to trust `data.shop` for tenant resolution without any additional cross-check (e.g. verifying the shop has a known/expected registration for that specific webhook). Both preconditions are realistic given the gem's documented usage pattern.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the HMAC-verified payload rather than trusting the header independently: either include these header values in the signable string checked by `HmacValidator`, or require the caller of `Registry.process` to independently verify that `request.shop` corresponds to a shop with an active, registered webhook subscription for `request.webhook_id`/`topic` before invoking the handler.

### Proof of Concept
1. App merchant "attacker.myshopify.com" has the app installed and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid against the app's shared `api_secret_key`), header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends this exact `(B, H)` pair to the app's webhook endpoint, but rewrites the header to `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H` — see [1](#0-0)  and [2](#0-1) .
4. `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)` — see [3](#0-2) , causing the app to process attacker-controlled content as if it originated from the victim shop.

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
