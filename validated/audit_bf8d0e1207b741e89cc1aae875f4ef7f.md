### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so `HmacValidator` never authenticates the `shop-domain` header. Any party who legitimately possesses one valid `(body, hmac)` pair for their *own* store (which any merchant with the app installed can obtain, since it is delivered to their own webhook subscription) can replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop. `Registry.process` still reports the request as verified and hands the attacker-chosen `shop` value straight to the app's handler, breaking the identity binding between the cryptographically-verified bytes and the tenant identity the host app acts on.

### Finding Description
`Registry.process` gates all further handling on a single check: [1](#0-0) 

```
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
```

`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`: [2](#0-1) 

And for a webhook `Request`, `to_signable_string` is defined as just the raw body — it deliberately excludes the `shop`, `topic`, `webhook_id`, and `api_version` values that are all read straight from unauthenticated HTTP headers: [3](#0-2) 

So the equality the library actually proves is:
`HMAC(secret, received_body) == received_hmac`

but the equality the host application relies on (and that the gem's own documentation promises — *"This will verify the request did indeed come from Shopify"*) is:
`asserted_shop (header) == the shop that produced this signed body`

These are not the same claim. The `shop-domain` header can be swapped for any string without invalidating the HMAC check, because it was never part of the signed material. [4](#0-3) 

### Impact Explanation
This is a cross-tenant boundary break: a request whose payload authenticity is only tied to "some webhook event for the app's secret," not to a specific shop, is passed to the app's handler carrying an attacker-chosen `shop` value. Per the gem's own documented usage pattern, host applications key business logic directly off `data.shop` (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` in `docs/usage/webhooks.md`). An attacker who is nothing more than an ordinary merchant with the app installed on their own store can capture one legitimately-signed webhook delivered to their own endpoint and replay it with a victim's shop domain in the header, causing the app to process attacker-controlled webhook data (including sensitive mandatory topics like `shop/redact`, `customers/redact`, `app/uninstalled`) as if it originated from the victim tenant — without ever needing the app's `client_secret`, an access token, or any privileged access.

### Likelihood Explanation
Likelihood is high for any app relying solely on `ShopifyAPI::Webhooks::Registry.process` for both authenticity and tenant attribution (the intended and documented usage): the attacker only needs a working relationship with the app on any single store (even a free/trial install) and the ability to send an HTTP POST with modified headers to the app's public webhook route — no interception, credential theft, or social engineering is required.

### Recommendation
Include the shop/tenant identity in the HMAC-signed material where possible, or, failing that, cross-check `request.shop` against an out-of-band trusted source (e.g., the shop associated with the session/webhook subscription that was registered) before dispatching to the handler. At minimum, document prominently that `Registry.process`'s HMAC check does not authenticate the `shop`, `topic`, `webhook_id`, or `api_version` headers, so host applications must not treat `data.shop` as trusted without additional verification (e.g., confirming a webhook was actually registered/expected for that shop/topic pair).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and configures/observes the webhook delivery to the app's callback endpoint, capturing a legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair for a topic such as `customers/data_request` or `app/uninstalled`.
2. Attacker resends the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the same endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` (unchanged), so `HmacValidator.validate` succeeds.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: <attacker's data>)`, causing the app to act on attacker-controlled content attributed to the victim's tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
