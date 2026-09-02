### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only, while the `shop` (tenant identity) is read from the `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` HTTP header, which is never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identifier passed to the host application's handler. Because the tenant-identifying field is not bound to the signature, a legitimate (but malicious) merchant who owns one shop can capture a validly-signed webhook delivered to their own store and replay the identical raw body + HMAC to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop, causing the application to process attacker-controlled webhook data under another tenant's identity.

### Finding Description
In `lib/shopify_api/webhooks/request.rb`:
- `hmac` is derived purely from the `hmac-sha256` header.
- `to_signable_string` returns `@raw_body` only [1](#0-0) .
- `shop` is read from a header that plays no part in signature computation [2](#0-1) .

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (the raw body) against the secret, and — once validation succeeds — forwards `request.shop` untouched to the webhook handler as the tenant identity: [3](#0-2) .

`Utils::HmacValidator.validate` confirms that only the fields included in `to_signable_string` are cryptographically checked [4](#0-3) .

This breaks the identity binding: **shop-header-claimed-tenant == shop-that-produced-this-signed-body**. The signature only proves "this body byte sequence was produced with the shared secret," not "this body was produced *for* the shop named in this header." Because any merchant can install the app on a shop they control and receive genuinely-signed webhooks for that shop, they possess valid `(raw_body, hmac)` pairs that pass `HmacValidator.validate` regardless of which `shop-domain` header accompanies them. Re-POSTing the same body+hmac with a different `shop-domain` header value (a header entirely under the sender's control at the HTTP layer) passes validation and is attributed to the spoofed tenant.

### Impact Explanation
Applications built on this gem (e.g. via `ShopifyAPI::Webhooks::Registry.process`) rely on `WebhookMetadata#shop` to decide which tenant's data/session the webhook payload should be applied to — for example, order/product/customer webhooks, `app/uninstalled`, or GDPR data-request/erasure webhooks. Since the shop identity is unauthenticated relative to the signature, an attacker (any merchant who has installed the app on their own store) can inject attacker-controlled webhook bodies that the host application will process as belonging to a different, victim shop. Depending on how the host app uses the shop field (e.g., to look up and act on that shop's stored access token, to trigger data deletion, or to update per-shop state), this can result in cross-tenant data corruption or cross-tenant action execution — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Moderate-to-high: exploitation requires only that the attacker be a legitimate (if malicious) merchant who has installed the target app on a shop they control — no special privileges, no leaked secret, and no access to `api_secret_key` are needed. They simply capture one of their own genuinely-signed webhook deliveries and replay it with a forged `shop-domain` header to the app's webhook endpoint.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the `shop-domain` header to the request:
- Prefer deriving/confirming tenant identity from a value embedded in the signed body (many Shopify webhook payloads already carry shop-scoped identifiers), rather than solely from an unsigned header.
- Alternatively, require the host application to independently verify that `request.shop` corresponds to a shop with an active, matching installation/session before trusting it, and document this requirement prominently since the gem itself cannot enforce it without protocol support from Shopify.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g., `products/update`) and capture the raw request body `B` and header `Shopify-Hmac-Sha256: H` — this is a validly Shopify-signed pair for shop `attacker.myshopify.com`.
2. Replay an HTTP POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
   - Header `X-Shopify-Topic`: unchanged
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `H` against `B`. `request.shop` returns `"victim.myshopify.com"` even though `B` was generated for `attacker.myshopify.com`. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled data attributed to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
