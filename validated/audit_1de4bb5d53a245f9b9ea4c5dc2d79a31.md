### Title
Webhook `shop` domain is trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then hands the `shop` value taken from an unauthenticated header straight to the app's handler as the tenant identifier. This is the same bug class as CVE-2022-27778 (curl acting on a filename/identifier that was not the one it actually verified): the byte range verified (`raw_body`) is not the same as the identity field acted upon (`shop-domain` header).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read from a separate, unauthenticated header (`shopify-shop-domain` / `x-shopify-shop-domain`) that is not part of that signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, and then forwards `request.shop` — the unauthenticated header — to the app-provided handler as the tenant identity, without any cross-check that this shop is the one the body actually pertains to: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirms only that the `secret` (the app's `client_secret`) produced the `hmac` over `to_signable_string` (i.e., the body) — it says nothing about which shop sent it: [4](#0-3) 

The documented contract of this gem explicitly tells integrators to trust `data.shop` as the shop identity for the webhook payload: [5](#0-4) 

Equality that should hold but doesn't: `shop bound by HMAC == shop acted upon by handler`. In reality, `shop covered by HMAC = ∅` (the signable string is body-only) while `shop acted upon by handler = request.shop` (an arbitrary attacker-controlled header). Any unprivileged internet user who can install the app on their own shop receives legitimately-signed webhooks (valid `hmac-sha256` over a given body, signed with the app's real `client_secret`). Because the header is not part of the signed bytes, that same `(body, hmac)` pair remains valid if replayed to the app's webhook endpoint with the `shop-domain` header changed to a different (victim) shop.

### Impact Explanation
This breaks the tenant/shop identity binding at the point the gem hands control back to the host application: an attacker who has a working install (any unprivileged Shopify merchant can install a public app) can produce a validly-HMAC'd payload for their own store, then replay it with a forged `shop-domain` header claiming to belong to a different shop. `ShopifyAPI::Webhooks::Registry.process` will accept the HMAC (since it only checks the body) and pass the forged shop to the handler as authentic. Depending on how the host app uses `data.shop` (e.g., session/tenant lookup, per-shop data writes), this can lead to cross-tenant data confusion/corruption — writing or associating one merchant's data under another merchant's identity.

### Likelihood Explanation
Moderate-to-high for apps that trust `data.shop` as a tenant key (which is exactly what the documentation recommends). It only requires: (1) an unprivileged install of the target app on an attacker-controlled shop to obtain one valid `(body, hmac)` pair, and (2) direct HTTP requests to the app's public webhook endpoint with a substituted `shop-domain` header — no access to `api_secret_key`, tokens, or any privileged account is required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically/contextually bind the `shop-domain` header to the verified body before it is exposed to handlers — e.g., verify that the webhook's registered `webhook_id`/subscription is actually associated with the claimed shop via a server-side lookup, rather than trusting the header value from the request that was replayable independent of the signed body.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` (an ordinary, unprivileged action available to anyone).
2. Shopify sends a webhook to the app with body `B` and headers including `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's real `client_secret`) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the exact same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged header, `Utils::HmacValidator.validate` returns `true` (it only checks `B` against `H`), and `Registry.process` calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the host app to process attacker-controlled data as though it originated from `victim-shop.myshopify.com`. [3](#0-2)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
