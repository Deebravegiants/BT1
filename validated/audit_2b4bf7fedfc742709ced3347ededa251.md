### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted for tenant identification but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` uses the unauthenticated `shop-domain` header (via `request.shop`) as the tenant identity passed to the app's webhook handler. Since the app's `client_secret` (`api_secret_key`) is a single value shared across every merchant shop that installs the app, a party who controls one legitimate shop can obtain a genuinely Shopify-signed webhook (valid HMAC over an attacker-chosen body) and then present that same body+HMAC to the shared webhook endpoint with a forged `shop-domain` header naming a different, victim shop.

### Finding Description
`Request#to_signable_string` binds the HMAC exclusively to `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are read directly from HTTP headers, which are not part of the signed material at all: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then dispatches the handler using the (unauthenticated) `request.shop` value as the tenant identity for the event: [3](#0-2) 

The binding that should hold is:
`hmac_signed_bytes == (shop, topic, body)` that Shopify actually generated for a specific installation event.

What actually holds is:
`hmac_signed_bytes == body only`, while `shop` (the value the handler trusts to know "which merchant this event is about") is taken from an out-of-band header.

Because `api_secret_key` is one value per app, shared by every merchant tenant that installs it (not per-shop), a person who legitimately installs the app on their own store, shop A, can trigger Shopify to send a genuinely-signed webhook (any body content they can produce, e.g. by creating/updating a product, customer, or order on their own store, or by using a webhook subscription with attacker-controlled `fields`/`filter`). Because they control the webhook callback URL for shop A during this step (temporarily pointing it at infrastructure they own), they can capture the exact `(body, valid HMAC)` pair Shopify produced. They can then submit that captured `(body, HMAC)` pair directly to the multi-tenant app's shared webhook endpoint, substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with any other tenant's shop domain. `Utils::HmacValidator.validate` will accept it because it only recomputes the signature over `@raw_body`: [4](#0-3) 

`Registry.process` will then invoke the registered handler believing the event originates from the victim shop: [3](#0-2) 

The gem's own documentation instructs implementers to build the `Request` straight from `request.headers.to_h` and rely on `Registry.process` to confirm "the request did indeed come from Shopify," implying the shop attribution is trustworthy once HMAC passes — which is not the case: [5](#0-4) 

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce: an app built on top of this library that keys any per-shop state (installation status, order/inventory records, GDPR redact flags, uninstall handling, billing state, etc.) off `WebhookMetadata#shop`/`request.shop` can be made to apply attacker-crafted webhook payloads to a shop the attacker does not control, i.e., cross-tenant data injection/corruption in a multi-tenant SaaS app — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate, unprivileged merchant able to install the target app on their own store (a normal internet user can do this for any public embedded app) and briefly control that store's webhook delivery target to capture one valid `(body, HMAC)` pair — no access to `client_secret`, access tokens, or TLS interception is required. The capture-and-replay step is straightforward scripting.

### Recommendation
Include the authenticated shop identity in the HMAC-signed material, or independently authenticate the shop-domain header (e.g., cross-check it against the shop bound to the session/access token used to register the webhook, or require Shopify's webhook signing to cover headers as well as body). At minimum, `Registry.process`/`WebhookMetadata` should not treat `request.shop` as trusted tenant attribution without an additional binding to the registered session for that shop.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and briefly points the webhook delivery URL at infrastructure they control (or otherwise captures a webhook fired for their own store, e.g., via `orders/create` after crafting an order with attacker-chosen fields).
2. Attacker records the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent — this HMAC is valid because it's computed by Shopify with the app's single shared `client_secret`.
3. Attacker sends a new HTTP POST to the app's real, shared webhook endpoint with:
   - the exact captured body (so `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:26-31` succeeds),
   - the exact captured `x-shopify-hmac-sha256`,
   - `x-shopify-topic` unchanged or of choice,
   - `x-shopify-shop-domain` replaced with `victim.myshopify.com`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) accepts the HMAC and invokes the app's handler with `shop: "victim.myshopify.com"`, causing the app to process attacker-controlled data as if it originated from the victim's store.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
