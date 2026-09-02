### Title
Webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) headers are not covered by the HMAC, allowing cross-tenant identity spoofing in `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking that `Utils::HmacValidator.validate(request)` succeeds, and that validation is computed only over the raw request body. The `shop`, `topic`, `api-version`, and `webhook-id` values, which are taken verbatim from unauthenticated HTTP headers, are then handed to the host application's `WebhookHandler` as the trusted tenant identifier, without ever being included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `api_version`, and `webhook_id` are read straight from client-supplied headers with no cryptographic binding: [2](#0-1) 

`Registry.process` verifies the request using `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` — i.e. only the raw body — and on success immediately trusts `request.shop`, `request.topic`, etc. to construct the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

The equality that should hold is: `shop header used for HMAC computation == shop header the application acts on`. In this gem it does not — the HMAC binds only the body bytes, not the `shop-domain` header that identifies which tenant the event belongs to.

Because Shopify apps share a single `client_secret`/`api_secret_key` across *all* installed shops, any merchant who has installed the app (an "unprivileged internet user" relative to other tenants of the same app) can trigger a legitimate webhook for their own shop, capture the valid `hmac-sha256` value (which depends only on the raw body, itself attacker-controllable to a large degree, e.g. free-text fields on their own store's resources), and then replay/forge a request to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a *different* victim shop. Because `to_signable_string` never includes the shop header, the forged request still passes `HmacValidator.validate`, and `Registry.process` will dispatch `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))`, causing the host app to act as if the event legitimately came from the victim tenant.

### Impact Explanation
This breaks the shop-identity boundary between tenants of the same app: an attacker who is a legitimate (but unprivileged, relative to other merchants) user of the app can make it process fabricated data under another merchant's `shop` identity. Depending on how the host app uses `WebhookMetadata#shop` (e.g., looking up/creating records, invalidating caches, triggering `shop/redact`-style destructive flows, or feeding data into per-tenant state), this enables cross-tenant data corruption or spoofed events, meeting the "cross-tenant access" bar for a High-severity finding.

### Likelihood Explanation
The attacker only needs to be a merchant who has installed the target app (no elevated privilege, no leaked secrets, no code execution) — this is a fairly low bar for a real "unprivileged internet user" relative to other tenants. The attack requires generating a webhook whose *body* is acceptable/replayable and swapping only the `shop-domain` header, which is straightforward since headers are entirely separate from the HMAC-covered payload.

### Recommendation
Bind the tenant/topic identity into the verified signature material, or independently verify that `request.shop` corresponds to a shop with an active, known session/installation before trusting it in `WebhookMetadata`. At minimum, document/require that host apps validate `data.shop` against their own installed-shops list before acting on webhook payloads, and consider including the `shop-domain`, `topic`, and `webhook-id` headers as part of the value verified by `HmacValidator` (mirroring how `AuthQuery#to_signable_string` includes all security-relevant fields, not just the body).

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com` (both merchants can independently install any public app).
2. Attacker triggers a legitimate webhook event on their own shop (e.g., updates a product), causing Shopify to POST to the app's registered webhook URL with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of raw body, computed with the app's single shared secret>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: products/update`
3. Attacker intercepts/replays this exact raw body to the same webhook endpoint, only changing `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and it matches, since the header was never part of the signed content: [1](#0-0) 
5. `Registry.process` proceeds to call `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))`: [5](#0-4) 
6. The host application processes attacker-controlled data believing it originated from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
