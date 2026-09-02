### Title
Webhook `shop` identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies only the raw webhook body against the HMAC signature. The `shop` (and `topic`, `webhook_id`, `api_version`) values that are handed to the host application's webhook handler come from HTTP headers that are excluded from the signed data, so a valid HMAC for one shop's webhook body can be replayed with a forged `shop` header claiming to originate from a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cross-check against the signed payload: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e., the body) and the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` accepts the request once this body-only HMAC check passes, then forwards the *unverified* `request.shop` header straight into `WebhookMetadata` given to the app's handler: [4](#0-3) [5](#0-4) 

The identity binding that should hold is:
`shop asserted in WebhookMetadata.shop == shop that Shopify actually generated this signed body for`

Because the HMAC only covers `@raw_body`, this equality is never enforced by the gem. Since a single `api_secret_key` is shared across every shop that installs the app, any body+HMAC pair that Shopify legitimately sent for shop A remains a valid HMAC pair regardless of which `shop` header accompanies it. An unprivileged user who installs the app on their own store (a normal, unprivileged action) can capture a real webhook delivery (body + `x-shopify-hmac-sha256`) and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. The HMAC still validates, `Registry.process` still dispatches to the handler, and the handler receives `WebhookMetadata` claiming to be from the victim shop.

The library's own documentation reinforces the false guarantee, stating that `Registry.process` "will verify the request did indeed come from Shopify," without qualifying that shop identity itself is unauthenticated: [6](#0-5) 

### Impact Explanation
Any host application that trusts `WebhookMetadata.shop` (as the gem's own docs example does — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) to route webhook data to per-tenant records will apply attacker-supplied or replayed data under a victim shop's identity. This is a cross-tenant confusion caused directly by a gap in the gem's identity binding, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Likelihood is realistic: obtaining a legitimate body+HMAC pair requires nothing more than installing the (typically public) app on one's own store and triggering any subscribed event — no `api_secret_key`, access token, or privileged account is needed. Replaying the captured request to the public webhook endpoint with a modified `shop` header is trivial.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is verified, or require the host application to independently confirm that the asserted `shop` corresponds to a shop with an active installation/session before trusting `WebhookMetadata.shop`. At minimum, the gem should document explicitly that HMAC validation only proves the body originated from an app-secret holder, not that the accompanying `shop` header is authentic, and should not present `Registry.process` as fully verifying "the request did indeed come from Shopify" for a specific shop.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a subscribed webhook topic (e.g. `orders/create`) and capture the raw POST: body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Replay the exact same body `B` and hmac `H` to the app's public webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks `B` against `H` using the shared `api_secret_key`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) dispatches `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)` to the registered handler, which processes attacker-controlled data as though it belongs to `victim.myshopify.com`.

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
