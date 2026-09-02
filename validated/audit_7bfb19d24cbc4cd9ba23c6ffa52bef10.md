Found it: in `Webhooks::Registry.process`, the HMAC (`Utils::HmacValidator.validate(request)`) is computed over `Webhooks::Request#to_signable_string`, which is defined as the raw request body bytes (`@raw_body`), but the `shop` identity that is actually handed to the webhook handler (`request.shop`, used to select/scope tenant data) is read from the `shopify-shop-domain` HTTP header, which is *not* covered by the HMAC at all.

### Title
Webhook `shop` identity is read from an unauthenticated header while the HMAC only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator.validate` only signs `@raw_body` (`to_signable_string` returns `@raw_body`). The header bytes used to determine which shop a webhook belongs to are never included in the signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) . `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed body [2](#0-1) . `Registry.process` validates the HMAC and then immediately trusts `request.shop` to build `WebhookMetadata`, which is handed to the app's handler as the tenant identifier [3](#0-2) .

This breaks the identity binding: `shop_authenticated (i.e. covered by HMAC) == shop_used_by_handler` does not hold. The HMAC only proves "Shopify (or holder of the secret) produced this exact body bytes"; it proves nothing about which shop header accompanied that body. The header is fully attacker-controlled unless the transport (host framework) independently protects/pins it, which this gem cannot assume and does not document as a requirement in `Errors::InvalidWebhookError` handling.

Contrast with `Auth::Oauth::AuthQuery#to_signable_string`, where `shop` is explicitly serialized into the signed string [4](#0-3) , i.e. that path correctly binds the shop into what's HMAC-verified. The webhook path does not follow the same pattern.

### Impact Explanation
An unprivileged network attacker who can replay a validly-signed webhook body from Shop A (e.g. a webhook payload leaked, logged, or captured from a low-value/legitimate delivery to shop A) can resubmit it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to Shop B. `Utils::HmacValidator.validate` still succeeds (the HMAC only covers the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "shopB"` alongside body content that actually belongs to shop A. Any handler that trusts `data.shop` to select the tenant record/session to update (a documented, expected pattern in `docs/usage/webhooks.md`) will write shop-A data under shop-B's identity — this is a cross-tenant data confusion primitive carried entirely by data this gem asserts is "verified."

### Likelihood Explanation
Exploitability depends on the attacker obtaining one valid signed webhook body (topic-specific, but many webhook bodies are not otherwise secret and could be observed via logs, error trackers, browser devtools in dev/test environments, or a webhook the attacker's own store legitimately receives) and being able to POST it to the target app's webhook endpoint with a different shop header — both of which are plausible for an unprivileged actor without needing `api_secret_key`.

### Recommendation
Bind `shop` (and ideally `topic`, `api-version`) into the signed payload used for verification, or independently verify that the header-derived `shop` matches a shop value embedded in/derivable from the verified body, before constructing `WebhookMetadata`. At minimum, document and enforce that `shop-domain` must not be trusted unless corroborated by data inside the HMAC-covered body.

### Proof of Concept
1. Capture (or independently receive, since your own store gets its own legitimate webhooks) a valid webhook delivery for `shop-a.myshopify.com`: headers include a correct `X-Shopify-Hmac-Sha256` for `@raw_body`.
2. Replay the exact same raw body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` in `Registry.process` passes because it only re-computes the HMAC over `@raw_body`, unaffected by the header change. [3](#0-2) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: <shop-a's data>, ...)`, and any tenant-scoped write keyed off `shop` will cross tenant boundaries.

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
