## Finding

### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used by the host application to identify *which tenant* the webhook belongs to are read directly from unauthenticated HTTP headers. Since the HMAC secret (`api_secret_key`) is shared across all shops that install the app, any shop that has installed the app can capture a legitimately-signed webhook body+HMAC pair and replay it with a forged `x-shopify-shop-domain` header, causing the host app to process attacker-controlled webhook data under a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight from a header with no relationship to the signed content: [2](#0-1) 

`HmacValidator.validate` only proves that `to_signable_string` (i.e. the raw body) was HMAC'd with `Context.api_secret_key`: [3](#0-2) 

`Registry.process` then trusts `request.shop` unconditionally to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

The gem's own documentation tells integrators that calling `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook," encouraging apps to use `data.shop` as the tenant key (e.g., to look up the shop's session/record) without further verification: [5](#0-4) [6](#0-5) 

Because `api_secret_key` is the app's single, global secret (not shop-specific), the HMAC only proves "this body was produced by an app-secret holder for the app," not "this body belongs to shop X." The identity binding broken is:

`shop authenticated (proven by HMAC over the request) == shop used as the tenant key (`request.shop`, from an unsigned header)`

before the request: the equality holds only for genuine Shopify-delivered webhooks. After an attacker's request sequence — (1) install the app on their own store (any unprivileged merchant/dev-store can do this), (2) trigger any event to receive a real webhook with a valid `raw_body` + `hmac` pair, (3) replay that exact body/HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and optionally `x-shopify-topic`) with a victim shop's domain — the equality no longer holds: the HMAC still validates (it only covers `raw_body`), but `request.shop` now identifies a shop the attacker doesn't own.

### Impact Explanation
This breaks the tenant isolation the HMAC is meant to provide. A host application that (as directed by the gem's own documentation) uses `data.shop` from `WebhookMetadata` to select which merchant record to update, mark `app/uninstalled`, or process order/customer data, can be manipulated into applying attacker-supplied webhook bodies to a victim shop's data — cross-tenant access/data corruption. This matches the “cross-tenant access” Critical-impact category.

### Likelihood Explanation
Likelihood is high: no privileged credentials, access tokens, or the app's `client_secret` are required. Any user who can install the target app on a store they control (e.g., a free Shopify Partner development store) can obtain a validly signed webhook body/HMAC pair for arbitrary content they can produce on their own store (e.g., by editing a product, placing an order), then replay it against the app's public webhook endpoint with a different `shop-domain` header. No shop-specific secret exists to prevent this because the HMAC key is global to the app.

### Recommendation
Bind the shop identity into the signed/verified material instead of trusting the header value in isolation:
- After HMAC validation, cross-check `request.shop` against the shop associated with a currently-known, previously registered webhook/session (e.g., verify the shop has an active session/installation and that the specific `webhook_id` was actually registered for that shop) before dispatching to the handler.
- Alternatively/additionally, treat the `shop-domain`, `topic`, and `webhook-id` headers as untrusted unless corroborated by out-of-band knowledge (e.g., only accept webhooks for shops present in the app's session store), and document this requirement clearly since the current docs imply `Registry.process` already performs full verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g. `orders/create`) and captures the raw POST body `B` and its `x-shopify-hmac-sha256` header `H` sent to the app's webhook endpoint — `H` is a valid HMAC over `B` using the app's global `api_secret_key`.
3. Attacker replays the exact same request to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (keeping body `B` and hmac `H` unchanged).
4. `HmacValidator.validate` succeeds because it only checks `H` against `B` — see `lib/shopify_api/utils/hmac_validator.rb` — and `Registry.process` passes `shop: "victim-shop.myshopify.com"` (from the forged header) to the app's handler, see `lib/shopify_api/webhooks/registry.rb` lines 188-200, even though the payload `B` actually originated from the attacker's own store.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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
