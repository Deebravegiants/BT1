Found it. In `lib/shopify_api/webhooks/request.rb`, the HMAC signature covers only the raw body:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

But `shop` (used as the tenant identity for routing the webhook payload to a handler) is read straight from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is **not included** in the HMAC-signed data at all: [1](#0-0) [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., the body), then immediately trusts `request.shop` (the unauthenticated header) to build `WebhookMetadata` and dispatch it to the host application's handler: [3](#0-2) 

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing tenant spoofing in webhook processing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from `@raw_body` only. The `shop` value exposed to the host application's webhook handler is taken from the `x-shopify-shop-domain` (or `shopify-shop-domain`) HTTP header, which is never part of the HMAC computation. `Registry.process` validates the HMAC of the body and then unconditionally trusts this unauthenticated header to identify the shop for the webhook.

### Finding Description
The binding that should hold is: `shop_used_by_handler == shop_that_the_HMAC_actually_authenticates`. Here it does not — the HMAC in `to_signable_string` binds only `@raw_body`, and `shop` is read from a header outside that signable set (`shopify_header("shop-domain")`). Since HTTP headers are attacker-controllable data delivered to the app's webhook endpoint (the endpoint is a public URL the host app exposes, and this gem's own `Request`/`Registry` code is what parses and trusts the header), any request whose `hmac-sha256` header matches a signature computed over a given `raw_body` will pass `HmacValidator.validate`, regardless of what `shop-domain` header accompanies it. `Registry.process` then builds `WebhookMetadata` using this unverified `shop` value and hands it to the app's handler:
```ruby
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
Because the shop identity is not cryptographically bound to the payload, an attacker who can obtain (or replay/re-send) one legitimately HMAC-signed webhook body for their own shop (which they control, since app-secret HMACs for a given app are the same across all shops using that app) can resubmit it with an arbitrary `shop-domain` header value, causing the host application to process the webhook as if it originated from a different, victim tenant.

### Impact Explanation
This crosses the tenant boundary this gem is responsible for maintaining: it lets data attributable to one shop be attributed to another shop inside the host application's business logic, purely via unauthenticated request metadata. This matches "cross-tenant access" in the impact list, since the shop that a host app's webhook handler acts on (e.g., updating per-shop state, revoking access, syncing order data) can be attacker-selected independently of what was actually HMAC-authenticated.

### Likelihood Explanation
Any unprivileged internet user who runs (or has run) the same third-party app on their own shop can capture a validly-signed webhook body/HMAC pair (the app's `client_secret`/`api_secret_key` HMACs identically for every shop installing that app) and resend it to the app's public webhook endpoint with a forged `shop-domain` header. No credentials, tokens, or privileged access are required beyond having the app installed on any shop.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signable string, or otherwise independently verify that the shop asserted in the header corresponds to a shop with an active, known session/installation, before dispatching to the handler. At minimum, document/enforce that `shop` must not be treated as authenticated purely because the overall HMAC check passed.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, capturing `raw_body` and its `x-shopify-hmac-sha256` header (both valid, HMAC computed with the app's shared `api_secret_key`).
2. Attacker resends the exact same `raw_body`/`hmac-sha256` pair to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only checks `@raw_body`, unaffected by the header change.
4. `handler.handle` is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, causing the host app's business logic to act as though the webhook came from the victim shop.

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
