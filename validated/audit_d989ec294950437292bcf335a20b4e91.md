### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (tenant) attribution comes from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then unconditionally trusts that header as the originating shop when building `WebhookMetadata`, breaking the implicit binding `hmac_valid ⇒ shop_header_is_authentic`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only re-computes the HMAC of `to_signable_string` (i.e. the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authorization to hand `request.shop` straight to the app's handler as the trusted tenant identifier: [4](#0-3) 

The documented contract explicitly claims full authenticity: "call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify" and documents `shop` as a trusted field of `WebhookMetadata` for the handler to key business logic on: [5](#0-4) [6](#0-5) 

**Identity binding broken (as an equality):**
`HMAC_valid(raw_body, api_secret_key) == true` is treated as proof that `request.shop == originating_shop`, but the signature never covers the shop header, so the two are actually independent: `shop_header ∉ signed_bytes`.

### Impact Explanation
Because the shop attribution is not authenticated, any unprivileged internet user who can obtain one valid `(raw_body, hmac)` pair — e.g. by installing the target app (or any app using this gem) on their own free/development store and observing a real webhook delivery to their own endpoint — can replay that exact body+HMAC to the victim app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `Registry.process` will accept it as authentic and hand the handler a `WebhookMetadata` claiming the event originated from an arbitrary victim shop, with attacker-controlled body content. Any app logic keyed on `data.shop` (order/customer records, billing state, GDPR redact handling, cache keys, per-shop feature flags, etc., as shown in the gem's own documented handler example using `data.shop`) can be corrupted or cross-attributed to a shop the attacker does not control — a cross-tenant data integrity break.

### Likelihood Explanation
Exploitation requires no privileged credentials, no `api_secret_key`, and no access token — only the ability to install any app on a shop the attacker controls (a normal, unprivileged action) and to send an HTTP request with a spoofed header, both trivially available to any internet user. The gem's own documentation reinforces the false assumption that `process` fully "verifies the request did indeed come from Shopify," which increases the likelihood that consuming applications rely on `data.shop` without additional cross-checks.

### Recommendation
Bind the shop domain into the signed material (or otherwise cryptographically authenticate it), e.g. by validating that the shop returned in the header matches a shop known to have an active session/registration for that specific webhook subscription, and/or by updating `to_signable_string`/`HmacValidator` usage so the tenant identity cannot be swapped independently of the signed payload. At minimum, update the documentation in `docs/usage/webhooks.md` to clarify that `process` only guarantees body integrity, not the authenticity of the `shop` header, so consuming apps are not misled into treating `data.shop` as a verified value.

### Proof of Concept
1. Attacker installs a target Shopify app (built on this gem) on their own store `attacker.myshopify.com` and registers to receive a webhook (e.g. `orders/create`) pointed at an endpoint the attacker controls.
2. Attacker triggers the event and captures the legitimate raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — this HMAC is valid because it is computed by Shopify over the body using the app's real `api_secret_key`.
3. Attacker replays this exact `(raw_body, hmac header)` pair directly to the app's public webhook route, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. Inside the app: `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` → `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the HMAC — this passes.
5. `Registry.process` builds `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)` and calls the app's handler, which now processes attacker-controlled data as if it belongs to `victim-shop.myshopify.com`.

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
