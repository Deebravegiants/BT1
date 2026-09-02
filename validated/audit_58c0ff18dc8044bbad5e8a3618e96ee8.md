## Title
Webhook `shop` (and `topic`) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook purely by validating an HMAC computed over the raw request body. The `shop` (and `topic`) values that are subsequently handed to the app's handler as trusted tenant identifiers come from HTTP headers that are **not included** in the signed content, so they can be freely substituted by anyone who can produce one valid (body, HMAC) pair, without ever needing the app's `client_secret`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates the HMAC against the request object (i.e. against the body only), and then dispatches the handler using the header-derived `shop`/`topic` values without any additional binding check: [3](#0-2) 

Compare this with the OAuth callback path, where the equivalent identity field (`shop`) **is** part of the signed content, matching the "shop authenticated == shop used" invariant: [4](#0-3) 

For webhooks, no such invariant holds: `hmac == HMAC(secret, body)` says nothing about `shop`. The binding that should hold — "the shop the HMAC authenticates" equals "the shop the app attributes/acts on" — is broken.

The documentation confirms the app is expected to trust `Registry.process` to establish provenance: *"This will verify the request did indeed come from Shopify"* and that `data.shop` is the shop domain handed to the developer's handler: [5](#0-4) [6](#0-5) 

### Impact Explanation
Any unprivileged internet user who can install the app on their own shop (a normal, unprivileged action for a public app) legitimately receives real webhook deliveries — genuine `(raw_body, HMAC)` pairs signed by Shopify using the app's `client_secret` — for their own shop's events. Because the `shop-domain` header is not covered by the signature, that same valid body+HMAC pair can be replayed to the app's webhook endpoint with the `shop-domain` header changed to any victim shop domain. `Registry.process` will accept it as authentic (HMAC checks out) and hand the attacker-chosen `shop` value to the app's handler as if it were an authentic event for the victim tenant. If the host application uses `data.shop` to key writes, sync orders/customers, or otherwise act on tenant data (as the documented usage pattern encourages: `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), this is a cross-tenant data-integrity/confusion vector achievable by any merchant with no credentials, access tokens, or the app's `client_secret`.

### Likelihood Explanation
High for any app that follows the gem's own documented pattern of trusting `data.shop`. The attacker only needs to be a legitimate (even short-lived) installer of the app on a shop they control — no special privilege, secret, or social engineering required — and a way to POST directly to the app's public webhook URL, which is by definition internet-reachable.

### Recommendation
Bind the header-derived identity fields into the signed content that `HmacValidator` verifies, e.g. by including `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (mirroring what real Shopify HMAC covers), or otherwise cryptographically bind the claimed shop to the verified payload before it is passed to `WebhookMetadata`/handlers. At minimum, document prominently that `data.shop`/`data.topic` are unauthenticated and must not be trusted as tenant identifiers without an independent check (e.g., cross-referencing against a shop that is known to have an active webhook subscription/session).

### Proof of Concept
1. Attacker installs the target public app on their own shop `attacker.myshopify.com` and lets it register for a webhook topic (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint: raw body `B` and header `Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`, plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `(B, H)` (trivial — it's their own webhook payload) and re-sends a POST to the same public webhook endpoint, keeping `B` and `H` unchanged but setting `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this still passes.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, i.e., the app processes attacker-controlled data as if it originated from the victim shop. [3](#0-2) [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-38)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
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
