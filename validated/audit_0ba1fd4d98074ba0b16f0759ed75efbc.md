### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before invoking the app's handler with the webhook's `shop`, `topic`, and `webhook_id`. In reality, the HMAC signature only authenticates the raw request body — the `shop-domain`, `topic`, and `webhook-id` headers that the handler relies on for tenant identity are never bound to that signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates only this body-derived HMAC, then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The gem's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify," and that `data.shop` is "The shop domain of the webhook" — implying it is authenticated: [4](#0-3) [5](#0-4) 

The broken binding, stated as an equality: `HMAC-verified bytes (raw_body)` ≠ `tenant-identity bytes actually acted on (shop-domain header)`. Since a single app `client_secret` is shared across every merchant that installs a public app, any shop that installs the app can obtain a validly HMAC-signed `(body, hmac)` pair for its own webhook deliveries. An attacker who controls one shop (e.g., their own dev/test store with the app installed) can capture one such valid `(raw_body, hmac)` pair, then replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to point at a victim shop. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` forwards the forged `shop` value to the handler as if it were verified.

### Impact Explanation
Downstream handlers are documented to trust `data.shop` as the authenticated identity of the originating tenant (per `docs/usage/webhooks.md`). A forged `shop` value lets an attacker who controls one tenant cause the app to process a webhook body as if it belongs to a different, victim tenant — a cross-tenant identity confusion reachable purely through this gem's documented `Registry.process`/`WebhookMetadata` contract, not through any misuse of the host app.

### Likelihood Explanation
Exploitation only requires installing the target app on a shop the attacker controls (a normal, low-privilege action for any public Shopify app) and the ability to send an arbitrary HTTP request to the app's public webhook endpoint with modified headers — no access to the app's `client_secret`, access tokens, or other privileged material is needed.

### Recommendation
Bind the tenant-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) into the HMAC-signable content (or otherwise cryptographically bind them to the verified body) so that `HmacValidator.validate` fails if any of these headers are altered independently of the signed body, matching the documented guarantee that a processed webhook "did indeed come from Shopify" for the claimed shop.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) they subscribed to, capturing the raw POST body `B` and the valid `x-shopify-hmac-sha256` header `H` computed by Shopify over `B` with the app's shared `client_secret`.
2. Attacker sends a new HTTP request to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally forged `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only recomputes/compares the HMAC over `B`.
4. `Registry.process` invokes the app handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, and the handler performs shop-scoped work believing it is legitimately processing an event for the victim tenant.

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
