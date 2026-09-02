### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the merchant identity (`shop`) that it passes downstream to app handlers from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that this gem validates only covers the raw request body, never the header. This breaks the identity binding: `shop_authenticated_by_hmac == shop_used_for_tenant_routing`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop` is read directly, and unauthenticated, from the `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` validates only the HMAC over the body via `Utils::HmacValidator.validate(request)`, then immediately forwards `request.shop` (the unauthenticated header) to the app's webhook handler as the tenant identifier: [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the HMAC purely from `verifiable_query.to_signable_string`, i.e., the body only — it never incorporates `shop`, `topic`, `webhook_id`, or `api_version`: [4](#0-3) 

Because the HMAC is keyed only to body bytes, a party that possesses one legitimately-signed webhook body/HMAC pair for their own shop (e.g., any merchant who has the app installed — a party the app should treat as "unprivileged" relative to *other* tenants' data) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop domain. `HmacValidator.validate` still returns `true` because the signature check never looks at the header, so `Registry.process` accepts the request and calls the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain. This is precisely the "field acted on but not covered by the HMAC" pattern: the equality that should hold — `shop bound inside the HMAC-verified payload == shop the app acts on` — does not exist in this library at all.

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` (as documented/intended) to decide which tenant's records to update, delete, or query is exposed to cross-tenant data corruption or disclosure: an attacker who controls one legitimate install can trigger writes/actions attributed to an arbitrary victim shop merely by replaying a body they already legitimately received, with a forged `Shop-Domain` header. This matches the Critical-tier "cross-tenant access" impact category, since the identity boundary between tenants is what's broken, and the gem itself provides no mechanism (documented or otherwise) to bind the shop value to the signed payload.

### Likelihood Explanation
Likelihood is high for any app that trusts `request.shop`/`WebhookMetadata.shop` for tenant routing, which is the designed and documented usage of this API. No secrets are required — replaying one's own previously-received legitimate webhook body with a modified header is trivial for a merchant who has the app installed, and no server-side interaction with Shopify's real webhook delivery infrastructure is needed since the gem's `process` method accepts any HTTP request bearing a valid HMAC over the body regardless of transport origin.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-covered signable payload, or independently verify that the `shop`/`X-Shopify-Shop-Domain` header matches a shop value embedded in the verified body (many webhook payloads already carry the shop's admin GraphQL ID or domain in their JSON). At minimum, document prominently that `request.shop` is not authenticated by the HMAC and must not be used as the sole tenant-routing key without additional verification (e.g., cross-checking against a locally stored, previously-authenticated shop record/session).

### Proof of Concept
1. App installs on `attacker.myshopify.com` and receives a legitimate webhook: raw body `B`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`, and a valid `X-Shopify-Hmac-Sha256` computed over `B` with the app's `client_secret`.
2. Attacker resends the identical HTTP request to the app's webhook endpoint, keeping body `B` and the HMAC header unchanged, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` — [5](#0-4)  — which recomputes the HMAC only from `@raw_body` — [1](#0-0)  — and succeeds because `B` is unchanged.
4. `WebhookMetadata.new(..., shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` — [6](#0-5)  — and delivered to the app's handler, which acts on the victim tenant using attacker-controlled body content.

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
