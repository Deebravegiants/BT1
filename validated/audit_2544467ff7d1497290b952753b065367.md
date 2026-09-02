### Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then passes the header-derived `shop` value straight to the app's webhook handler as trusted tenant identity.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns `@raw_body` only — none of the `shopify-*` headers are included in the signable string.

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are parsed straight from headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate`, then immediately builds `WebhookMetadata` using the unauthenticated `request.shop`: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body): [4](#0-3) 

The documented contract explicitly states that `process` "will verify the request did indeed come from Shopify," and instructs developers to trust `data.shop` as the tenant identifier for downstream processing (e.g., enqueuing a job keyed by `shop_domain: data.shop`): [5](#0-4) [6](#0-5) 

**Identity binding broken:** `shop authenticated (implicitly, by the passing HMAC check that the docs claim proves Shopify origin) ≠ shop acted upon (attacker-controlled `shopify-shop-domain` header, never covered by the HMAC digest)`.

Because a valid `hmac-sha256`/body pair for one tenant's payload remains valid regardless of the `shop-domain`, `topic`, or `webhook-id` header values sent alongside it, an attacker who can obtain (e.g., by replaying, intercepting, or reusing) any single legitimately-signed webhook body/HMAC pair for topic X can resubmit it to the same endpoint with an arbitrary `shopify-shop-domain` header (a different merchant) and/or a different `shopify-topic`/`webhook-id` header, and `process` will accept it as authentic and dispatch it to the handler with the attacker-chosen `shop`.

### Impact Explanation
This directly maps to cross-tenant confusion: the merchant identity used by the host application to route/store data (`data.shop`) is not bound to the cryptographic proof of authenticity (the HMAC), letting an attacker who obtains any one valid signed payload impersonate a different shop or topic in the webhook pipeline, causing the host app to attribute Shopify-originated data to the wrong tenant or wrong event type.

### Likelihood Explanation
Exploitability requires the attacker to already possess a validly-signed `(raw_body, hmac)` pair — a realistic condition since webhook bodies/HMACs are visible to man-in-the-middle-adjacent parties (logging systems, browser dev tools relaying, misconfigured proxies, or captured via any endpoint the app exposes that echoes webhook payloads), and Shopify webhook endpoints are typically public unauthenticated URLs by design. No `api_secret_key` or credentials are required to mount the header-substitution attack itself, only a previously observed valid signed body.

### Recommendation
Include the security-critical headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) in the HMAC-signed material, or otherwise cryptographically bind them, rather than trusting them as plain headers once only the raw body has been verified.

### Proof of Concept
1. Capture a legitimately Shopify-signed webhook request: headers `x-shopify-topic: orders/create`, `x-shopify-shop-domain: victim.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, body `raw_body`.
2. Resend the identical `raw_body` and identical `x-shopify-hmac-sha256` value to the same webhook endpoint, but change `x-shopify-shop-domain` to `attacker-shop.myshopify.com` (and/or change `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `to_signable_string` (the untouched `raw_body`), so validation passes: [7](#0-6) 
4. The handler receives `WebhookMetadata` with `shop: "attacker-shop.myshopify.com"` and the original body, which the host app (per documented usage) treats as an authentic webhook for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
