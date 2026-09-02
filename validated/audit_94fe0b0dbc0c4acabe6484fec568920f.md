### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its authenticity signature over the raw body only, while the `shop` (tenant identity) is read from an HTTP header that is never included in the signed bytes. `ShopifyAPI::Webhooks::Registry.process` treats `HmacValidator.validate` success as proof that "the request did indeed come from Shopify" for the shop it reports, but the signature does not bind the shop identity at all, breaking `shop cryptographically authenticated == shop dispatched to handler`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from an attacker-suppliable HTTP header, outside the signed content: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.to_signable_string` (the raw body) against `verifiable_query.hmac` using `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` gates on this HMAC check and then forwards `request.shop` straight into `WebhookMetadata`, which is delivered to the app-defined handler as the trusted tenant identifier: [4](#0-3) 

The gem's own documentation instructs developers to treat a passing `process` call as proof the webhook "did indeed come from Shopify" for the `shop` in `data.shop`, and to route business logic (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) using that value: [5](#0-4) [6](#0-5) 

Because the shop-domain header sits entirely outside `to_signable_string`, the equality the gem is supposed to guarantee — `shop cryptographically bound in HMAC == shop delivered to handler` — never holds. Any bearer of one genuinely Shopify-signed `(raw_body, hmac)` pair (trivially obtainable by an unprivileged party who installs/uses the app on their own store and captures one of their own webhook deliveries) can replay that exact body+signature to the app's public webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with any other merchant's `*.myshopify.com` domain. `HmacValidator.validate` still succeeds (it only checks the body bytes), and `Registry.process` dispatches the forged tenant identity to the handler as if Shopify itself asserted that shop.

### Impact Explanation
This breaks the cross-tenant isolation the HMAC check is supposed to provide: an attacker can inject arbitrary attacker-chosen webhook payloads (product/order/customer/app-uninstalled data, etc., subject to the topic's schema) that the app will process and persist as belonging to a victim shop it has never interacted with, without any credential belonging to that shop. Depending on what the host app does with `data.shop`/`data.body` (e.g., updating per-shop records, triggering shop-scoped side effects, or acting on `app/uninstalled`), this enables cross-tenant data corruption/injection — classified Critical (cross-tenant access) per the scope rules.

### Likelihood Explanation
Likelihood is high for any app author following the documented pattern exactly as shown in `docs/usage/webhooks.md`: no additional binding of `shop` is suggested or provided by the library, so this is not a case of the host ignoring documented API — it is the documented API's own guarantee being incomplete. An attacker only needs to capture one legitimately-signed webhook body (e.g., from their own store's install of the target app) and replay it with a modified header to any internet-reachable webhook endpoint of that app.

### Recommendation
Bind the shop identity into the authenticity check rather than trusting an unsigned header:
- Include the shop domain (and ideally topic/api-version) in the bytes verified by `HmacValidator`, or
- Cross-check `request.shop` against an independently trusted source (e.g., look up the registered/expected shop for the topic/webhook_id via the Admin API, or require the caller to supply the expected shop and compare it against a signed value) before dispatching to the handler, and
- Update `docs/usage/webhooks.md` to make explicit that `data.shop` is not authenticated by the HMAC check, if binding is not implemented, or remove that ambiguity by binding it as described.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) — Shopify legitimately signs the raw body `B` with the app's shared `client_secret`, producing header `hmac = HMAC-SHA256(secret, B)` and `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays this exact `raw_body: B` and `shopify-hmac-sha256: hmac` to the app's public webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac...})` builds successfully; `to_signable_string` is still just `B`.
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(secret, B)` and matches the supplied `hmac` — validation passes.
5. `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...))` is invoked, and the host app processes attacker-controlled data believing it is authentic Shopify traffic for `victim-shop.myshopify.com`, despite no cryptographic tie between that shop and the signature.

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

**File:** docs/usage/webhooks.md (L12-30)
```markdown
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
