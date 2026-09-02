### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from an unauthenticated HTTP header, while the HMAC signature computed by `Utils::HmacValidator` only ever covers the raw request body. This breaks the intended binding `verified_bytes == acted_on_identity`: the bytes that are cryptographically verified (the body) do not include the field (`shop-domain`) that `Registry.process` uses to key the webhook data delivered to the host application's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes and compares the HMAC purely over `verifiable_query.to_signable_string`, i.e. the raw body: [2](#0-1) 

Meanwhile `Request#shop` (and `#topic`, `#webhook_id`, `#api_version`) are read directly from HTTP headers, which are never included in the signed content: [3](#0-2) 

`Registry.process` validates only the HMAC and then immediately trusts `request.shop` as the tenant identity, constructing `WebhookMetadata` and dispatching it to the app's handler: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no further validation, and the interface contract for `WebhookHandler#handle` guarantees nothing about the origin of `shop` beyond "whatever the header said": [5](#0-4) 

**Attack sequence (equality broken):**
- Before: `hmac_valid == true` is meant to imply `(body, shop, topic) all originated together from Shopify for shop S`.
- After: An attacker who legitimately receives (or controls) a webhook delivery for their own shop A (a valid `raw_body` + valid `x-shopify-hmac-sha256`) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with victim shop B's domain. `HmacValidator.validate` still returns `true` because the signed bytes (the body) are unchanged, but `Registry.process` now dispatches to the handler with `data.shop == "B"` even though the payload content is really A's data.

This produces the equality break: `hmac_valid(bytes) == true` no longer implies `shop_claimed == shop_that_produced(bytes)`.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` (per the documented API of this gem) as the tenant key for persistence, cache invalidation, deduplication, or authorization decisions can be tricked into associating attacker-supplied webhook content with a different, unrelated merchant/tenant. This is a cross-tenant data-integrity issue rooted entirely in this gem's webhook verification logic — the gem verifies only the body, not the header field it hands back as the trusted "shop" identity.

### Likelihood Explanation
Exploitation requires the attacker to be able to send arbitrary HTTP requests to the app's public webhook endpoint (unprivileged internet capability) and to possess one legitimately-signed body+HMAC pair, which they can obtain simply by installing the app on their own store (a standard, no-privilege action) and capturing the webhook delivery Shopify sends them. No access token, `client_secret`, or TLS interception is required — only replay of a header-swapped copy of a request they legitimately received.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind `request.shop` to the verified body before it is exposed via `WebhookMetadata`. Short of that, `Registry.process` should not treat `request.shop` as a trusted identity for cross-request correlation without an independent verification step (e.g., confirming the shop against a Shopify API call, or documenting explicitly that `shop` is unauthenticated and must not be used for tenant-keyed decisions).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, receives a legitimate webhook `orders/create` with raw body `B` and header `x-shopify-hmac-sha256: H` (valid for `B`).
2. Attacker replays the request to the app's webhook endpoint, keeping the body `B` and header `H` unchanged, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` (via `Registry.process`) recomputes HMAC over `B` only and it matches `H`, so validation passes: [6](#0-5) 
4. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: B, ...)` and invokes the registered handler as if the payload genuinely belonged to `victim.myshopify.com`: [7](#0-6) 
5. Any host-side logic keyed on `data.shop` now operates on attacker-controlled content under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
