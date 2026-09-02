### Title
Webhook shop identity spoofing via HMAC scope gap enabling cross-tenant webhook injection - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating an HMAC computed only over the raw request body, then trusts a separate, unsigned HTTP header (`x-shopify-shop-domain`) as the tenant identity passed to the app's handler. Because the `shop` field is not part of the HMAC-covered material, an attacker who obtains one valid `(body, hmac)` pair can replay it with an arbitrary `shop` header and have it accepted as an authentic webhook for a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` includes `Utils::VerifiableQuery` and defines: [1](#0-0) 

`hmac` is read from the `hmac-sha256` header, and `shop` is read independently from the `shop-domain` header. Critically, the signable string used for verification is only the raw body: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string` (the raw body) and compares it to the received HMAC: [3](#0-2) 

`Registry.process` performs exactly this check and then forwards `request.shop` — a value that was never covered by the HMAC — directly into the handler as the tenant identity: [4](#0-3) 

The binding that should hold is:
`hmac_valid(body) == true` **should imply** `shop_header == shop_that_actually_sent_this_body`.

In reality the equality only proves `hmac_valid(body)`; `shop_header` is fully attacker-controlled and independent of the signature. Since all shops installed on a given app share the same signing secret (`Context.api_secret_key`), any legitimate webhook payload the attacker can observe (e.g. a webhook delivered to their own shop's endpoint, which they control, or one captured via any means available to a merchant of the app) yields a valid `(body, hmac)` pair. The attacker can then replay that exact body/hmac to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop domain. `Utils::HmacValidator.validate` still returns `true` (it never inspects `shop`), so `Registry.process` calls the handler with `WebhookMetadata.new(topic:, shop: <attacker-chosen victim shop>, body:, ...)`.

### Impact Explanation
This breaks the tenant/shop authentication boundary the gem is documented to enforce for webhook processing: host applications reasonably treat a passing `Utils::HmacValidator.validate` result as proof that both the payload *and* its declared shop originated from Shopify for that shop. Because `shop` is excluded from the signed content, an attacker can inject events attributed to a different tenant (cross-tenant data confusion), e.g. triggering shop-scoped side effects (inventory sync, order processing, uninstall/app-lifecycle handling, tenant-keyed cache invalidation, etc.) under a victim shop's identity. This matches the Critical-tier "cross-tenant access" impact category, since the tenant binding the host application relies on (shop identity of webhook events) is forgeable by any actor who can obtain a single valid signed payload.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one legitimate `(raw_body, hmac)` pair signed with the app's shared secret. The most direct source is the attacker's own shop, which — as an installer of the app — regularly receives real webhooks signed with the same `api_secret_key`, all with different content but the same secret; the attacker can also craft their own store's events (e.g., placing/cancelling orders) to generate bodies of their choosing, then replay the resulting valid `hmac` alongside a forged `shop-domain` header. No knowledge of `api_secret_key` itself, no TLS interception, and no privileged account are required — only ordinary interaction as an app installer/merchant, which is an "unprivileged internet user" relative to other tenants of the app. This is a straightforward, low-effort replay because `Request#initialize` performs no header/body binding checks beyond presence.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable material, or otherwise cryptographically bind the `shop` header to the signed body before trusting it as tenant identity — e.g. compute/verify the signature over `shop + raw_body` (or require it to match a shop already known/authorized for the delivered `topic`/subscription id looked up server-side) rather than accepting an independent, unauthenticated header as the source of truth for tenant routing.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (or otherwise causes/observes a webhook delivery to their own endpoint).
2. Attacker captures a legitimate webhook request: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — this is the same secret shared by all shops on the app.
3. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this passes because `B` and `H` are unmodified (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` proceeds to `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` where `request.shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-200`, `lib/shopify_api/webhooks/request.rb:20-23`), causing the host application to process the (attacker-supplied) payload as if it belonged to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
