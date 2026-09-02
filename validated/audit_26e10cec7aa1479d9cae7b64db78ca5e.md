### Title
Webhook shop/topic identity spoofing via unauthenticated headers — HMAC covers only the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," but the cryptographic check only covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` fields — which the handler uses to attribute the event to a specific merchant — are read straight from unauthenticated HTTP headers and are never bound to the HMAC. This breaks the identity binding `HMAC-verified bytes == attributed tenant`, allowing a validly-signed webhook body to be replayed with a spoofed shop header.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from headers, none of which are part of the signable string: [2](#0-1) 

`Registry.process` validates only this HMAC-over-body and, once it passes, forwards the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` values straight into `WebhookMetadata` for the handler to act on: [3](#0-2) 

`Utils::HmacValidator.validate` in turn only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. the raw body: [4](#0-3) 

The documentation explicitly promises full authenticity: "This will verify the request did indeed come from Shopify and then call the specified handler for that webhook," and instructs apps to key their downstream logic off `data.shop`: [5](#0-4) [6](#0-5) 

The app's `api_secret_key` is a single shared secret across every shop that installs the app (it is the same key used for OAuth HMAC validation and JWT verification elsewhere in the gem), not a per-shop secret: [7](#0-6) 

Because the HMAC never covers `shop`/`topic`, an attacker who legitimately installs the app on their own store (a normal, unprivileged action) receives genuinely-signed webhook deliveries for their own store — valid `(raw_body, hmac)` pairs computed with the app's shared secret. Since the header fields are excluded from the signed content, the attacker can replay that same `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or topic) header for an arbitrary victim shop. `Utils::HmacValidator.validate` still returns `true` because it never inspects the headers, and `Registry.process` dispatches the handler with `WebhookMetadata` falsely attributing attacker-controlled body content to the victim shop.

### Impact Explanation
Any app that follows this gem's own documented pattern (using `data.shop` from `WebhookMetadata` to select/update per-tenant records, as the docs example directly demonstrates) can be made to process forged webhook events "from" a shop that never sent them, and with body content the attacker fully controls (subject only to reusing a body previously validly signed for their own store, or any body whose HMAC they can obtain via their own installation). This is a cross-tenant identity-spoofing primitive: an unprivileged actor (any merchant able to install the app) can inject data attributed to a different merchant's tenant into the app's webhook processing pipeline.

### Likelihood Explanation
Any user who can install the app on a store of their own — no leaked credentials, no privileged account — automatically qualifies as an unprivileged attacker under this scan's threat model, since installing an app and receiving your own genuine webhooks requires no special access. Constructing the header-modified replay HTTP request requires no cryptographic material beyond intercepting your own legitimately delivered webhook.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content used for HMAC verification (or otherwise cryptographically bind them, e.g. by having `Registry.process` cross-check the header-provided shop against a shop registered/expected for that webhook subscription) so that tampering with any of these header fields invalidates the signature, matching the "verify the request did indeed come from Shopify" guarantee already documented.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; Shopify delivers a legitimately HMAC-signed webhook, e.g. `orders/create`, to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (computed over `B` using the app's shared `api_secret_key`).
2. Attacker captures `(B, H)` from their own webhook delivery (or crafts `B` to contain arbitrary attacker-chosen JSON while it happens to be delivered with valid `H`, since `H` only ever depends on `B`).
3. Attacker sends a forged HTTP POST directly to the app's public webhook route with the same body `B` and hmac header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present); `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and returns `true`.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to act on attacker-controlled data as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** docs/usage/webhooks.md (L10-18)
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
