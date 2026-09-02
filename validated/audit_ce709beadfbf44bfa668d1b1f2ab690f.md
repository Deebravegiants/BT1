### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, but then extracts the tenant identity (`shop`) from an HTTP header that is never included in that signature. Any attacker who can obtain one legitimately-signed `(body, hmac)` pair from Shopify (e.g. for a shop they themselves own) can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the signature check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then dispatches to the handler using the unauthenticated `request.shop` value as the tenant identity: [3](#0-2) 

This is the exact identity-binding break requested: the entity the HMAC actually authenticates (`raw_body` signed with the app's `client_secret`) is not equal to the entity the code treats as authenticated (`request.shop`, taken from a header outside the signed payload). `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) only ever calls `to_signable_string`, so it cannot detect header tampering.

### Impact Explanation
An app built on this gem uses `WebhookMetadata#shop` (populated from `request.shop`) to decide which merchant's data the webhook body applies to — e.g. persisting order/customer data, or honoring `customers/redact` / `shop/redact` GDPR requests for "that" shop. Because the shop value is unauthenticated, an attacker can cause the host app to apply a legitimately-signed payload to a different tenant than the one it actually came from, i.e. cross-tenant data injection/mutation using the app's own webhook trust relationship.

### Likelihood Explanation
Exploitation requires the attacker to possess one valid `(raw_body, hmac)` pair signed with the app's `client_secret`. This is trivial to obtain without ever knowing the secret: any merchant who has installed the app receives real webhook deliveries for their own store, each carrying a body+HMAC that Shopify computed with the app's secret. That merchant (an otherwise unprivileged tenant of the app) can capture that delivery and replay the identical body/HMAC to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` (or `X-Shopify-Hmac-Sha256` equivalent alt-header) pointing at a victim shop, since nothing in this gem ties the header to the signed content.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable string, or otherwise cryptographically bind them to the payload before trusting them (e.g. require the app layer to cross-check `request.shop` against the shop associated with the session/subscription for that topic/webhook id before invoking the handler).

### Proof of Concept
1. App A (attacker-owned, has the target app installed) receives a genuine webhook: `POST /webhooks` with body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's `client_secret`), and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only and it matches `H`, so `Registry.process` proceeds.
4. `handler.handle` is invoked with `shop: "victim-shop.myshopify.com"` even though the payload never originated from Shopify for that shop, letting the attacker inject/mutate data attributed to a shop they do not control.

### Citations

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
