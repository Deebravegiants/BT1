Confirmed. This is a solid analog matching the required bug class.

### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Shop Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` field solely from the unauthenticated `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` HTTP header, while the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. `Registry.process` trusts `request.shop` and hands it to the host app's webhook handler as the authoritative tenant identifier, without that value ever being included in the signed data.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor reads directly from an HTTP header that is never part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then constructs `WebhookMetadata` using `request.shop` and passes it straight to the registered handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` const with no further verification performed by the gem: [4](#0-3) 

**Identity binding broken (as an equality):**
`shop_bound_by_hmac (∅, since to_signable_string == @raw_body only)` ≠ `shop_used_by_handler (request.shop, read from an unauthenticated header)`.

The HMAC only proves the body bytes were signed by Shopify with the app's `client_secret`; it says nothing about which shop header accompanied that body. Any party who can obtain one valid `(raw_body, hmac)` pair for *any* shop — trivially available to an unprivileged user who installs the app on their own free/dev store and receives their own legitimate webhooks — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary value in the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still return `true` because it never inspects headers, and `Registry.process` will deliver the attacker-chosen `shop` value to the host application's handler as if it were authentic.

### Impact Explanation
Host applications rely on `WebhookMetadata#shop` as the tenant key to route data (e.g., deleting customer data, updating per-shop billing/subscription state, invalidating sessions, or writing to a per-shop data store) triggered by webhook topics such as `customers/redact`, `app/uninstalled`, `shop/update`, etc. Because the shop value is unauthenticated relative to the HMAC, an attacker who owns one legitimate installation can forge webhook deliveries that are processed under a victim shop's identity, causing cross-tenant data mutation/exfiltration in the host app — meeting the "cross-tenant access" Critical impact bar.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on a shop the attacker controls (trivial — free development stores are unrestricted), (2) capturing one real webhook delivery (raw body + `X-Shopify-Hmac-Sha256` header) sent to their own endpoint, and (3) replaying that exact body/HMAC pair to the target application's webhook endpoint with a modified `Shop-Domain`/`X-Shopify-Shop-Domain` header. No access to Shopify's `client_secret`, TLS interception, or victim credentials is needed, and the gem itself performs no cross-check between the header-derived shop and the HMAC-covered content.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) values into the data verified by the HMAC, or otherwise cryptographically tie the header-derived shop to a value that is authenticated — e.g., only trust `request.shop` for a topic/webhook_id combination that the host app has independently confirmed via a signed source, or require the shop domain to be embedded in and validated against the signed body rather than sourced purely from headers. At minimum, document prominently that `WebhookMetadata#shop` is not covered by HMAC verification so host applications do not treat it as an authenticated tenant identifier.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a store they legitimately control) and registers a webhook (e.g. `customers/redact`).
2. Shopify delivers a real webhook to the app's endpoint:
   - Header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - Header `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body>`
   - Body: `raw_body`
3. Attacker captures `raw_body` and the valid `X-Shopify-Hmac-Sha256` value (they own this data since it was delivered to their own server).
4. Attacker resends the identical request to the app's webhook endpoint, only changing the header to `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. In `ShopifyAPI::Webhooks::Registry.process`:
   - `Utils::HmacValidator.validate(request)` returns `true` because it only re-computes the HMAC over `@raw_body`, which is unchanged (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
   - `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`).
6. The host application's `WebhookHandler#handle` executes attacker-controlled webhook content under the victim's shop identity, achieving cross-tenant impact.

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
