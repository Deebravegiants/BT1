### Title
Webhook `shop-domain` (and `topic`) headers are not covered by the HMAC signature, enabling cross-tenant webhook shop-spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator` verifies the HMAC exclusively against that body. The `shop` (and `topic`) values, which are read straight from the unauthenticated `X-Shopify-Shop-Domain`/`X-Shopify-Topic` headers, are never included in the signed material, yet they are forwarded unchanged into `WebhookMetadata` and handed to the app's webhook handler as the authoritative tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as just the raw body: [1](#0-0) 

`shop` is read from a header that is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC purely over `verifiable_query.to_signable_string`, i.e. the body only: [3](#0-2) 

`Registry.process` accepts any request whose body/HMAC pair validates, then trusts `request.shop` (and `request.topic`) as-is when building `WebhookMetadata` for the handler: [4](#0-3) 

`WebhookMetadata.shop` is a plain, unauthenticated string field passed straight to app code: [5](#0-4) 

The gem's own documentation shows apps are expected to key their per-tenant processing directly off `data.shop`: [6](#0-5) 

This is the exact analog described in the reference bug class: an attacker-controllable field (`shop`) is *acted on* by downstream logic but is *not covered* by the HMAC that is supposed to bind the request to a specific, authenticated shop. Formally, the gem should guarantee `hmac_verified_body ⟺ shop_used_by_handler`, but instead it only guarantees `hmac_verified_body`, while `shop_used_by_handler` is taken from an independent, unauthenticated channel.

Because a given app uses the same `api_secret_key` (the app's `client_secret`) for webhook HMACs across every shop that installs it, any attacker who legitimately installs the app on their own store can capture a valid `(raw_body, hmac)` pair (e.g., by triggering `orders/create` on their own shop) and then replay that exact body/HMAC to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain: victim-shop.myshopify.com`. `HmacValidator.validate` still passes because it never inspected the shop header, so `Registry.process` dispatches the attacker's payload to the handler labeled as belonging to `victim-shop.myshopify.com`.

### Impact Explanation
This breaks the tenant boundary the HMAC is meant to enforce: an unprivileged attacker (any developer/merchant who can install the target app on their own store) can inject attacker-controlled webhook data that the host application will process as if it originated from an arbitrary victim shop. Any app that follows the gem's documented pattern of dispatching/persisting webhook data keyed by `data.shop` is exposed to cross-tenant data corruption or unauthorized cross-tenant state changes — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple shops (which is the normal SaaS app model): obtaining a valid `(body, hmac)` pair only requires installing the app on an attacker-controlled shop, a routine, unprivileged action, and no access to `api_secret_key`, tokens, or the target shop's credentials is required.

### Recommendation
Bind the shop (and ideally topic) into the signed material, or otherwise cryptographically tie the verified request to the shop identity — e.g., include the `shop-domain` header value in `to_signable_string`/`HmacValidator` verification, or cross-check `request.shop` against a shop the app already has a stored, HMAC/OAuth-verified relationship with before dispatching to the handler. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant routing without additional verification (e.g., checking it against an existing installed-shop record).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `orders/create`) and captures the raw POST: body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — valid because the app's `api_secret_key` is shared across all shops.
3. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb` lines 26-31, `lib/shopify_api/webhooks/request.rb` lines 35-38).
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and invokes the app handler (`lib/shopify_api/webhooks/registry.rb` lines 188-200).
6. The app handler, following the documented pattern of trusting `data.shop`, processes/persists attacker-controlled data under the victim shop's tenant context.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
