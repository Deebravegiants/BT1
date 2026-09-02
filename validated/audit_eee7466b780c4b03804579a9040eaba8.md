### Title
Webhook `shop` identity is unauthenticated (not covered by the HMAC signature), enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from an HTTP header that is never included in the HMAC-signed payload, while `ShopifyAPI::Webhooks::Registry.process` only validates the HMAC before handing that unauthenticated `shop` value straight to the app's handler. This breaks the identity binding `hmac-authenticated sender shop == shop passed to handler`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) 

But `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which plays no part in that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string` (i.e., the body) using the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` performs exactly one check — HMAC validity — and then immediately trusts `request.shop` to build the `WebhookMetadata` object dispatched to the app's registered handler: [4](#0-3) 

Because the `api_secret_key` is a single value shared by the app across *every* shop that has installed it (not a per-shop secret), the equality that should hold — `shop encoded in the signed bytes == shop delivered to the handler` — never actually exists: `shop` is not signed at all. Any of the app's own merchants (an "unprivileged internet user" from the perspective of other tenants) can capture a legitimately-signed `(raw_body, hmac)` pair sent to their own store's webhook endpoint (e.g. from browser dev tools, a proxy, or their own server logs) and replay it to the same endpoint with the `X-Shopify-Shop-Domain` header rewritten to name a different, victim shop. The HMAC still validates because it only covers the untouched body, so `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: request.shop, ...)` carrying the attacker-controlled shop value: [5](#0-4) .

### Impact Explanation
This is a cross-tenant identity-binding break: an app built on this gem cannot distinguish "the payload/signature genuinely originated for shop X" from "any shop's valid payload replayed while claiming to be shop X," because the gem's own `shop` accessor is presented as part of the "verified" webhook request without ever being covered by the signature it verifies. Any handler logic that keys off `data.shop` (session lookup, per-tenant data writes, billing/plan updates, deletion flows for GDPR/mandatory webhooks, etc.) can be tricked into operating on a shop other than the one that actually sent the payload — a cross-tenant access primitive.

### Likelihood Explanation
Any merchant who has installed the app can trivially capture one legitimate `(body, hmac)` pair delivered to their own shop and replay it with a forged shop-domain header; no access to `api_secret_key`, tokens, or Shopify infrastructure is required. This is fully reachable through the gem's own public API (`Webhooks::Request.new` + `Registry.process`), not by an app ignoring documented gem contracts.

### Recommendation
- Do not expose `shop` as an implicitly-trusted field of a "validated" `Request`; document explicitly that the HMAC only guarantees body integrity/authenticity, not header authenticity.
- Bind `shop` into the authenticated context, e.g., require callers to independently verify `shop` against a known/installed shop record (session store) before trusting it, or have `Registry.process` require an explicit, out-of-band verified shop rather than trusting the header value uncritically.
- At minimum, require that consuming apps treat `WebhookMetadata#shop` as unauthenticated input unless cross-checked against stored session/shop data before performing any tenant-scoped action.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com`: headers include `X-Shopify-Hmac-Sha256: <hmac-of-body>` and `X-Shopify-Shop-Domain: shop-a.myshopify.com`, with some JSON body `B`.
2. Attacker (owner/admin of `shop-a`, having legitimately received this webhook) resends the exact same body `B` and the exact same `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com` (a victim shop also using the same app).
3. `Webhooks::Request.new` parses this into a `Request` with `shop == "shop-b.myshopify.com"` while `to_signable_string == B`, unchanged.
4. `HmacValidator.validate` recomputes HMAC over `B` using the app's single `api_secret_key` and it matches — validation succeeds.
5. `Registry.process` dispatches to the app's handler with `WebhookMetadata.new(topic:, shop: "shop-b.myshopify.com", body: parsed(B), ...)`, even though `shop-b` never sent this webhook, achieving cross-tenant data/action confusion.

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
