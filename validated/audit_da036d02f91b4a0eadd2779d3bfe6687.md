This confirms the vulnerability. The `WebhookMetadata` struct passed to every app's `WebhookHandler#handle` includes `shop` and `topic` fields sourced directly from `Request#shop`/`Request#topic`, which read unauthenticated HTTP headers, while `Utils::HmacValidator.validate` only verifies the raw JSON body via `Request#to_signable_string`.

### Title
Webhook `shop` and `topic` identity fields are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by checking the HMAC signature over the raw request body [1](#0-0) . The `Utils::HmacValidator` computes the signature over `verifiable_query.to_signable_string`, which for `Webhooks::Request` returns only `@raw_body` [2](#0-1) . However, the `shop`, `topic`, `webhook_id`, and `api_version` values used downstream (including the `shop` value passed to every app's `WebhookHandler#handle`) are read straight from HTTP headers, which are never included in the signed material [3](#0-2) . This breaks the intended identity binding: `hmac(raw_body) == hmac(raw_body)` verifies successfully, but `header.shop-domain` used by the handler is never checked to equal the tenant that actually generated/signed the body.

### Finding Description
`Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` all as plain header reads [3](#0-2) , while `to_signable_string` — the only thing actually authenticated by `HmacValidator.validate` — returns solely the raw body bytes [2](#0-1) . `Registry.process` raises `InvalidWebhookError` only if the HMAC over the body is invalid, then immediately trusts `request.topic` and `request.shop` to build the `WebhookMetadata` delivered to the app's handler [4](#0-3) . The `WebhookMetadata#shop` field [5](#0-4)  is exactly the value host applications use to look up which merchant/tenant's stored access token or database row the webhook belongs to. Because the header is not part of the signed payload, the equality the gem should guarantee — `shop-domain header == shop that produced/authorized this HMAC-signed body` — never actually holds; the HMAC only proves "someone possessing `api_secret_key` signed this exact body," not "this body came from the shop named in this header."

An unprivileged internet user who is themselves a legitimately installed merchant (and thus receives genuinely-signed webhooks from Shopify for their own shop) can capture one such request/response pair and resend the identical `raw_body` + `x-shopify-hmac-sha256` value to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header naming a different, victim tenant. `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` forwards the attacker-chosen `shop`/`topic` straight into the handler as if Shopify itself had asserted it for that tenant.

### Impact Explanation
This is a cross-tenant identity-binding break: in a multi-tenant Shopify app (the common integration pattern this gem targets), the webhook handler uses `WebhookMetadata#shop` to select which merchant's access token, database records, or business logic to act on. An attacker who controls one installed shop can forge the *tenant attribution* of a webhook payload they legitimately received, causing the host application to process attacker-supplied webhook content (product/order/customer data, GDPR redact topics, etc.) as if it originated from a victim shop, or to invoke handlers/topics not actually authorized for that body. This matches the "Critical: cross-tenant access" category, since it lets one tenant's traffic be attributed to another tenant purely by manipulating unauthenticated headers.

### Likelihood Explanation
No special credentials beyond a normal, free Shopify Partner/merchant account are required — the attacker only needs to install the target app on their own shop to receive real, correctly HMAC-signed webhooks, then replay the request with a modified `shop-domain`/`topic` header. Because the HMAC computation in `HmacValidator.compute_signature` never includes these headers [6](#0-5) , the tampered request passes validation deterministically every time, with no dependency on timing, race conditions, or infrastructure quirks.

### Recommendation
Bind the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) into the HMAC-signed material, or otherwise cryptographically tie them to the raw body before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, `Webhooks::Request#to_signable_string` should not omit the shop/topic headers that the rest of the gem and host applications treat as authenticated identity, and `HmacValidator` (or a new validator) should verify that these fields match what Shopify actually signed rather than passing them through unauthenticated.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; capture a legitimate webhook Shopify sends to the app's endpoint, e.g.:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-signature-of-body>
   x-shopify-shop-domain: attacker.myshopify.com
   body: {"id": 123, ...}
   ```
2. Resend the identical body and `x-shopify-hmac-sha256` value to the same endpoint, but change the header:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes the signature only over `request.to_signable_string` (the unchanged raw body) and finds it valid [7](#0-6) .
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` [8](#0-7)  and the host app processes attacker-controlled data under the victim shop's identity/tenant context.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
