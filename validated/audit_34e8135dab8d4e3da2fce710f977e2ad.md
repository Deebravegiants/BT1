Based on the analysis, I found a clear analog vulnerability in the webhook processing path.

### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` identity fields are read from unauthenticated headers, not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop, topic, webhook id, and API version that a webhook handler acts on entirely from HTTP headers, while `to_signable_string` (used by `HmacValidator`) signs only the raw body. This breaks the binding "bytes verified == bytes acted on" — the header-derived shop identity is never covered by the cryptographic signature that the library treats as proof of authenticity.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string`, and `Registry.process` gates all further processing on this check: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

But the values that `Registry.process` extracts and hands to the merchant's registered handler — `shop`, `topic`, `webhook_id`, `api_version` — all come from HTTP headers that are outside the signed payload: [3](#0-2) [4](#0-3) 

`HmacValidator.validate` only proves that `@raw_body` was produced by someone holding `api_secret_key`; it says nothing about which headers accompanied that body. Because `hmac()` itself is also read from a header (`shopify-hmac-sha256`) rather than being bound to the other headers, the equality the library implicitly relies on — "header-derived shop == HMAC-authenticated shop" — does not hold. Any request carrying a previously-observed valid `(raw_body, hmac)` pair passes `Utils::HmacValidator.validate`, regardless of which `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers are attached.

### Impact Explanation
If the host application (as documented in `docs/usage/webhooks.md`) relies on `WebhookMetadata#shop` returned by `Registry.process` to attribute the webhook body to a tenant (e.g., writing the payload into that shop's records, invalidating that shop's cache, or triggering per-shop side effects), an attacker who has captured any single legitimate webhook delivery (body + hmac) — for example by operating their own store and receiving webhooks for it, or observing one in transit — can resend the identical body/hmac pair to the app's public webhook endpoint with a different `shopify-shop-domain` header. `Utils::HmacValidator.validate` still returns `true` (it only checks the body), and the handler executes with attacker-chosen shop attribution. This is a cross-tenant identity-binding break consistent with the Critical "cross-tenant access" impact class in scope for this analysis.

### Likelihood Explanation
Exploitation only requires possession of one legitimately-signed webhook (attainable by any merchant/developer who installs their own app instance and observes their own webhook traffic, or via network capture on a non-TLS-protected replay path) plus the ability to POST to the app's public webhook endpoint with custom headers — no `api_secret_key` or privileged credentials are needed to forge new content, only replay of already-seen content with altered headers.

### Recommendation
Include the identity-bearing headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) in the signable material used for HMAC verification (or otherwise cryptographically bind them to the body, e.g., by hashing them alongside the payload before comparison), so that `Utils::HmacValidator.validate` fails if any of these fields are altered relative to what Shopify originally sent.

### Proof of Concept
1. App registers a webhook handler and receives a legitimate webhook for `shop-a.myshopify.com` with topic `orders/create`; capture the raw body `B` and the `shopify-hmac-sha256` header value `H` (valid because `HMAC(secret, B) == H`).
2. Attacker POSTs to the same webhook endpoint with the identical raw body `B` and header `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: shop-b.myshopify.com` (a different tenant) and/or a different `shopify-topic`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` builds the request object; `Utils::HmacValidator.validate(request)` calls `to_signable_string` which returns `B` only, so the HMAC check passes.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, where `shop` is `"shop-b.myshopify.com"` even though the payload actually originated from `shop-a`'s order — demonstrating the cross-tenant identity-binding break.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
