### Title
Webhook `shop` (and other identity) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from only the raw request body, while the shop-identifying header (`x-shopify-shop-domain`) is read separately and never covered by the signature. Any attacker who can obtain one genuinely-signed webhook (e.g., by installing the app on their own store) can replay that valid `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shop` header, and `Registry.process` will accept it and dispatch it as if it belonged to the victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from an unauthenticated header, independent of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `to_signable_string` (i.e., the body), never against the `shop`, `topic`, `webhook-id`, or `api-version` headers: [3](#0-2) 

`Registry.process` gates purely on this body HMAC and then forwards `request.shop` (the unauthenticated header) to the host application's handler as the tenant identifier: [4](#0-3) 

This is the exact bug class described in the report: a field that is *acted upon* (the `shop` used to attribute/route the webhook to a tenant) is not *covered by the integrity check* (the HMAC only binds the body). The equality the code implicitly assumes — `authenticated_shop == attributed_shop` — is broken because the HMAC never binds `shop` to the body.

Because Shopify apps share a single `client_secret`/`api_secret_key` across all shops that install them, a genuinely-signed `(body, hmac)` pair obtained from a webhook delivered for shop A (which any attacker can obtain by installing the app on their own development/test store) remains valid when replayed with the `shop` header rewritten to shop B. `HmacValidator.validate` will still pass because it never inspects `shop`.

### Impact Explanation
This breaks tenant isolation for any host application built on this gem's documented `ShopifyAPI::Webhooks::Registry.process` / `WebhookMetadata` API: it enables cross-tenant webhook injection — an attacker-controlled webhook body (e.g., `orders/create`, `customers/create`, `app/uninstalled`) can be attributed to an arbitrary victim shop while still passing this gem's authenticity check. Depending on the host app's webhook handlers (which trust `WebhookMetadata#shop` as the tenant key, exactly as the library's own docs/tests demonstrate), this can be leveraged for cross-tenant data injection or state corruption (e.g., forging an `app/uninstalled` event for a victim shop to trigger token/session invalidation, or injecting fabricated order/customer records attributed to a shop the attacker does not control). This matches the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on any shop the attacker controls (a normal, permission-less action for any developer or public-app user), to obtain one real signed webhook body+HMAC pair, and (2) sending an HTTP request to the app's webhook endpoint with that body/HMAC but an attacker-chosen `x-shopify-shop-domain` header. No access to `api_secret_key`, access tokens, or the victim's credentials is needed — only the gem's own signature-verification logic is used against it.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed payload verification, or otherwise cryptographically bind the shop attribution to the signed body (e.g., by validating that the `shop` header is consistent with information embedded in and covered by the signed body/claims), rather than trusting an out-of-band, unauthenticated header for tenant attribution.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, and Shopify delivers a legitimate webhook, e.g. `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC over raw body, computed with the app's shared api_secret_key>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-topic: orders/create`
2. Attacker captures the raw body and HMAC value, then sends their own POST request to the app's webhook endpoint reusing the identical raw body and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers/body without error (see initializer at `lib/shopify_api/webhooks/request.rb:45-63`), and `Utils::HmacValidator.validate(request)` returns `true` because it only checks the body-derived signable string against the HMAC — the forged `shop` header is never validated (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` therefore accepts the request and calls the host app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` (`lib/shopify_api/webhooks/registry.rb:189-199`), even though the body content originated entirely from the attacker's own shop, achieving cross-tenant webhook spoofing.

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
