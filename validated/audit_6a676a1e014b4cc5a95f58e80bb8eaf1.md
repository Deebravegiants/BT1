### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` used to attribute an incoming webhook from the unauthenticated `x-shopify-shop-domain` HTTP header, while `Utils::HmacValidator.validate` only authenticates the raw request body. The identity binding `hmac_signed_bytes == data_used_for_tenant_attribution` is broken: the signature covers `@raw_body` only, not the shop header, so any holder of a validly-signed webhook body for their own store can relabel it as belonging to a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Request#shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signed material: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)` — which only checks `request.to_signable_string` (the raw body) against `request.hmac` — and then forwards `request.shop`, taken from the unauthenticated header, straight to the handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate_signature` confirms the signature is computed solely over `verifiable_query.to_signable_string` (the body), never over headers: [4](#0-3) 

Because HMAC-SHA256 over the body does not bind the shop domain, a valid signature for a given raw body remains valid for *any* value of the `x-shopify-shop-domain` header. An attacker does not need the app's `client_secret`: they only need one legitimately-received, validly-signed webhook payload (e.g. delivered to their own installed store) and can then resend that exact `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting a different shop's domain in the `x-shopify-shop-domain` header. `Registry.process` will accept it (HMAC checks out) and hand `WebhookMetadata` claiming an arbitrary victim shop to the host application's handler.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: the "authenticated shop" identity used by the consuming application (`WebhookMetadata#shop`) is not actually bound by the cryptographic proof. A host application that uses `data.shop` to look up/target per-merchant state (offline sessions, orders, inventory, entitlements, etc., which is the documented purpose of `WebhookMetadata`) can be made to apply an attacker-controlled shop's identity to data that was never sent for it — i.e. cross-tenant access/injection, which is exactly the identity-crossing impact class in scope (Critical - cross-tenant access).

### Likelihood Explanation
Any unprivileged actor who can install the app on their own store (or otherwise obtain one legitimately-signed webhook payload) can replay it with a different shop header at will; no secret material is required. The only inputs needed — raw body and its HMAC — are attacker-visible from their own legitimate webhook deliveries.

### Recommendation
Bind the shop identity into the verified material, e.g. include the `x-shopify-shop-domain` header (and/or `topic`, `api-version`, `webhook-id`) in `to_signable_string` before computing/verifying the digest, or independently authenticate the shop against the delivered access-token/session rather than trusting the header as-is. At minimum, the header value used for tenant attribution must not be able to vary independently of the signed payload.

### Proof of Concept
1. Install the app on attacker-owned store `attacker.myshopify.com`; capture a legitimate webhook delivery: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid HMAC of `B` with the app's real secret), header `x-shopify-shop-domain = attacker.myshopify.com`.
2. POST to the app's webhook endpoint with the same `raw_body = B` and `x-shopify-hmac-sha256 = H`, but set `x-shopify-shop-domain = victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only — this matches `H`, so validation succeeds. [3](#0-2) 
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)`, i.e. attacker-supplied content is attributed to the victim shop even though it was never signed for the victim.

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
