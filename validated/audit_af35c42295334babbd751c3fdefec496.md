### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross‑tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body bytes, never the `shop-domain` header. `Utils::HmacValidator.validate` therefore only proves "these bytes were HMAC'd with the app's shared `api_secret_key`" — it proves nothing about which shop the request claims to be from. `Registry.process` still trusts `request.shop` (read straight from the unauthenticated header) and hands it to the app's webhook handler as the tenant identifier.

### Finding Description
`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding: [1](#0-0) 

The signable string used for HMAC verification is only the raw body: [2](#0-1) 

`HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it to the `hmac` header — the `shop` header plays no role in the check: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately forwards the unauthenticated `request.shop` value to the handler as the tenant identity: [4](#0-3) 

Crucially, `api_secret_key` (the app's `client_secret`) is a single value shared by **every** shop that has the app installed — it is not per-shop. So the equality the gem's HMAC check is actually supposed to guarantee is:
`HMAC(secret, body) == received_hmac` ⟺ "this body was produced by Shopify for *some* shop that has this app installed."

But the code (and the app built on top of it) treats a passing check as if it also proved:
`request.shop == the shop that actually generated this body`

These two are not equivalent, because `shop` travels in a header that is outside the signed material. A merchant who has legitimately installed the app on their own shop will receive real webhook deliveries with valid HMACs (computed with the shared secret over their own body). They can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` (the body/HMAC pair is untouched and valid), and `Registry.process` builds `WebhookMetadata.new(shop: request.shop, body: request.parsed_body, ...)` with the attacker-controlled `shop` field, silently mislabeling the attacker's own webhook payload as belonging to another tenant.

### Impact Explanation
Any host application built on this gem that keys per-tenant behavior off `WebhookMetadata#shop` (e.g., looking up the tenant's access token, updating tenant records, billing state, or entitlements by `shop`) can be made to process attacker-supplied data under another merchant's identity. This is a cross-tenant boundary break: the binding "HMAC valid ⇒ shop field trustworthy" that the gem's API implicitly offers to consumers does not hold, because `shop` is never part of the signed payload.

### Likelihood Explanation
Exploitation only requires being an ordinary merchant who has installed the target app (no special privileges, no access to `api_secret_key` or any merchant's access token) — they use their own genuine webhook deliveries (which they can trigger themselves, e.g. via `orders/create` on their own store) and simply modify one header before forwarding it to the app's public webhook endpoint.

### Recommendation
Bind the shop identity into the verified material: either include the `shop-domain` header in `to_signable_string`, or, upstream, have `Registry.process` cross-check `request.shop` against a shop that is independently known to be authorized (e.g., a shop the app has an active, previously-established session/install record for) rather than trusting the header value as-is once the body HMAC passes.

### Proof of Concept
1. App merchant A installs the target Shopify app; the app registers a webhook (e.g., `orders/create`) that its host calls into `ShopifyAPI::Webhooks::Registry.process`.
2. Shopify delivers a genuine webhook to the app for shop A: body `B`, header `x-shopify-shop-domain: shop-a.myshopify.com`, header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Merchant A (attacker) captures this request and resends it to the same endpoint, changing only the header to `x-shopify-shop-domain: shop-victim.myshopify.com`, keeping body `B` and the HMAC header unchanged.
4. `Utils::HmacValidator.validate` in `hmac_validator.rb` recomputes `HMAC(secret, B)` (the body wasn't touched) and it matches — validation passes.
5. `Registry.process` builds `WebhookMetadata.new(shop: "shop-victim.myshopify.com", body: parsed(B), ...)` and calls the registered handler, which now processes attacker-controlled data attributed to `shop-victim`.

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
