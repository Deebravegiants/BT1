### Title
Webhook `shop` (and `topic`) identity is trusted from unauthenticated headers while only the raw body is covered by the HMAC — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) and event `topic` from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`), but the HMAC signature verified by `Utils::HmacValidator.validate` is computed only over the raw request body. `Registry.process` treats a valid body HMAC as proof the whole request "did indeed come from Shopify" (per the gem's own documentation) and hands the header-derived `shop` straight to the app's handler via `WebhookMetadata`, without binding it to the signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` and `topic` are read from headers that are never part of the signed material: [2](#0-1) 

`Registry.process` verifies only that HMAC and, on success, unconditionally forwards `request.shop` and `request.topic` to the registered handler as trusted metadata: [3](#0-2) 

The docs describe this check as proof the "request did indeed come from Shopify," implying the whole request (including the shop/topic identity used for tenant routing) is authenticated: [4](#0-3) 

The equality this breaks: `shop bound by the HMAC` should equal `shop trusted by the application for tenant identification`, but in fact `shop (header, unauthenticated)` ≠ `shop (covered by HMAC, none)`. Because the same `api_secret_key` is shared by every shop that installs the app, any merchant/internet user who has the app installed on their own store can legitimately trigger a webhook, capture the resulting `(raw_body, hmac)` pair — which is valid because it truly was HMAC'd with the app's real secret — and then replay that exact body to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a victim shop. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` dispatches the handler with `shop: <victim shop>`.

### Impact Explanation
Any application logic that uses the webhook's `shop` to look up the shop's stored access token/session, update per-shop billing/order state, trigger fulfillment, or otherwise act on behalf of that tenant will act on attacker-chosen data while believing it originated from — and is authorized for — a different, victim tenant. This is a cross-tenant access/data-integrity break driven entirely by an identity value that the library never actually authenticates, meeting the Critical bar (cross-tenant access) defined in scope.

### Likelihood Explanation
The precondition is low-effort and does not require any Shopify credentials, access tokens, or `api_secret_key` knowledge: an attacker only needs to be a legitimate (even free/dev) merchant with the target app installed so they can capture one real, validly-signed webhook body, then replay it to the shared public endpoint with a forged `shop-domain`/`topic` header. No interaction with Shopify's servers beyond normal app installation is required.

### Recommendation
Bind the tenant/topic identity into the verified signable material (e.g., include `shop`, `topic`, and `webhook_id` in the HMAC input, or perform a secondary authenticated check such as confirming the shop is one for which this app holds a session/has an active installation before trusting `request.shop`), and update `Utils::HmacValidator`/`Webhooks::Request#to_signable_string` accordingly so `Registry.process` cannot be tricked into dispatching a genuinely-signed body under a spoofed shop/topic.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers any webhook event (e.g. `orders/create`), capturing the raw POST: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid because it's HMAC-SHA256(`api_secret_key`, B)), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the exact same `B`/`H` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and, if desired, a different `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and `body: B`, and the host application processes it as a legitimate event for the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
