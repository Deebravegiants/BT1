This confirms the design: the gem's own documentation instructs developers to trust `data.shop` as the authenticated shop domain (`docs/usage/webhooks.md:14,26`), and `ShopifyAPI::Webhooks::Registry.process` verifies "the request did indeed come from Shopify" via HMAC before invoking the handler [1](#0-0) , but the HMAC only ever signs the raw body, not the shop domain header that is passed through as authenticated identity.

### Title
Webhook shop-domain identity spoofing via HMAC scope mismatch - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, then passes `request.shop` straight into `WebhookMetadata` for the app's handler to trust as the originating tenant. However, the HMAC signature only covers the raw request body — never the `shop-domain` header — so an attacker who possesses one valid `(body, hmac)` pair (trivially obtainable by installing the app on their own store and receiving a real webhook) can replay that exact body/hmac to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header value. The signature still validates because the header is outside the signed scope, and the handler processes attacker-controlled/replayed data under the identity of a shop the attacker doesn't control.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 
while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers: [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. the body: [4](#0-3) 

`Registry.process` gates entirely on that body-only HMAC check and then forwards the header-derived, unauthenticated `shop` value into the handler's trusted metadata: [5](#0-4) 

This breaks the intended identity binding: `shop authenticated-by-HMAC == shop delivered to handler`. In reality, only `body authenticated-by-HMAC == body delivered to handler` holds; `shop` (and `topic`/`webhook_id`) ride along unauthenticated. The gem's own documentation instructs integrators to trust `data.shop` as the verified originating shop domain and to key business logic (e.g., `shop_domain: data.shop`) on it directly after calling `process`: [6](#0-5) [1](#0-0) 

### Impact Explanation
An unprivileged attacker who is any Shopify merchant (or trial/dev store) can install the target app on their own store, capture one legitimate webhook delivery (`body`, `hmac-sha256` header) for any subscribed topic, and replay it against the same app's webhook endpoint any number of times with the `shopify-shop-domain` header rewritten to any victim shop domain string. Because `process` only validates the body's HMAC, the forged request passes `Utils::HmacValidator.validate` and the app's handler executes with `data.shop` set to the attacker-chosen victim shop. Depending on how the host app keys its per-tenant data/authorization on `data.shop` (as the gem's own docs recommend), this enables cross-tenant data injection/confusion — e.g., fabricating "genuine" webhook events (order/customer/product data) attributed to a shop the attacker doesn't operate, poisoning per-shop caches, job queues, or audit trails keyed by `shop_domain`. This matches the Critical "cross-tenant access" impact category, since the trust boundary between tenants is broken using only an unprivileged/self-service test store.

### Likelihood Explanation
Likelihood is moderate-to-high: no secrets, tokens, or privileged access are required — the attacker only needs to install the app once (a standard, unprivileged, self-service action any developer/merchant can perform) to obtain one valid signed request, then can replay it indefinitely with a forged `shop-domain` header. The vulnerability is a direct, deterministic consequence of the HMAC's signed scope excluding `shop`/`topic`/`webhook_id`, not a probabilistic or edge-case condition.

### Recommendation
Extend the HMAC-verifiable scope (or add a second binding check) to cover the shop domain — e.g., require the caller to supply the shop identity out-of-band (from the route/registration, not from `request.shop`) and cross-check it against `request.shop`, or reject processing when the header-derived `shop` doesn't match a shop the app has an active session/registration for that topic. At minimum, document prominently that `data.shop` is NOT authenticated by the HMAC and must not be trusted as a tenant identity without independent verification against known/registered shops.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers/receives one genuine webhook, e.g. `orders/create`, capturing the raw body `B` and the real `x-shopify-hmac-sha256: H` header (computed by Shopify over `B` with the app's real `client_secret`, which the attacker never needs to know).
2. Attacker sends a new HTTP POST to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `x-shopify-hmac-sha256: H` (unchanged)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic: orders/create` (unchanged or attacker-controlled, also unauthenticated)
3. Server builds `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` and calls `ShopifyAPI::Webhooks::Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` calls `to_signable_string` → `B`, recomputes `HMAC-SHA256(secret, B)`, which equals `H` — validation passes [7](#0-6) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` built from `request.shop`, which is entirely header-derived and unauthenticated [8](#0-7) [9](#0-8) .
6. The app's handler processes attacker-supplied/replayed order data as if it genuinely originated from `victim-shop.myshopify.com`, confirming the cross-tenant identity binding is broken.

### Citations

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
