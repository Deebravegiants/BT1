### Title
Webhook shop identity is not covered by HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity by HMAC-validating only the raw request body, while the `shop` identity that is handed to the application's handler is read from an unauthenticated HTTP header. This breaks the binding `shop authenticated == shop delivered to handler`, letting anyone who can obtain one genuinely Shopify-signed webhook (e.g. by installing the app on their own store) replay it against the app's webhook endpoint while swapping the shop identity to a victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is never part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it with the `hmac-sha256` header: [3](#0-2) 

`Webhooks::Registry.process` performs this HMAC check and then immediately forwards the unauthenticated `request.shop` value to the application handler as the tenant identity: [4](#0-3) 

The gem's own documentation confirms the intended trust contract — that `process` "will verify the request did indeed come from Shopify" — and shows the resulting `data.shop` being used directly as the tenant key to queue tenant-scoped work: [5](#0-4) [6](#0-5) 

Because the HMAC only proves the *body* was produced with the app's `client_secret`, but not which shop it was produced for, an attacker who installs the app on their own store (an ordinary, unprivileged install requiring no access token or secret) receives genuinely Shopify-signed webhook deliveries for their own shop. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (body/HMAC untouched), so `Registry.process` accepts the request as authentic and calls the handler with `shop: <victim-shop>`, even though the payload was never generated for that shop.

### Impact Explanation
This breaks the tenant boundary the gem is documented to enforce for webhook processing: `Registry.process` is supposed to guarantee "the request did indeed come from Shopify" for the shop it reports, but the shop value itself is unauthenticated. An attacker can cause an app to attribute arbitrary (attacker-controlled-shape) webhook data to a shop they do not control, i.e. cross-tenant data injection/processing — matching the Critical "cross-tenant access" impact category, achieved without needing the app's `client_secret`, an access token, or any privileged credential.

### Likelihood Explanation
Medium-to-High. Any internet user can register as a Shopify partner/developer, install the target app on a free development store, and receive real webhook deliveries for that store — no special access is required. Replaying the captured body with a modified `shop-domain` header is trivial (a single HTTP request), and the vulnerability is exercised through the gem's own documented `Registry.process` / `Webhooks::Request` API exactly as instructed in `docs/usage/webhooks.md`.

### Recommendation
Bind the shop identity to the signature instead of trusting a header value alone:
- Include the `shop-domain` header (and ideally `topic`, `api-version`, `webhook-id`) in `to_signable_string`, so the HMAC covers the full identity tuple, not just the body; or
- Have the gem independently confirm the reported shop is one the app has an active session/installation for before invoking the handler, rejecting webhooks for unknown/mismatched shops.

### Proof of Concept
1. Attacker installs the target Shopify app on their own development store (`attacker-shop.myshopify.com`) — no special privileges required.
2. Shopify sends a legitimately signed webhook to the app's endpoint:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC over raw body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id": 123, ...}
   ```
3. Attacker captures this exact request and replays it to the same endpoint, changing only the shop header:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same valid HMAC, body unchanged>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id": 123, ...}
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this as before; `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC.
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process/store attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
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
