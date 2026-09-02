### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` extracts the `shop` value from the `x-shopify-shop-domain` HTTP header, but `Utils::HmacValidator` only verifies the HMAC over the raw request body. The shop identity that gets attached to every processed webhook is therefore not cryptographically bound to the signature that "authenticates" the request, breaking the equality `hmac_signed_bytes == bytes_the_app_trusts_as_authenticated`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight from headers with no cryptographic coverage: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC solely over `to_signable_string` (the body): [3](#0-2) 

`Registry.process` checks only this body HMAC, then immediately trusts `request.shop` as the tenant identity and forwards it to the app's handler: [4](#0-3) 

Because all shops that install the same app share the same `api_secret_key`, any merchant who installs the app receives genuinely-signed webhooks for their own store. That merchant can capture a legitimate `(body, hmac)` pair from their own store's webhook delivery and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to any other shop's domain. `HmacValidator.validate` will still succeed because it never inspects the header, so `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain while `body` is attacker-controlled content.

The library's own documentation reinforces the false assumption that `process` fully authenticates the request, including the shop identity: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook," and the documented handler example uses `data.shop` directly as a merchant/tenant key (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), which is exactly the intended, documented usage pattern this gem promotes. [5](#0-4) [6](#0-5) 

### Impact Explanation
An unprivileged attacker who merely installs the app on a shop they control (no access token, no `client_secret`, no privileged account needed) can forge webhook deliveries that the host application will process as belonging to a different, victim shop. Since the host application follows the gem's documented pattern of trusting `data.shop` as the tenant key, this enables cross-tenant data injection/impersonation — attacker-controlled webhook bodies get attributed to and processed under a victim shop's identity. This matches the Critical "cross-tenant access" impact category, since the tenant/shop boundary that the app relies on this gem to authenticate is not actually enforced.

### Likelihood Explanation
Any developer/merchant with legitimate access to install the app (which is by design open to any Shopify merchant) can trivially capture one real, validly-signed webhook payload from their own store and replay it against the app's public webhook endpoint with a modified `shop-domain` header. No secrets, tokens, or privileged access are required beyond normal app installation, making this straightforward to exploit.

### Recommendation
Bind the shop identity to the authenticated payload. At minimum, `Webhooks::Request#to_signable_string`-equivalent verification should also require that `request.shop` correspond to a shop with an active install/session known to the app (i.e., the library should either include the shop domain in the value being verified, or explicitly document/enforce that consumers must cross-check `data.shop` against their own installed-shop registry before trusting it) rather than presenting `Registry.process` as a full authentication of the request, including shop identity.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any subscribed topic (e.g. `orders/create`), receiving a legitimate webhook POST with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker replays this exact `(B, hmac)` pair directly to the app's webhook controller endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, and the host app (following the documented pattern) processes/stores attacker-controlled data `B` under `victim-shop.myshopify.com`'s tenant context.

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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
