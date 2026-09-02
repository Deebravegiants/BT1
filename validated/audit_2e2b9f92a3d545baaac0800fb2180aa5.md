This confirms the vulnerability: the docs explicitly state `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" via HMAC, and hands `data.shop` to the handler as the trusted tenant identifier — but the HMAC only covers the raw body, never the `shop` header.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`, then unconditionally trusts the `shop` value taken from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header when constructing the `WebhookMetadata` passed to the app's handler. The `shop` field is never included in the signed payload, so the equality "HMAC-authenticated sender == shop attributed to the webhook" does not hold.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read directly and unauthenticated from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then builds `WebhookMetadata` using `request.shop`, handing it to the host app's handler as the authoritative tenant identifier: [3](#0-2) 

`WebhookMetadata.shop` is documented as "The shop domain of the webhook" and is the value apps are expected to use to route/attribute the webhook to a tenant: [4](#0-3) [5](#0-4) [6](#0-5) 

Because the `api_secret_key` used to compute the HMAC is shared across every shop that has installed a given app (it is a per-app secret, not a per-shop secret), any account/shop that legitimately installs the app can obtain a fully valid `(raw_body, hmac)` pair for its own store. The header carrying the shop identity is not part of the signed data, so that same body+HMAC pair can be replayed to the app's webhook endpoint with an arbitrary `shop-domain` header value, and it will still pass `Utils::HmacValidator.validate`. This breaks the identity binding `HMAC(secret, body) == integrity(shop, body)`: the signature proves the body originated from an installer of the app, but not that it belongs to the shop named in the header.

### Impact Explanation
This is a cross-tenant boundary break: a party who has (or ever had) a legitimate installation of a vulnerable app can forge webhook deliveries that the gem will pass through as authenticated for a different, victim shop, since `Registry.process` reports `Utils::HmacValidator.validate(request)` as sufficient proof of authenticity for the entire `WebhookMetadata`, including `shop`. Any host application that uses `data.shop` (as documented) to select which tenant's data to update — which is the gem's own documented usage pattern — can be made to apply attacker-controlled webhook bodies to a different merchant's records, i.e., cross-tenant access/manipulation of another shop's data. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires: (1) attacker has or creates a store that installs the target app once (a normal, unprivileged action for any Shopify app that supports self-serve installs / dev stores), (2) attacker captures one legitimate webhook delivery (raw body + HMAC) sent by Shopify to the app for their own store, (3) attacker replays that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header to name the victim shop. No knowledge of `api_secret_key` or any victim credential is required, and the HMAC check present in this gem's own code (`Utils::HmacValidator.validate`) passes.

### Recommendation
Bind the `shop` claim to the signed payload before it is trusted, analogous to fixing an owner-swap bug by re-checking the post-flight state against the pre-flight authenticated state. Concretely, `Webhooks::Request#to_signable_string` (or `Registry.process`) should incorporate the `shop-domain` header into the value that is HMAC-verified (Shopify's newer webhook headers also include an `X-Shopify-Webhook-Id`/API version that could be bound similarly), or `Registry.process` should independently verify that `request.shop` corresponds to a shop with an active, expected installation/session before invoking the handler, rather than trusting the header as-is once the body-only HMAC check succeeds.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal install flow), triggering Shopify to send a legitimate webhook, e.g. `orders/create`, to the app's registered webhook endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some JSON `raw_body`.
2. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value (e.g., by controlling their own receiving proxy, or because the webhook target is their own dev server for testing).
3. Attacker crafts a new HTTP POST to the app's webhook endpoint reusing the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (all required headers present), and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against `hmac` — both unchanged from the legitimate delivery.
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker's JSON>, ...)`, so the host app — following this gem's own documented pattern of trusting `data.shop` — processes attacker-controlled webhook content as if it were an authentic webhook for `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L12-17)
```markdown
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
