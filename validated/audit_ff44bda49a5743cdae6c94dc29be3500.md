Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `topic`, `shop`, `api_version`, and `webhook_id` are all pulled unauthenticated from HTTP headers via `shopify_header`, and none of those fields participate in the HMAC computation.I have enough evidence to finalize the analog finding on the webhook HMAC binding gap.

### Title
Webhook shop/topic/api-version/id headers are not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC over the raw request body only. The `shop`, `topic`, `api_version`, and `webhook_id` values that `ShopifyAPI::Webhooks::Registry.process` passes on to the host application's handler are read directly, and unauthenticated, from HTTP headers that are never part of the signed content.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery`'s `hmac` against `to_signable_string`. For webhooks, `Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to that HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e., only the body), then constructs `WebhookMetadata` directly from these unauthenticated header fields and hands it to the app's handler, which uses `shop` as the tenant key: [3](#0-2) 

The equality the gem is implicitly relying on is: `shop_verified_by_hmac == shop_used_for_tenant_routing`. In reality, the HMAC only proves `HMAC(secret, raw_body)` is correct — it says nothing about which shop, topic, webhook id, or API version that body belongs to. Any request whose `raw_body` happens to match a signature the attacker has already observed (e.g., a webhook Shopify sent to the attacker's own shop's endpoint for a payload with predictable/fixed content, such as `shop/redact`, `customers/redact`, or any topic whose body content is empty/constant/attacker-controlled) can be replayed with a different `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` header while the HMAC header is left untouched — the signature will still validate because those headers were never part of the signed bytes.

### Impact Explanation
This breaks the tenant-authentication boundary that host applications rely on: the gem tells the app "this HMAC-verified webhook is for shop X, topic Y" when in fact only the body bytes were verified, not the shop/topic association. A host application that trusts `WebhookMetadata#shop` (as the library's own tests and docs assume `data.shop` is trustworthy right after `Utils::HmacValidator.validate` passes) can be made to process, store, or act on data under the wrong merchant's tenant context — i.e., cross-tenant confusion driven entirely by attacker-controlled headers, despite HMAC validation "passing."

### Likelihood Explanation
Medium: the attacker needs a legitimately signed raw body/HMAC pair (obtainable from webhooks Shopify already sends to any shop/app installation the attacker controls, including topics with static/empty bodies such as the mandatory `shop/redact` topic), and needs to be able to reach the app's public webhook endpoint with modified headers — both are realistic for an unprivileged internet user/app-installer.

### Recommendation
Include `topic`, `shop-domain`, `api-version`, and `webhook-id` in the HMAC-signed content check (or otherwise independently verify that the shop header corresponds to a shop that legitimately triggered this specific signed body) instead of relying on `to_signable_string` returning only `@raw_body`. At minimum, document and enforce that host applications must not trust `WebhookMetadata#shop`/`#topic` without additional out-of-band verification (e.g., cross-checking against a known/registered shop for that webhook subscription).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook whose body is fixed/predictable, e.g., the mandatory `shop/redact` topic, capturing the real `x-shopify-hmac-sha256` header Shopify computed for that raw body.
2. Attacker resends that exact raw body and HMAC header to the app's webhook endpoint but swaps `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and/or swaps `x-shopify-topic`/`x-shopify-webhook-id`).
3. `Utils::HmacValidator.validate` recomputes `HMAC(secret, raw_body)` — unchanged — and passes, because `to_signable_string` never included the shop/topic/webhook-id headers.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` from the spoofed headers and invokes the app's handler believing the event is authentically from `victim-shop.myshopify.com`, even though nothing about that shop association was ever HMAC-verified.

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
