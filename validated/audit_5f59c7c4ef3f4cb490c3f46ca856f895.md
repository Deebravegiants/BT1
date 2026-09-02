Confirmed: the docs explicitly instruct developers to build the trust model around `ShopifyAPI::Webhooks::Registry.process`, which validates only the raw body against the HMAC and then dispatches on the unauthenticated `topic`/`shop-domain` headers. [1](#0-0) 

### Title
Webhook topic and shop identity are dispatched from HMAC-unauthenticated headers - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the webhook's raw JSON body via HMAC-SHA256, but uses the `shopify-topic` and `shopify-shop-domain` HTTP headers — which are not included in the signed payload — to select the handler and to populate `WebhookMetadata#shop`, the tenant identifier the host application is documented to trust.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against this signable string (the body), never against `topic`, `shop-domain`, `webhook-id`, or `api-version`: [3](#0-2) 

`Registry.process` then dispatches the handler using the unauthenticated `request.topic` header, and constructs `WebhookMetadata` using the unauthenticated `request.shop` header: [4](#0-3) 

`request.topic` and `request.shop` are read verbatim from headers with no cryptographic binding to the body or to each other: [5](#0-4) 

Because a Shopify app's `client_secret` (`api_secret_key`) is a single shared secret across every shop that has installed the app, any merchant who installs the app can legitimately receive real webhook deliveries with valid `(body, HMAC)` pairs signed under that same shared secret. Nothing in `HmacValidator` or `Request` binds a given `(body, HMAC)` pair to the `shop-domain`/`topic` header values it was originally delivered with. A malicious merchant (tenant A) can therefore take a `(body, HMAC)` pair from their own genuine webhook delivery and POST it directly to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a different, victim shop (tenant B) and/or a different `x-shopify-topic`. `HmacValidator.validate` still returns `true` (the body/HMAC pair is valid), the registry looks up a handler purely by the forged `topic`, and the handler receives `WebhookMetadata` asserting `shop: "victim-tenant-B"` for body content that actually originated from tenant A. This breaks the identity equality the host application relies on: `shop verified by HMAC` should equal `shop acted upon by the handler`, but here the HMAC only verifies bytes of the body, while the `shop` value acted upon (used by virtually every Shopify app to select which tenant's database row to update) is taken from a completely unauthenticated header.

### Impact Explanation
This is a cross-tenant data-integrity/confusion vulnerability: it lets one merchant with a legitimate app installation inject events (with a valid signature) that the app must attribute to any other shop of the attacker's choosing, and can also route the body to whichever handler the attacker names via the forged `topic` header, applying that tenant's arbitrary body content to the victim's records under the app's trusted-webhook code path. Per the report's classification bucket, this falls under "cross-tenant access" since it lets one tenant's authenticated write path (webhook HMAC check) be redirected to operate on another tenant's identity.

### Likelihood Explanation
Exploitability requires only that the attacker be a legitimate (even free-trial) installer of the target app, which is normal for public/App-Store-listed apps, and the ability to send an arbitrary HTTP POST to the app's public webhook URL (no `api_secret_key` or other confidential values are needed, since the HMAC of the attacker's own genuine webhook deliveries is directly reusable). No TLS interception or credential theft is required.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` in the value that is HMAC-verified (or independently verify that the header-reported shop matches a shop known to have subscribed to that specific webhook/topic before trusting `WebhookMetadata#shop` for tenant routing), so identity fields acted upon by handlers are cryptographically bound to the same signature that authenticates the body.

### Proof of Concept
1. App is installed by attacker's shop `attacker.myshopify.com` and by victim shop `victim.myshopify.com`, both under the same app (same `api_secret_key`).
2. Shopify delivers attacker a genuine webhook: body `{"order_id":123}`, header `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, and a valid `x-shopify-hmac-sha256` computed over that body only.
3. Attacker resends the exact same body and HMAC to the app's public webhook endpoint but replaces the header with `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) succeeds because it only checks the body's HMAC.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the `orders/create` handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: {"order_id"=>123}, ...)`, and the host application processes attacker-supplied data as if it belonged to the victim shop.

### Citations

**File:** docs/usage/webhooks.md (L125-136)
```markdown
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
