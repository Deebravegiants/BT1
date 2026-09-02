### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used by `ShopifyAPI::Webhooks::Registry.process` to route the payload to the app's handler are read directly from unauthenticated HTTP headers. The HMAC check therefore does not bind the tenant identity to the signed payload.

### Finding Description
`to_signable_string` — the value that `Utils::HmacValidator.validate` HMACs and compares against the `hmac-sha256` header — returns only the raw body: [1](#0-0) 

But `shop` (and `topic`) are pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed string at all: [2](#0-1) 

`Registry.process` validates the HMAC against the body, then unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

The identity binding that should hold is:
`shop_bound_by_HMAC == shop_delivered_to_handler`

Because the signable string is `@raw_body` alone, `shop_bound_by_HMAC` is undefined/empty — the header value is free for anyone who can produce (or replay) a body+HMAC pair to set arbitrarily.

Since the merchant's own webhook deliveries for their own shop are legitimately signed (the secret is the app's global `client_secret`, not per-shop), any shop that installs the app receives valid `(body, hmac)` pairs for its own webhooks. An unprivileged holder of one such pair can replay that exact body/HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with an arbitrary victim shop domain. `HmacValidator.validate` still succeeds (it never looks at headers), and `Registry.process` will label the event as belonging to the attacker-chosen shop before invoking the app's handler.

### Impact Explanation
This breaks the tenant boundary the webhook subsystem is supposed to enforce: an app that trusts `WebhookMetadata#shop` (the documented API surface for identifying which merchant a webhook belongs to) can be made to process/store data under an incorrect (attacker-chosen) shop identity, i.e., cross-tenant confusion driven entirely from this gem's own webhook verification logic, not from the host ignoring documented behavior — the gem's own `process` method performs no binding between the signed bytes and the shop it reports.

### Likelihood Explanation
Requires the attacker to have received at least one legitimately signed webhook body (trivial for anyone who can install/uninstall the app on a shop they control, or observe a delivery), plus the ability to send an HTTP POST to the app's public webhook endpoint with modified headers — no secret, token, or privileged access needed.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC computation, or otherwise cryptographically bind them to the payload before `Registry.process` reports them to the handler, so a valid signature can only correspond to one specific shop/topic/body combination.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com`, triggers a webhook (e.g., `orders/create`), and captures the raw body `B` and its valid `x-shopify-hmac-sha256` value `H` from the delivery to their own endpoint.
2. Attacker POSTs to the target app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` (via `Request#to_signable_string` returning only `@raw_body`) succeeds because it never inspects the shop header.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to process/store attacker-supplied data under the victim shop's identity.

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
