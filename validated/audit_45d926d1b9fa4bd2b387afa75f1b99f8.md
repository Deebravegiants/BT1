### Title
Webhook HMAC verification does not bind the `shop-domain` header, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable representation from the raw request body only. The `shop-domain` (tenant identity), `topic`, `api-version`, and `webhook-id` headers are never included in the signed material, yet `shop` is trusted downstream as the tenant key passed to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an HTTP header with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the received HMAC against `verifiable_query.to_signable_string` — i.e., body bytes only: [3](#0-2) 

`Registry.process` gates only on this body-only HMAC check, then forwards the *unauthenticated* `request.shop` value straight into the handler as the tenant identifier: [4](#0-3) 

The equality actually being enforced is:
`HMAC(raw_body, api_secret_key) == received_hmac`

but the value host applications rely on to select/scope a merchant's data is `shop`, which is **not** part of that equality. Any two requests with identical bodies but different `shop-domain` headers produce the same valid signature.

### Impact Explanation
Any merchant who installs the app (an "unprivileged internet user" relative to other tenants of the same app) legitimately receives Shopify-signed webhooks for their own store — i.e., a genuine `(raw_body, hmac)` pair signed with the app's `api_secret_key`. Because `shop` is outside the signed material, that same attacker can resend the identical body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `Registry.process` will accept the request as valid (HMAC still matches the unchanged body) and hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop: [5](#0-4) 

Any host application that uses `data.shop` from `WebhookMetadata` to select which tenant's records to create/update/delete (the standard multi-tenant pattern) will process attacker-controlled webhook content under another merchant's tenant scope — a cross-tenant data injection/impersonation, which maps to the report's identity-binding-break pattern ("shop authenticated versus the shop trusted downstream").

### Likelihood Explanation
Any developer/merchant who can install the app on a store they control can obtain a validly signed body/HMAC pair for arbitrary webhook content of their choosing (e.g., by editing a resource that triggers a webhook topic they control, like a product or order update with attacker-chosen field values), then replay it against the shared webhook endpoint with a forged `shop-domain` header. No possession of `api_secret_key`, access tokens, or privileged access is required — only the ability to install the app as a normal merchant and send an HTTP request to the app's public webhook endpoint, which is inherently internet-reachable.

### Recommendation
Bind the tenant identity into the verified material: include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in `to_signable_string`, or independently verify that the `shop-domain` header matches an authenticated relationship (e.g., cross-checking against Shopify's mandatory webhook headers using a canonical signed string that Shopify itself supports) before trusting `request.shop` as the tenant key. At minimum, document to host applications that `shop` on `WebhookMetadata` is unauthenticated and must not be used as a sole tenant-scoping key without additional verification (e.g., confirming an active session/installation exists for that shop before trusting the payload).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic (e.g., `products/update`) with a payload of their choosing.
2. Shopify delivers `POST /webhooks` with body `B` and header `x-shopify-hmac-sha256: HMAC(B, api_secret_key)`; the shop header is `attacker-shop.myshopify.com`.
3. Attacker replays the exact same request to the app's public webhook endpoint but changes only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only — this still matches, since the body is unchanged: [6](#0-5) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, and any host app logic keyed on `data.shop` mutates/creates data under the victim tenant.

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
