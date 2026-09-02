### Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC, but the HMAC only covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that the gem hands to the host application's handler are read directly from unauthenticated HTTP headers, so the "authenticated" identity (the body/signature) and the "acted-upon" identity (the shop header used to route/attribute the event) are not the same bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over exactly that signable string and compares it to the `hmac-sha256` header: [2](#0-1) 

But `Registry.process` uses `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all pulled straight from headers that are never included in the signed bytes — to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

The equality that should hold is: `shop-bound-by-HMAC == shop-acted-upon`. In fact the code enforces only `HMAC(body) == received_signature`, while `shop`/`topic`/`webhook_id` are taken from `@headers["shopify-shop-domain"]` (or `x-shopify-shop-domain`), values that are never mixed into `to_signable_string`. Any request with a body/HMAC pair that is valid for the app's secret (e.g., one captured from a legitimately delivered webhook for one shop, since an unprivileged user can install the app on their own store and receive real webhooks) can be replayed with a different `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header, and `Registry.process` will still accept it (because the body-only HMAC still validates) and will hand the handler a `WebhookMetadata` claiming the event belongs to an arbitrary, attacker-chosen shop.

This is documented as trustworthy by the gem itself: the webhook doc states that calling `Registry.process` "will verify the request did indeed come from Shopify" and instructs handlers to use `data.shop` directly (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [5](#0-4) [6](#0-5) 

So this is not a case of the host app misusing an undocumented API — the gem's own documented contract tells developers `data.shop` is safe to trust after `process` succeeds, when in reality only the body bytes are authenticated, not the shop attribution.

### Impact Explanation
An attacker who can obtain any single valid `(body, hmac)` pair for the target app (trivially available to anyone who installs a free/dev version of the app on their own store and captures one real webhook delivery) can forge webhook deliveries attributed to any other merchant's shop domain by simply changing the `X-Shopify-Shop-Domain` header on the replayed POST. Since host applications are told by the gem's documentation that a processed webhook's `data.shop` is a verified identity, this breaks the tenant boundary: it enables cross-tenant data injection/confusion in downstream systems that key their processing (e.g., "update order for shop X", enqueueing background jobs, or writing to a per-shop database record) on `data.shop`. This matches "Critical - cross-tenant access" since a shop-boundary is crossed with only a captured/replayable payload and no access token or `client_secret`.

### Likelihood Explanation
Likelihood is high: no privileged credentials are needed. An attacker only needs (a) one authentic webhook `(body, hmac)` pair, obtainable by installing the target app on a shop they control (a normal unprivileged action) or waiting for/triggering a webhook event, and (b) the ability to send an HTTP POST with custom headers to the app's public webhook endpoint, which is expected to be internet-reachable per the gem's own integration instructions.

### Recommendation
- Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before trusting them.
- At minimum, when Shopify's webhook signature only covers the body, `Registry.process`/`Webhooks::Request` should not expose `shop`/`topic`/`webhook_id` as verified fields without also validating them against known/expected registrations (e.g., cross-checking `shop` against an active session or webhook subscription record before dispatch), and the documentation should be updated to clarify that `data.shop` is unauthenticated header data, not verified by the HMAC check.
- Consider validating the `topic` against the `webhook_id` via a Shopify Admin API lookup (using a valid session for the claimed shop) before acting on high-value webhooks.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged action available to any developer/merchant) and configures a webhook, e.g. `orders/create`.
2. Attacker triggers the webhook and captures the raw POST, including the valid `X-Shopify-Hmac-Sha256` header computed over the JSON body with the app's real `api_secret_key` (attacker never sees the secret, but the header is valid for that body).
3. Attacker replays the exact same body and `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but overwrites `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the body/HMAC pair — this passes because the body is unchanged: [7](#0-6) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, and the host app (per the gem's documented usage) processes it as a legitimate event for the victim tenant: [8](#0-7)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
