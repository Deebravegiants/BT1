Found it: in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`), the HMAC validator only covers `request.to_signable_string`, which is the raw request body (`lib/shopify_api/webhooks/request.rb:36-38`). The `shop` field, taken from the `X-Shopify-Shop-Domain` header (`lib/shopify_api/webhooks/request.rb:20-23`), is never included in the signed bytes, yet it is passed straight into `WebhookMetadata` and handed to the app's handler as the tenant identifier (`registry.rb:198-199`).

### Title
Webhook tenant identity (`shop`) is not covered by HMAC verification, allowing shop spoofing in webhook processing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body (`@raw_body`). `shop` is read from the `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` header via `shopify_header("shop-domain")` and is completely outside the bytes the HMAC covers.

### Finding Description
`Utils::HmacValidator.validate(request)` (used in `Registry.process`, `lib/shopify_api/webhooks/registry.rb:190`) recomputes the HMAC over `request.to_signable_string`, i.e. the raw JSON body only [1](#0-0) . The `shop` attribute is derived independently from a header that is not part of that signed string [2](#0-1) . The gem itself never cross-checks that the header-derived `shop` corresponds to the tenant whose secret validated the body; it simply forwards it into `WebhookMetadata` for the handler [3](#0-2) .

This breaks the binding: `shop == bytes_covered_by_hmac`. An attacker who can produce a validly-HMAC'd body (e.g., by replaying or forging any accepted webhook payload signed with the shared `api_secret_key` for their own shop) can freely alter the `X-Shopify-Shop-Domain` header value sent alongside it, since that header is never part of what is verified. The HMAC only proves body integrity for a client possessing the shared secret; it says nothing about which shop the header claims to be.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` (the value produced by this gem) as the tenant key to look up sessions, apply data, or route redaction requests without doing its own separate binding, cross-tenant data confusion becomes possible purely because the library asserts the payload is "verified" while `shop` was never part of that verification. This matches the "cross-tenant access" impact category, since the library's own verified-request object exposes an unauthenticated tenant identifier as if it were authenticated.

### Likelihood Explanation
Exploitability requires that an attacker already control or forge a request carrying a valid HMAC (i.e., possess or reuse a validly-signed payload for the shared api_secret_key, e.g. via a legitimate webhook from their own store) and then modify the shop-domain header before delivery to the app's webhook endpoint. This is plausible for any developer who tests/relays webhooks, or in scenarios where webhook delivery paths are proxied, since nothing in this gem stops the header from being swapped independent of body signing.

### Recommendation
Include the `shop`/`shop-domain` header value in the signable string covered by the HMAC (mirroring how `AuthQuery#to_signable_string` binds `shop` into its signed representation, see `lib/shopify_api/auth/oauth/auth_query.rb:34-43`), or otherwise cryptographically bind the shop identity to the payload before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Capture (or generate in a test shop) a legitimately signed webhook request: body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and `X-Shopify-Hmac-Sha256` computed over `B` with the shared `api_secret_key`.
2. Resend the same body `B` and the same valid HMAC header to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) still returns `true`, because validation only checks `@raw_body` (`Request#to_signable_string`) against the HMAC — the shop header is irrelevant to that check.
4. `WebhookMetadata.new(... shop: request.shop ...)` is built with `shop: "victim-shop.myshopify.com"` (`registry.rb:198-199`), and the app's handler processes the (validly-signed) body as if it belonged to `victim-shop`, despite the body actually being signed/originated for `attacker-shop`.

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
