### Title
Webhook shop-domain header not covered by HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop` (and `topic`/`webhook-id`) values used downstream by the handler come from unauthenticated HTTP headers. `Utils::HmacValidator` only proves that the *body* bytes were signed with the app's `api_secret_key` — it never binds that proof to the `shop-domain` header that `Registry.process` later trusts and hands to the handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic tie to the body or the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC using `verifiable_query.to_signable_string` (the raw body only) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` accepts the request once this body-only HMAC check passes, then dispatches to the handler using `request.shop` (an unauthenticated header value) as the tenant identity: [4](#0-3) 

Because `api_secret_key` is a single per-app secret (not per-shop), any tenant that has installed the app receives genuine webhook deliveries whose body+HMAC pair is valid under that same shared secret. Since the `shop-domain` header is excluded from the signed content, an attacker who possesses one valid `(raw_body, hmac)` pair (e.g., from a webhook delivered for their own installed shop) can resend that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because it never inspects the header, so `Registry.process` invokes the handler with `shop: request.shop` pointing at a different (victim) tenant.

This breaks the identity binding: **shop that actually produced/owns the signed payload == shop the handler is told the payload came from**. The `shop` field is "acted on" (used to select tenant-scoped data in the handler) but is not covered by the HMAC that authenticates the request.

### Impact Explanation
This enables cross-tenant confusion in a multi-tenant Shopify app: a request can be made to look like it originated from a victim shop while it was actually a replay of legitimate content belonging to (or crafted for) a different shop. Depending on how the host app's webhook handler uses `data.shop` (e.g., to look up/update per-shop records, mark subscription/billing state, or trigger data sync), this can result in cross-tenant data manipulation or state corruption attributable to another merchant's shop identity, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Medium. It requires the attacker to already hold one valid signed webhook body (obtainable trivially by installing the app themselves as a normal merchant, since `api_secret_key` is shared across all shops of the app) and requires the host application's handler to trust `data.shop`/`WebhookMetadata#shop` as an authenticated tenant identifier — which is exactly how the gem's own documentation and `WebhookMetadata` struct present it (as a shop identity field alongside a verified webhook). The gem provides no warning or additional mechanism (e.g., binding the shop to the HMAC, or verifying shop against a known/expected value) to prevent this replay-with-header-substitution.

### Recommendation
Include the claimed shop domain (and ideally topic/webhook-id) in the HMAC-signable content, or independently verify that the shop asserted in the header matches an application-level expectation (e.g., a shop-specific secret, or cross-check against a per-shop registered webhook subscription) before trusting `request.shop` in `Registry.process`. At minimum, document clearly that `request.shop`/`WebhookMetadata#shop` is unauthenticated header data and must not be used as the sole tenant boundary without additional verification by the host app.

### Proof of Concept
1. App has two installed shops: `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both under the same app (`api_secret_key` shared).
2. Attacker's shop legitimately receives a real webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends a POST to the app's webhook endpoint with the same body `B` and same HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body successfully.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` — matches, since body `B` is unchanged: [5](#0-4) 
6. Handler is invoked with `shop: "victim-shop.myshopify.com"` even though the payload never actually originated from Shopify for that shop, because `shop` is never part of the signed bytes.

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
