### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` only signs the raw request body for HMAC verification, but exposes `shop` (from the unsigned `X-Shopify-Shop-Domain` header) as a trusted attribute that `Webhooks::Registry.process` passes straight into the handler as the tenant identifier. Because the same `api_secret_key` is shared across every shop that has an app installed, any user who can obtain one valid `(body, hmac)` pair from a webhook delivered to their own shop can replay that exact body/HMAC to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop, and the HMAC check will still pass.

### Finding Description
`HmacValidator.validate` verifies the signature against `verifiable_query.to_signable_string`, and for webhooks that string is defined as just the raw body: [1](#0-0) 

The `shop` accessor, however, is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which plays no part in the signable string: [2](#0-1) 

`Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` as the tenant key handed to the app's webhook handler: [3](#0-2) 

The binding that should hold is:
`shop authenticated by HMAC (i.e., the shop whose secret produced this exact body) == shop used as the tenant/session key delivered to the handler`

Because the header is outside the signed content, this equality does not hold. Any user who installs the app on their own store (a normal, unprivileged action) will receive genuine webhook deliveries — each a valid `(raw_body, hmac)` pair computed with the app's shared `api_secret_key` (identical for every install of that app, since it's the app's client secret, not a per-shop secret). The attacker can then replay that request to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to any victim shop domain. The HMAC only covers `@raw_body`, so `HmacValidator.validate` still returns `true`; `WebhookMetadata.shop` then reports the forged victim domain to the handler.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged attacker (no access token, no `api_secret_key`, no victim credentials — only their own legitimate install) can make the host application process arbitrary, attacker-chosen webhook bodies (topic-appropriate) under the identity of any other merchant using the app. If the host application uses `shop`/`data.shop` from `WebhookMetadata` to key data access, sync state, or trigger merchant-scoped actions (the intended and documented use of this field per `webhook_handler.rb`/`registry.rb`), this yields cross-tenant data manipulation — satisfying the Critical "cross-tenant access" bar in scope.

### Likelihood Explanation
Likelihood is meaningful but bounded by real-world constraints: the bug class itself (HMAC covering body only, not headers) is inherited from Shopify's own webhook signing scheme and is called out explicitly as an accepted analog pattern in the task's rules ("a shop authenticated versus the shop stored as a session key"). Any user can freely install a public app on their own dev/trial store to harvest a legitimate `(body, hmac)` pair for a topic of their choosing, then replay it against the shared public webhook endpoint with a forged shop header — no privileged access, secrets, or social engineering required. The actual damage depends on how permissively the host app trusts `data.shop`, which is outside this gem, but the gem provides no safeguard, warning, or optional secondary verification (e.g., cross-checking against a known/registered shop list) to prevent this trust misuse.

### Recommendation
Bind the shop identity into the verified material, or otherwise stop treating the header as authenticated on its own:
- Include the `shop-domain` header value in the signable string used for HMAC verification (this would require coordination with Shopify's own signing behavior, so it may not be directly fixable without a breaking change), or
- At minimum, document prominently in `Webhooks::Request`/`Registry` that `shop` is derived from an unauthenticated header and must be cross-validated by the host application against its own registered/installed-shop records before being used as a tenant key, and consider exposing a helper to do so.

### Proof of Concept
1. Attacker installs the target public app on their own shop `attacker-shop.myshopify.com` and lets Shopify deliver a real webhook (e.g. `orders/create`) to the app's registered endpoint. Attacker captures the full raw HTTP request: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker crafts a new HTTP POST to the same app webhook endpoint with the exact same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. Server-side, `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `request.hmac` decodes to the same value, and `to_signable_string` returns `B` unchanged — `Utils::HmacValidator.validate(request)` returns `true` (see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:13-22`).
4. `Registry.process` proceeds and calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))` (see `lib/shopify_api/webhooks/registry.rb:188-199`), even though the body/topic actually originated from the attacker's own shop and secret-verified request.

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
