### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body alone, while the `shop` (and `topic`, `api_version`, `webhook_id`) values are read from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to build the `WebhookMetadata` object handed to the app's `WebhookHandler`. An attacker who can obtain one genuinely-signed webhook body/HMAC pair (trivial: install the app on their own store and capture a real webhook delivery) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header, causing the host app to process the payload as if it belonged to a different, victim shop.

### Finding Description
The signed string for a webhook request is defined as only the raw body: [1](#0-0) 

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

`shop` is derived purely from the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header, which is never mixed into the signed bytes: [2](#0-1) 

Verification happens in `Registry.process`, which checks the HMAC (body-only) and then immediately trusts `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` — none of which are part of the signed material — to construct the `WebhookMetadata` delivered to the app's handler: [3](#0-2) 

The binding that should hold is:
`shop (used by handler to scope tenant data)` == `shop (cryptographically bound to the signed body)`

but the actual binding enforced is only:
`hmac(secret, raw_body)` == `received hmac`

with `shop` completely outside that equality. Because the app's `client_secret`/webhook secret is per-app (not per-shop), any shop that has installed the app can capture one legitimately-signed webhook (body + `X-Shopify-Hmac-Sha256`) and resend it to the same endpoint with a forged `X-Shopify-Shop-Domain` header pointing at any other installed shop. `HmacValidator.validate(request)` (used at `Registry.process` line 190) will report the signature as valid because it only checks the body, and the forged shop value flows unmodified into `WebhookMetadata#shop`, which apps use to select the tenant/session to act on (e.g., for `shop/redact`, `customers/redact`, `customers/data_request`, or any other topic that triggers tenant-scoped side effects).

### Impact Explanation
This breaks the shop/tenant identity binding for webhook processing, letting one shop's legitimately-installed operator (an ordinary unprivileged actor from the app's perspective) inject payloads that the host app attributes to a different shop. Depending on how the app's `WebhookHandler` uses `data.shop` (e.g., writing/deleting tenant records, triggering GDPR redaction, or driving billing/inventory logic keyed by shop), this results in cross-tenant data corruption or an attacker-controlled action being executed against a victim shop's tenant context — matching the "cross-tenant access" High-severity class.

### Likelihood Explanation
Likely for any app relying on this gem's `Webhooks::Registry.process` to dispatch webhooks: the attacker only needs their own valid app installation (which grants them a legitimate secret-signed webhook body/HMAC pair) and the ability to send an HTTP POST with a forged header to the app's public webhook endpoint — no possession of the app's `client_secret`, access token, or victim credentials is required.

### Recommendation
Bind the header-derived identity fields (`shop`, and ideally `topic`/`api_version`/`webhook_id`) into the value verified by the HMAC, e.g., by including the `X-Shopify-Shop-Domain` header (or the full raw header set Shopify signs) in `to_signable_string`, or by cross-checking `request.shop` against the shop associated with the session/subscription the webhook was registered for before dispatching to the handler.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` and trigger any webhook topic the app subscribes to; capture the raw POST body and its `X-Shopify-Hmac-Sha256` header — this is a validly-signed pair for the app's secret.
2. Replay this exact body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate(request)` at [4](#0-3)  succeeds because only the raw body is verified.
4. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` at [5](#0-4)  and invokes the app's `handler.handle`, which acts as though the (attacker-controlled) payload originated from the victim shop.

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
