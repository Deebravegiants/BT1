### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating that `hmac-sha256` matches a signature computed over the raw request body [1](#0-0) . The `Request#to_signable_string` method used for that HMAC computation returns only `@raw_body`; it never includes the `shop-domain` (or `topic`) header [2](#0-1) . Yet `request.shop`, read straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header, is passed on to the app's handler as the tenant identity for the event [3](#0-2) [4](#0-3) . This breaks the intended identity binding: `shop attributed to the event == shop bytes verified by the HMAC`.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field using `OpenSSL.secure_compare` [5](#0-4) . For `Webhooks::Request`, `to_signable_string` is defined as simply the raw HTTP body [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all read from HTTP headers that are never part of that signed string [6](#0-5) .

Crucially, `Context.api_secret_key` — the HMAC secret used for validation — is the app's single `client_secret`, shared across every shop that has installed the app; it is not a per-shop secret [7](#0-6) . This means any unprivileged Shopify merchant who has installed the app on their own store can:

1. Trigger a real webhook (e.g. `orders/create`) on their own shop, causing Shopify to deliver a body `B` together with a valid `x-shopify-hmac-sha256` signature `H = HMAC(client_secret, B)`.
2. Replay `B` and `H` unchanged to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`, since those are also unsigned).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over the (unchanged) body and secret — it validates successfully regardless of the header values, since the header values were never part of the signed material [8](#0-7) .
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, where `shop` is the attacker-controlled victim domain, not the shop that actually produced/authorized the payload [4](#0-3) .

The documented contract for host apps explicitly instructs them to trust `data.shop` as "the shop domain of the webhook" once `process` returns without raising, and to key their own business logic (job enqueuing, DB writes) off it, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [9](#0-8) [10](#0-9) . Because the gem's own `process`/`Request` API does not bind `shop` (or `topic`) to the cryptographically verified bytes, any app that follows this documented pattern inherits a tenant-confusion vulnerability that is intrinsic to the gem, not a misuse of it.

This maps to the report's bug class of "an identity binding broken by a field that is acted upon but not covered by the HMAC": `verified bytes (body) != attributed shop identity (header)`.

### Impact Explanation
An attacker who is merely an unprivileged Shopify merchant/app-installer (no special access, no leaked secrets, no privileged account) can cause the app to process webhook payloads under an arbitrary victim shop's identity, using only their own legitimately-signed webhook traffic as raw material. Depending on how the host app models tenants from `data.shop` (which the gem's own docs encourage), this enables cross-tenant data injection/corruption — e.g. spoofing `orders/create`/`app/uninstalled`/`shop/redact` events for a victim shop, corrupting per-shop state, triggering unintended data deletion (GDPR redact handlers), or forging billing/inventory events attributed to another tenant. This satisfies the "Critical – cross-tenant access" impact bar.

### Likelihood Explanation
Likelihood is high for any attacker with legitimate access to a low-privilege install of the target app (a very low bar — trial/dev stores are trivially obtainable), since no secret material, TLS interception, or social engineering is required — only the ability to intercept/replay their own outgoing webhook HTTP request with a modified header, then send it to the app's public webhook endpoint.

### Recommendation
Bind the shop domain (and topic/webhook_id) into the material that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the signed body — e.g., include `shop`/`topic` in `to_signable_string`, or require callers to cross-check `request.shop` against an out-of-band trusted registration record (the shop for which the webhook subscription was created) before dispatching to the handler, rejecting mismatches in `Registry.process`.

### Proof of Concept
1. Install the target app on `attacker.myshopify.com` and register for `orders/create` webhooks.
2. Trigger an order creation on `attacker.myshopify.com`; capture the resulting POST body `B` and the `x-shopify-hmac-sha256` header `H` sent by Shopify to the app's webhook endpoint.
3. Re-POST to the same webhook endpoint with body `B` and header `x-shopify-hmac-sha256: H` unchanged, but with `x-shopify-shop-domain: victim.myshopify.com`.
4. Observe `ShopifyAPI::Webhooks::Registry.process` at `lib/shopify_api/webhooks/registry.rb:190` succeeds (`Utils::HmacValidator.validate` passes because only `B` is checked, per `lib/shopify_api/webhooks/request.rb:35-38`), and the registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's chosen `body`.

### Citations

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

**File:** docs/usage/webhooks.md (L10-29)
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

**File:** docs/usage/webhooks.md (L125-135)
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
