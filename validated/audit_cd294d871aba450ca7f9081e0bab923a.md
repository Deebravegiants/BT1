Based on my analysis, I've confirmed the identity binding gap in the webhook processing path.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw HTTP body [1](#0-0) , using `Request#to_signable_string`, which returns only `@raw_body` [2](#0-1) . The `shop` value that is subsequently trusted as the tenant identity for the webhook [3](#0-2)  and handed to the application handler as `WebhookMetadata.new(... shop: request.shop ...)` [4](#0-3)  comes from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header and is never included in the HMAC-signed material.

### Finding Description
`HmacValidator.validate` recomputes an HMAC-SHA256 over `verifiable_query.to_signable_string` with the app's `api_secret_key` and compares it to the `hmac` header using `OpenSSL.secure_compare` [5](#0-4) . For webhook requests, `to_signable_string` is defined to be exactly `@raw_body` — it does not incorporate `topic`, `shop-domain`, `webhook-id`, or `api-version` [6](#0-5) .

Because Shopify signs webhooks with the app's single, global `api_secret_key` shared across **every** shop that installs the app (not a per-shop secret), any merchant who installs the app receives real webhooks with a validly-computed HMAC for arbitrary bodies. That attacker-controlled-but-genuinely-signed `(raw_body, hmac)` pair can then be replayed against the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to name a victim shop. `HmacValidator.validate` will still succeed, since it never checks the `shop` header, and `Registry.process` will invoke the registered handler with `WebhookMetadata#shop` set to the forged victim domain [7](#0-6) .

This is the exact identity-binding gap described in the report class: **a field acted on (`shop`) but not covered by the HMAC**. The equality that should hold — `hmac_signed_scope == identity_used_for_tenant_dispatch` — is broken: the HMAC binds only `(secret, raw_body)`, while tenant dispatch is keyed on the unauthenticated `shop-domain` header.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce. Applications built on this gem virtually always use `WebhookMetadata#shop` to decide which merchant's records to create/update/delete (e.g., `orders/create`, `products/update`, `app/uninstalled`, GDPR `shop/redact`/`customers/redact` topics registered via `MANDATORY_TOPICS` [8](#0-7) ). An attacker who is any legitimate (even free/dev) install of the app can forge webhook deliveries attributed to a different, victim shop, causing cross-tenant data corruption, spurious deletion/redaction against the wrong tenant, or fake "app/uninstalled" events that make the app tear down a victim's stored session/access token. This satisfies the "cross-tenant access" Critical impact category, since it lets one tenant's authenticated (but not tenant-bound) message be replayed as if it belonged to another tenant.

### Likelihood Explanation
Likelihood is high for any app that has at least one other unrelated legitimate install (trivially achievable by installing the app on the attacker's own free development store), since:
1. No `api_secret_key`, access token, or leaked credential is required — only a normal install of the target app.
2. Shopify's own webhook delivery to the attacker's shop is enough to obtain a validly-signed `(body, hmac)` pair.
3. Replaying the HTTP request with a modified `shop-domain` header is trivial and entirely within the unprivileged internet-user threat model (no TLS interception, no social engineering).

### Recommendation
Bind the shop identity into the authenticated material, or otherwise cryptographically link the `shop-domain` header to the signed payload/session before dispatch:
- Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in `Request#to_signable_string` so the HMAC covers them, or
- Require applications/`Registry.process` to cross-check `request.shop` against a previously stored, trusted shop record (e.g., verifying an existing session/installation record for that shop before trusting the webhook), and document this as a mandatory step rather than leaving it implicit.
- At minimum, update `docs/usage/webhooks.md` (out of scope for code fix but relevant) to explicitly warn implementers that `shop` is not authenticated by the HMAC and must not be trusted for tenant-scoped writes without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, and triggers a webhook (e.g. updates a product to fire `products/update`).
2. Shopify delivers a POST to the app's webhook endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(api_secret_key, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures this raw request, then re-sends it directly to the app's webhook endpoint, keeping `B` and the `hmac` header unchanged but replacing the header value with `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes over `request.to_signable_string == B` [2](#0-1)  — validation succeeds.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)` [4](#0-3) , causing the app to process attacker-supplied data as if it originated from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L196-200)
```ruby
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
