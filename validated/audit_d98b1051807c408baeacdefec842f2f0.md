### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely against that body. The `shop-domain` header, which `Registry.process` treats as the authoritative tenant identifier for dispatching webhook data to the app's handler, is never included in the signed material.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field of the object [1](#0-0) . For webhook requests, `to_signable_string` is defined as simply `@raw_body` [2](#0-1) , and the `shop` accessor pulls straight from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header with no cross-check against the signed payload [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant to which the webhook body belongs: `raise ... unless Utils::HmacValidator.validate(request)` followed by `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [4](#0-3) .

Because Shopify apps use a single app-wide `client_secret`/`api_secret_key` to sign webhooks for *every* installed shop (not a per-shop secret), any HMAC that validates for one shop's webhook body validates identically regardless of which shop the header claims to be from. The identity binding the code implicitly assumes is:

`hmac_valid(raw_body, api_secret_key) == true` implies `shop-domain header == originating shop of raw_body`

but the actual guarantee provided by the signature is only:

`hmac_valid(raw_body, api_secret_key) == true` implies `raw_body was signed by an app holding api_secret_key` (i.e., genuinely came from Shopify for *some* shop under this app)

The `shop` field is "a field acted on but not covered by the HMAC."

### Impact Explanation
An unprivileged actor who controls or has access to one shop installed on the app (e.g., a malicious merchant, or anyone who can trigger/observe a legitimate webhook delivery for their own shop, such as `orders/create` with attacker-controlled order content) can capture a validly-signed webhook body and headers, then replay the identical body with the `shopify-shop-domain` header changed to a victim shop that is also installed on the same app. Because the HMAC only covers `@raw_body`, the signature still validates, and `Registry.process` will pass the attacker-controlled body to the handler tagged as belonging to the victim shop. If the host application uses `WebhookMetadata#shop` to select which tenant's data/session/database row to update (a common pattern for `orders/create`, `app/uninstalled`, GDPR topics, etc.), this results in cross-tenant data corruption or disclosure — one merchant's webhook payload being processed under another merchant's identity.

This satisfies the "Critical - cross-tenant access" impact category: the identity binding between the HMAC-verified bytes and the tenant identifier is broken, letting one tenant's authenticated payload be attributed to another tenant.

### Likelihood Explanation
Likelihood is moderate-to-high for multi-tenant apps: the attacker only needs their own legitimate installation (no leaked secrets, no privileged account, no TLS interception) to obtain a validly-signed body/HMAC pair, then send a crafted HTTP request to the app's public webhook endpoint with a different `shop-domain` header. The gem itself performs no binding between the header and the signed content, so any host application that relies on `WebhookMetadata#shop` post-validation for tenant routing inherits this gap without any misuse of the gem's documented API — the vulnerable code path is entirely internal to `ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry`.

### Recommendation
Do not treat `Request#shop` as authenticated data derived independently of the HMAC. Either:
- Include the `shop-domain` (and `topic`, `webhook-id`) header values in the signed string used for verification, or
- Require the host application to independently verify that `request.shop` corresponds to a shop actually installed/known to the app (e.g., cross-check against a session store) before dispatching to handlers, and document this requirement prominently since `Registry.process` currently offers no such protection.

### Proof of Concept
1. App is installed on Shop A (attacker-controlled) and Shop B (victim), both under the same Shopify app / `api_secret_key`.
2. Shopify sends a legitimate webhook (e.g., `orders/create`) to the app for Shop A with body `B` and header `shopify-shop-domain: shop-a.myshopify.com`, correctly HMAC-signed with the app's `api_secret_key`.
3. Attacker captures this raw request (they control Shop A, so they can trivially trigger and observe it).
4. Attacker replays the exact same body `B` and HMAC header, but modifies `shopify-shop-domain` to `shop-b.myshopify.com`, and sends it to the app's webhook endpoint.
5. `ShopifyAPI::Webhooks::Registry.process`:
   - `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(raw_body, api_secret_key)`, unaffected by the header change [5](#0-4) .
   - `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, body: request.parsed_body, ...))` delivers Shop A's data tagged as Shop B [6](#0-5) .
6. The host app processes attacker-controlled data as if it belongs to the victim tenant (Shop B), achieving cross-tenant data injection/corruption.

### Citations

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
