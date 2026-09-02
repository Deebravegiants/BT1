### Title
Webhook `shop` field is not covered by the HMAC, allowing cross-tenant shop-domain spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` entirely from HTTP headers, while `to_signable_string` (the data the HMAC actually protects) is only `@raw_body`. `Registry.process` validates the HMAC over the body but then trusts `request.shop` unconditionally when constructing `WebhookMetadata` and dispatching it to the app's handler. The binding "HMAC-verified bytes == bytes the app attributes to a specific shop" does not hold, because the `shop-domain` header sits outside the signed payload.

### Finding Description
- `Request#hmac` and `Request#to_signable_string` cover only the raw JSON body: [1](#0-0) [2](#0-1) 
- `Request#shop` (and `topic`, `webhook_id`, `api_version`) are read straight from headers, which are never part of the signed string: [3](#0-2) 
- `Registry.process` validates the HMAC against the body only, then immediately forwards `request.shop` to the handler as the authoritative tenant identifier, with no cross-check that the shop matches anything cryptographically bound to the payload: [4](#0-3) 

Because Shopify webhook HMACs are computed with the app's single shared `api_secret_key`/`client_secret` (the same key for every installed shop, confirmed by `HmacValidator.validate` using `Context.api_secret_key`), any shop that installs the app can legitimately trigger a webhook to itself, capture the exact `(raw_body, hmac)` pair delivered to the app's public endpoint, and then replay that same body+HMAC to the endpoint again while substituting a different `shopify-shop-domain` header value. `HmacValidator.validate` only checks that the body matches the signature under the shared secret — it has no way to know, and does not check, that the signature was ever associated with the shop name claimed in the (unsigned) header.

Equality that should hold but doesn't: `shop bound by HMAC == shop consumed by the handler`. In reality: `shop consumed by handler == arbitrary attacker-supplied header value`, while `HMAC` only proves `body was produced with app secret` (i.e., "by some install of this app"), not `body originated from shop X`.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` (from `Registry.process`) to select which shop/tenant's data to load, mutate, or delete is exposed to cross-tenant confusion: a malicious merchant who has installed the app can forge the `shop` attribution of a webhook payload they legitimately received, causing the host app to apply that payload's effects to a different shop's tenant context. This includes GDPR/mandatory topics (`shop/redact`, `customers/redact`, `customers/data_request`) and any ordinary webhook-driven state sync, potentially causing unauthorized cross-tenant data manipulation — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any party that can install the app on their own store (an "unprivileged internet user" from the perspective of other merchants) can obtain a valid `(body, hmac)` pair for themselves and replay it with a forged `shop-domain` header to the app's public webhook endpoint, since no additional secret or privileged access is required beyond having installed the app once. The only work required is capturing one webhook delivery and resending it with a modified header, which is fully attacker-controlled and requires no interaction with Shopify's servers beyond normal app installation.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-covered signable content, or otherwise cryptographically bind the shop to the payload before it reaches `to_signable_string`. At minimum, `Registry.process` (and any downstream consumer of `WebhookMetadata`) must not trust `request.shop` from an unauthenticated header as the sole tenant key; it should be cross-validated against session/tenant state already known to the app (e.g., verifying the shop is one that legitimately owns the resource IDs contained in the signed body) before dispatching to handlers.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook, capturing the exact headers and raw body Shopify sent, including a valid `shopify-hmac-sha256` value computed with the app's shared secret.
2. Attacker POSTs the same raw body and `shopify-hmac-sha256` value to the app's public webhook endpoint again, but replaces the `shopify-shop-domain` header with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (the raw body) against the HMAC — this succeeds because the body and secret are unchanged: [5](#0-4) 
4. `handler.handle` is invoked with `shop: request.shop`, now containing `victim-shop.myshopify.com`, even though the payload never originated from that shop: [6](#0-5) 
5. If the host app's handler uses `data.shop` to select which tenant's records to update/delete, the attacker has caused it to act on the victim's tenant using attacker-supplied data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
