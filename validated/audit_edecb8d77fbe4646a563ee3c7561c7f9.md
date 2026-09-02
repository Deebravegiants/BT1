### Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the webhook HMAC only over the raw request body, but the `shop` (tenant) identity used to route and label the webhook data is taken from an unsigned HTTP header. This breaks the binding: `shop_used_for_tenant_identification == shop_covered_by_HMAC`. An attacker who legitimately installs the app on their own shop can capture a genuinely-signed webhook (valid HMAC over the body) and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header changed to a victim shop, while the HMAC still validates.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read directly from the (unauthenticated) header, independent of that signed string: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (i.e., the body) against the computed HMAC, then immediately trusts `request.shop` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute the HMAC purely from `verifiable_query.to_signable_string`, so any header not included in that string — including `shop` — is never bound by the signature check: [4](#0-3) 

This exactly mirrors the reported bug class: a value (`shop`) is *acted upon* (used as the tenant identity passed to the handler) but is *not covered* by the cryptographic check (HMAC over body only) — analogous to the chainlink adaptor consuming a feed whose freshness wasn't actually bound by the check being performed.

### Impact Explanation
Because `shop` is not part of the signed payload, any actor who can obtain one valid `(body, hmac)` pair — trivially achievable by installing the app on their own (attacker-controlled) shop and letting Shopify send a real webhook — can replay that exact body/HMAC to the app's webhook endpoint while substituting the `shop-domain` header for an arbitrary victim shop domain. The HMAC check passes (body unchanged), and the handler receives `WebhookMetadata` claiming the data belongs to the victim shop. Any app logic that uses `data.shop` to select/update tenant-scoped records (a common, encouraged pattern, since `WebhookMetadata.shop` is the field the gem provides specifically for this purpose) can be tricked into applying attacker-controlled webhook content under a victim tenant's identity — i.e., cross-tenant data manipulation.

### Likelihood Explanation
Likelihood is high for any app that trusts `WebhookMetadata#shop` for tenant routing (the intended use of that field), since exploitation requires no credentials, no access token, and no knowledge of `api_secret_key` — only the ability to install the app once on an attacker-owned store to harvest one genuine signed webhook body/HMAC pair, then issue crafted HTTP requests with a spoofed header to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and other identity-relevant fields such as topic/webhook-id) in the HMAC-covered signable string, or otherwise cryptographically bind them (e.g., verify `shop` against a shop known from an authenticated session/registration rather than trusting the header), so that the shop-domain header cannot be altered independently of a valid signature.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a normal, unprivileged action).
2. Shopify sends a real webhook to the app: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` and replays it directly to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` recomputes HMAC over `B` only (see `to_signable_string`) — it matches `H`, so validation succeeds.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` and dispatches it to the app's handler, which processes attacker-controlled data as if it originated from `victim-shop.myshopify.com`. [3](#0-2)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
