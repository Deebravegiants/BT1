### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant spoofing of processed webhooks - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers — none of which are covered by that signature — before dispatching them to the host application's handler.

### Finding Description
`Webhooks::Request#hmac` is computed by the caller's secret against `to_signable_string`, which is defined as `@raw_body` only: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` values, however, are read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.), which are never part of the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC of the request and then immediately trusts `request.shop`/`request.topic` to build `WebhookMetadata` and dispatch to the registered handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no further binding back to the signed body: [4](#0-3) 

This is exactly the identity-binding break called out in the rules: a field (`shop`) that is acted upon (used to attribute the webhook to a tenant and passed to the host app's business logic) is not covered by the HMAC that is supposed to authenticate the request. Equality that should hold is:

`shop_bound_by_HMAC == shop_used_for_dispatch`

but in this implementation:

`shop_bound_by_HMAC = ∅ (HMAC only covers raw_body)`
`shop_used_for_dispatch = header["shopify-shop-domain"] (attacker-controlled, unauthenticated)`

Because the two are disjoint, whoever controls the header can decouple the authenticated body bytes from the tenant identity that the host application will act on.

### Impact Explanation
An attacker who is able to obtain one validly signed webhook body+HMAC pair (e.g., from their own development/trial store, which is entirely within their control and requires no privileged access to the target) can replay that exact body and HMAC while substituting the `shop-domain` header for a victim shop. `Registry.process` will pass HMAC validation (it only checks the body) and will then hand the handler a `WebhookMetadata` claiming the data belongs to the victim's `shop`. Any host application logic that uses `data.shop` to select the tenant record to update (a very common integration pattern for merchant-redact/data-request/orders/GDPR-style handlers) can be tricked into attributing attacker-supplied data to another merchant — a cross-tenant confusion condition rooted in this gem's own signature-verification boundary.

### Likelihood Explanation
The only prerequisite is possession of one legitimately signed webhook (attacker's own store is sufficient — no target credentials, TLS interception, or the app's `client_secret` are needed), and the ability to send an HTTP POST to the app's webhook endpoint with a modified `shop-domain` header. This is reachable purely through this gem's documented `Webhooks::Request`/`Registry.process` API surface, matching the required unprivileged-internet-user profile.

### Recommendation
Do not trust any header-derived identity field (`shop`, `topic`, `api_version`, `webhook_id`) unless it is cryptographically bound to the signed payload. At minimum:
- Include the `shop-domain` (and ideally `topic`, `api-version`, `webhook-id`) header values in the string that is HMAC-verified (`to_signable_string`), so tampering with these headers invalidates the signature, or
- Have `Registry.process` independently verify that `request.shop` matches an expected/allow-listed value for the session/store the webhook claims to originate from before dispatching to the handler.

### Proof of Concept
1. Attacker operates their own Shopify development store (`attacker.myshopify.com`) subscribed to the app's webhook, and captures a legitimately delivered webhook: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H` is computed by Shopify using the app's `client_secret` over `B`).
2. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Webhooks::Request#hmac` still decodes/validates against `B`; `HmacValidator.validate` succeeds because it only checks `to_signable_string` (`@raw_body`). [5](#0-4) 
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the forged `shop-domain` header and invokes `handler.handle(data: ...)`, causing the host application to process attacker-controlled body content as if it originated from `victim-shop.myshopify.com`. [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
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
