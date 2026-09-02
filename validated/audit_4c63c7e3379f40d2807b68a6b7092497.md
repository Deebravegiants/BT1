Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` in `Registry.process` only authenticates the body bytes, never the `shop`, `topic`, or `webhook-id` header values that are then trusted and dispatched to the handler [2](#0-1) .

### Title
Webhook shop/topic/webhook-id identity is not bound to the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its verifiable signature only over the raw request body, while the `shop`, `topic`, and `webhook_id` values (read from HTTP headers) are excluded from the signed material and yet are trusted as the tenant identity for dispatch.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 
`shop`, `topic`, and `webhook_id` are read from headers that are never mixed into the signable string: [3](#0-2) 
`Registry.process` validates only this body-only HMAC via `Utils::HmacValidator.validate(request)` and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build `WebhookMetadata` for dispatch to the app's handler: [2](#0-1) 

Because all shops share the single app-level `api_secret_key`, an attacker who legitimately installs the app on any shop (an unprivileged action, e.g., a free development store) will receive genuinely-signed webhooks from Shopify for their own shop. The attacker can capture one `(raw_body, hmac)` pair from their own store, then replay it directly to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header to name a different, victim shop. Since the HMAC only covers `raw_body`, `Utils::HmacValidator.validate` still succeeds, and the handler receives `WebhookMetadata` claiming to be from the victim shop with attacker-controlled body content.

This breaks the intended identity binding: `shop_verified_by_hmac == shop_acted_on`. In fact, `shop` (and `topic`/`webhook_id`) are never part of the HMAC-verified bytes at all, so the equality never holds for those fields.

### Impact Explanation
This is a cross-tenant identity break: an app that keys any tenant-scoped action (e.g., syncing data, revoking access, mutating records, billing state) off `WebhookMetadata#shop` from a webhook handler can be tricked into applying attacker-controlled payloads under a victim shop's identity, since the gem provides no binding between the signed bytes and the shop that is dispatched to the handler. This matches the "Critical - cross-tenant access" category, since the confidentiality/integrity boundary between tenants (shops) sharing the same installed app is what's being violated, and the library-level primitive (`Registry.process`/`Webhooks::Request`) is what fails to enforce the binding.

### Likelihood Explanation
Exploitation requires only: (1) installing the app on any shop the attacker controls (not privileged — any developer/merchant can do this for free), (2) capturing one legitimately Shopify-signed webhook body+HMAC pair sent to the attacker's own endpoint, and (3) replaying it to the target app's public webhook URL with a modified `shop-domain` header. No secrets, tokens, or access to the victim's shop are required.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signable string used for HMAC verification, or otherwise independently authenticate the shop header against a value derived from bytes that are actually covered by the HMAC, before trusting `request.shop` for dispatch.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (an unprivileged action).
2. Shopify sends a legitimate webhook to the app's endpoint: `raw_body = B`, `hmac = HMAC(api_secret_key, B)`, header `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this `(B, hmac)` pair.
4. Attacker POSTs the same `B`/`hmac` to the app's webhook endpoint again, but sets header `shopify-shop-domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` in `Registry.process` passes because it only checks `B` against `hmac` [4](#0-3) .
6. `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` is built with `shop = "victim-shop.myshopify.com"` and dispatched to the app's registered handler [5](#0-4) , causing the app to process attacker-supplied data under the victim shop's identity.

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
