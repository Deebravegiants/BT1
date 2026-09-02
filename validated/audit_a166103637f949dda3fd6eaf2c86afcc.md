### Title
Webhook `shop-domain` (and topic/webhook-id/api-version) are trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while `ShopifyAPI::Webhooks::Registry.process` treats the unauthenticated `shop-domain` header as the trusted tenant identifier once `Utils::HmacValidator.validate` passes. This breaks the identity binding `shop_verified_by_hmac == shop_acted_on`, because the shop identity is never part of what the HMAC actually verifies.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` is instead read straight from an attacker-controllable HTTP header, entirely independent of the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body, then immediately forwards the header-derived, unauthenticated `request.shop` to the app's handler as if it were an authenticated tenant identifier: [3](#0-2) 

Because the `api_secret_key` is shared by the app across every installed shop (it is not per-tenant), any merchant who installs the app on their own store legitimately receives real webhooks with a valid `(raw_body, hmac)` pair signed by Shopify using that same shared secret. That attacker-merchant can capture one such valid `(body, hmac)` pair from their own tenant and replay it to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`/`shopify-api-version`) header values to name a *different* victim shop. `Utils::HmacValidator.validate` will still succeed because it only re-computes the digest over `to_signable_string`, which is just `@raw_body`: [4](#0-3) 

The forged request is accepted, and `WebhookMetadata` is built with the attacker-chosen `shop`, `topic`, `webhook_id`, and `api_version`, none of which were part of what the signature actually attested to. Any host application that uses `data.shop` from the handler callback to route or attribute webhook data to a tenant (the intended and documented use, per `WebhookMetadata`) will process attacker-controlled body content under a victim shop's identity — a cross-tenant confusion rooted entirely in this gem's own verification logic, not a documented host-app misuse.

### Impact Explanation
This allows an unprivileged but validly-onboarded merchant to inject forged webhook events attributed to a different tenant (shop) of the same app, since the shop/topic/webhook-id fields consumed by the handler are not bound to the cryptographic signature. This is a cross-tenant identity confusion caused directly by the gem's `Request`/`Registry` design.

### Likelihood Explanation
Any app developer using this gem's webhook flow (`ShopifyAPI::Webhooks::Registry.process`) is affected without any special configuration. Obtaining one valid `(body, hmac)` pair only requires installing the app on the attacker's own store — no access to `api_secret_key`, access tokens, or any other privileged credential is required.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable string, or otherwise cryptographically bind them to the verified payload, instead of trusting header values that sit outside the signed content. At minimum, `Registry.process` should not treat `request.shop`/`request.topic`/`request.webhook_id` as authenticated data derived from `Utils::HmacValidator.validate`.

### Proof of Concept
1. Register a webhook handler for topic `orders/create` and install the app on Shop A (attacker-controlled). Capture a real inbound webhook request: raw body `B` and header `shopify-hmac-sha256: H` (valid, computed by Shopify with the app's shared `api_secret_key`).
2. Replay the exact same `(B, H)` pair to the app's webhook endpoint, but change `shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally the topic/webhook-id headers).
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only recomputes HMAC over `@raw_body`, per: [5](#0-4) 
4. `Registry.process` invokes the handler with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` even though nothing about the victim shop was ever cryptographically verified, confirming the identity-binding break at: [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
