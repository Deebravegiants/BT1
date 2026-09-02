### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an unauthenticated HTTP header, while the HMAC signature that `Registry.process` validates only covers the raw request body. This breaks the identity binding `hmac_signed_bytes == bytes_the_handler_trusts_for_tenant_identity`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` calls `Utils::HmacValidator.validate(request)` which HMACs exactly that signable string against `Context.api_secret_key` [2](#0-1) . Meanwhile `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header with no cryptographic binding to the body or the HMAC at all [3](#0-2) . After successful HMAC validation, `Registry.process` passes `request.shop` directly into the `WebhookMetadata` object delivered to the host application's handler as the authoritative tenant identifier [4](#0-3) .

Because the HMAC only signs the body and never the `shop-domain` header, a party who has observed (or can otherwise obtain) one valid `(body, hmac)` pair for shop A can replay that exact body/hmac pair to the same webhook endpoint while substituting the `shopify-shop-domain` header with shop B. `HmacValidator.validate` will still succeed (the body and secret are unchanged), and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "B"` for data that Shopify actually generated for shop A. The equality that should hold - `signed_bytes == bytes_used_for_tenant_binding` - does not: signed_bytes = raw_body only, tenant_binding_bytes = shop-domain header, which is disjoint from what's signed.

### Impact Explanation
This directly enables cross-tenant confusion: a merchant/attacker with access to their own or an intercepted legitimate webhook payload (bodies are frequently exposed via logs, browser devtools on storefronts, or other non-secret channels, and the topic/hmac/body triple is not tied to a specific destination shop) can cause the host application to process the webhook body as if it belonged to a different `shop`. Since apps commonly use `WebhookMetadata#shop` to select the tenant's data/session to write to (e.g., "look up session for `data.shop`, then persist `data.body`"), this can lead to data being attributed to, or acted upon on behalf of, the wrong tenant - a cross-tenant integrity break within the trust boundary this gem is supposed to enforce.

### Likelihood Explanation
Medium. It requires the attacker to possess at least one legitimate `(raw_body, hmac)` pair (obtainable from their own store's webhook deliveries, which are not treated as secret and are commonly logged or forwarded), plus the ability to submit an HTTP request with attacker-chosen headers to the app's webhook endpoint (which host apps expose publicly to receive Shopify webhooks). No access token, `api_secret_key`, or privileged account is needed.

### Recommendation
Bind the header set to the signature verification. Include `shop`, `topic`, and `api_version` header values in the HMAC-verified representation (e.g., by hashing/concatenating them together with the body before comparison, or by independently deriving/validating the shop from a signed source such as a stored session lookup rather than trusting the header verbatim). At minimum, `Registry.process` should not use `request.shop` as an authoritative tenant identifier unless that value is itself covered by the same HMAC that is validated.

### Proof of Concept
1. Attacker's own store `A` receives a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` [5](#0-4) .
2. Attacker replays an HTTP POST to the same app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: shop-b.myshopify.com` (a different tenant).
3. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (= `B` only) and succeeds, since `B` and the secret are unchanged [2](#0-1) .
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: parsed B, ...)` [4](#0-3) , with the `shop` field forged and unauthenticated by the HMAC that just "passed".

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
