Confirmed the full path: `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) validates only `HmacValidator.validate(request)`, which HMACs `request.to_signable_string` — and `Webhooks::Request#to_signable_string` returns solely `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`), while `shop`/`topic`/`webhook_id` are read straight from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:20-23`) and then handed to the app's handler as the tenant identifier (`lib/shopify_api/webhooks/registry.rb:190-199`).

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` only proves that the **body** of a webhook request was signed by Shopify. The `shop` (and `topic`/`webhook_id`) values that the gem hands to the developer's handler as the trusted tenant identifier are read from HTTP headers that are completely outside the HMAC's coverage, breaking the intended binding `verified_bytes == acted_on_identity`.

### Finding Description
`Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string` (`lib/shopify_api/utils/hmac_validator.rb:26-31`). For webhooks, `Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

This mirrors Shopify's real signing scheme (HMAC over the raw body only), but the `shop` accessor is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic linkage to the signed body:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`Registry.process` performs exactly one check — the HMAC over the body — and then immediately trusts `request.shop` as the tenant for dispatch:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

The equality the gem should guarantee but doesn't is: `hmac_verified_bytes == bytes_that_determine(shop)`. Since `shop` is excluded from `to_signable_string`, any entity that possesses one valid `(raw_body, hmac)` pair — trivially available to any merchant who has an app installed and receives their own legitimate webhooks — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` still succeeds (it never looks at the header), and `Registry.process` calls the developer's handler with the attacker-chosen `shop`, `topic`, and `webhook_id`, since those are also unauthenticated headers. The gem's documentation reinforces the false trust: it states `process` "will verify the request did indeed come from Shopify" and describes `data.shop` simply as "The shop domain of the webhook" (`docs/usage/webhooks.md:14`, `:125`) with no caveat that this value is unauthenticated — an unprivileged internet user (any merchant with a live app installation, i.e., no special privilege beyond normal app usage) can therefore forge cross-tenant webhook deliveries using only a body they already legitimately received.

### Impact Explanation
This breaks a tenant-identity binding at the exact spot the gem is responsible for verifying: "request believably came from Shopify" versus "request is attributable to a specific shop." Any downstream app that follows the documented contract and uses `WebhookMetadata#shop` to key storage/authorization decisions (exactly as the gem's own example handler does: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`, `docs/usage/webhooks.md:26`) can have another merchant's legitimately-signed webhook body attributed to an arbitrary target shop, corrupting or injecting data into a different tenant's records — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires no secrets and no privileged access: any user who can install an app on their own store (a normal, unprivileged action) receives real webhooks with valid `(body, hmac)` pairs for their own shop, then can immediately replay that pair against the same endpoint with a forged `shop-domain` header. The only "cost" to the attacker is having any live app installation generating webhook traffic, which is trivial to obtain.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the HMAC-verified surface rather than trusting bare headers. Concretely, extend `to_signable_string` to incorporate the shop-domain header (and other identity-bearing headers) into the signed payload used for comparison, or — since Shopify's real HMAC only covers the body — have `Registry.process` cross-check `request.shop` against an independently trusted source (e.g., match it against the shop stored for the webhook_id in the app's own subscription records) before dispatching to the handler, and update `docs/usage/webhooks.md` to explicitly warn that `data.shop`/`data.topic`/`data.webhook_id` are not covered by the HMAC and must not be trusted for tenant-scoping without additional verification.

### Proof of Concept
1. Attacker installs the vulnerable app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. for `customers/data_request`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid since Shopify signed it).
2. Attacker replays the exact same request to the app's public webhook endpoint, keeping `raw_body = B` and `X-Shopify-Hmac-Sha256 = H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `request.hmac` reproduces `H`.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string == B` and matches `H` — validation succeeds. [4](#0-3) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, and any app following the documented pattern persists or acts on this data as belonging to `victim-shop`, even though it never sent this webhook.

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
