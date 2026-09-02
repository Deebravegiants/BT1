This confirms the finding: `WebhookMetadata.shop` is populated directly from the unauthenticated header value, and the app's `WebhookHandler#handle` interface hands that `shop` straight to consumer code as the tenant identifier for the webhook.

### Title
Webhook shop domain is not covered by HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` (and `topic`, `api_version`, `webhook_id`) values come from HTTP headers that are never included in the signed payload. `Registry.process` validates only that the body's HMAC matches, then trusts the header-derived `shop` as the tenant identity passed to the host application's webhook handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` accessor is derived purely from the `x-shopify-shop-domain`/`shopify-shop-domain` header, with no cryptographic binding to the HMAC: [2](#0-1) .

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only proves the raw body matches the HMAC computed with the app's shared `api_secret_key` — it says nothing about which shop the header claims: [3](#0-2) . The (unauthenticated) `request.shop` is then forwarded directly into `WebhookMetadata`, which is the sole tenant identifier exposed to the host application's handler: [4](#0-3) .

Critically, the webhook HMAC secret (`Context.api_secret_key`, i.e., the app's `client_secret`) is shared across *all* shops that have installed the app — it is not shop-specific. Any unprivileged user who can install the app on their own store (or otherwise trigger/observe a legitimate webhook delivery for their own shop) legitimately obtains a `(raw_body, valid_hmac)` pair signed with that shared secret. Because `shop` is excluded from `to_signable_string`, that same valid `(raw_body, hmac)` pair remains valid when replayed to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` header value pointing at a victim shop.

This breaks the intended identity binding:
`shop authenticated by HMAC` ≠ `shop used as the tenant key in WebhookMetadata`

Before the attack: the app assumes any request that passes `HmacValidator.validate` is an authentic Shopify webhook *for the domain the header claims*. After the attacker's replay: the HMAC still validates (it never covered `shop`), but `WebhookMetadata#shop` is fully attacker-controlled and can be set to any victim's `myshopify.com` domain.

### Impact Explanation
This qualifies as Critical - cross-tenant access. Any application logic keyed on `data.shop` (e.g., updating per-shop records, writing merchant-scoped data, invalidating shop settings, triggering shop-specific side effects such as uninstall/data-erasure handling) can be manipulated by an attacker who owns their own shop installation, allowing them to inject attacker-controlled webhook bodies attributed to a victim shop of their choosing — a classic cross-tenant identity confusion enabled purely through this gem's webhook verification API.

### Likelihood Explanation
Moderate-to-high likelihood: exploitation only requires the attacker to install the app themselves (a normal, unprivileged action available to any merchant) to obtain a valid `(body, hmac)` pair, then send a forged HTTP request to the app's public webhook endpoint with a spoofed `shop-domain` header. No access to the victim's credentials, token, or `client_secret` is required.

### Recommendation
Include the shop domain (and topic/webhook id, if they are meant to be trusted) in the HMAC-signable string, or otherwise cryptographically bind the shop identity to the signed payload before trusting `request.shop` as the tenant key in `WebhookMetadata`. At minimum, document that `WebhookHandler` implementers cannot rely on `data.shop` as an authenticated tenant identifier unless it is bound into the signature — and change `to_signable_string` to enforce that binding within the gem itself.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, becoming a legitimate merchant of the app.
2. Shopify sends the attacker's shop a real webhook: `raw_body = '{"id":123,...}'`, header `x-shopify-hmac-sha256 = valid_hmac_of(raw_body, app_secret)`, header `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `raw_body` and `valid_hmac`, then sends a new POST directly to the app's webhook endpoint with the same `raw_body`/`x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [5](#0-4)  which succeeds because the signature only covers `raw_body`.
5. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: attacker_controlled_json, ...)`, and the host app processes attacker-controlled data as if it originated from `victim.myshopify.com`.

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
