### Title
Webhook `shop` identity field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header that is never included in the bytes that `Utils::HmacValidator` authenticates. `Registry.process` accepts any request whose raw body HMAC matches, then blindly trusts the header-derived `shop` value and hands it to the app's registered handler as the tenant identifier. Because the same `api_secret_key` is used to sign every webhook for every shop that installs the app, an attacker who owns a shop that has the app installed can capture one legitimately-signed webhook body and replay it with a forged `shop-domain`/`x-shopify-shop-domain` header pointing at a victim shop, producing a request that passes HMAC validation while claiming to belong to a different tenant.

### Finding Description
`HmacValidator.validate` verifies only the bytes returned by `to_signable_string`: [1](#0-0) [1](#0-0) 

For `Request`, `to_signable_string` returns only `@raw_body`; the `shop` accessor is read straight from an unauthenticated header: [2](#0-1) 

`HmacValidator.validate` computes/compares the HMAC purely against `to_signable_string`, so the `shop` header plays no role in the cryptographic check: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed into the handler: [4](#0-3) 

Since `api_secret_key` is a single per-app secret shared across every merchant who installs the app (not a per-shop secret), any shop owner who installs the app can obtain a validly-HMAC'd webhook body for their own store, then resend that exact body with a different `shop-domain` header. `Utils::HmacValidator.validate` will accept it because the signed bytes (the body) are unchanged, while `Registry.process` will report `data.shop` as the attacker-chosen victim domain to the host application's handler.

This is exactly the "bytes verified vs. bytes parsed" identity-binding break: `verified_bytes = raw_body` while `identity_used_by_handler = header["shop-domain"]`, and the two are never bound together by the signature.

### Impact Explanation
This breaks the shop⇄session identity binding across the webhook pipeline that host applications (following this gem's documented usage in `docs/usage/webhooks.md`) rely on to route webhook data and side effects (e.g., loading the victim shop's session, updating the victim's data, or triggering shop-scoped business logic) purely from `WebhookMetadata#shop`. An attacker-controlled `shop` value flowing into per-tenant logic is a cross-tenant access primitive, since the host app is only given `ShopifyAPI` primitives (`request.shop`) as the trust anchor for "which merchant does this data belong to." This qualifies as Critical - cross-tenant access.

### Likelihood Explanation
Any internet user can install a Shopify app on a store they control (a normal customer/developer action, not requiring `api_secret_key` or a stolen credential) and thereby receive a genuinely-signed webhook. Replaying that captured request with a modified `shop-domain` header requires only sending one HTTP POST to the app's public webhook endpoint — no privileged access, no interception of TLS, no social engineering. This is directly reachable from the described "unprivileged internet user" threat model.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) header values into the signed payload verified by `HmacValidator`, or independently verify that `request.shop` corresponds to a shop for which the application holds an active, previously-established session/installation record before invoking the handler. At minimum, document and enforce that host applications must cross-check `request.shop` against their own list of installed shops before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, and the app registers an HTTP webhook (e.g., `orders/create`).
2. Attacker triggers the webhook and captures the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — this HMAC is valid because it's computed with the app's single, shared `api_secret_key` over `raw_body` only, per `Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`).
3. Attacker resends the identical body and HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the untouched `raw_body` (`lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` now equals `"victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-200`, `lib/shopify_api/webhooks/request.rb:20-23`) — the host application processes attacker-supplied data as though it originated from the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
