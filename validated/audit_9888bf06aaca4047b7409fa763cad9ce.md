Analog identified in `lib/shopify_api/webhooks/`. The webhook verification binds the HMAC to the request body only, while the tenant-identifying `shop` (and `topic`) come from unauthenticated HTTP headers that the HMAC never covers — this is exactly the "field acted on but not covered by the HMAC" class from the report, applied to a real identity boundary (shop/tenant) instead of RaptorCast chunk counts.

### Title
Webhook shop/topic attribution is not covered by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the *body bytes* but not the `shop-domain` or `topic` headers. `Registry.process` nonetheless forwards `request.shop` and `request.topic`, taken verbatim from headers, into `WebhookMetadata` used by the app's handler as the tenant identity.

### Finding Description
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field via `OpenSSL.secure_compare` [1](#0-0) . For webhooks, `to_signable_string` returns `@raw_body` exclusively [2](#0-1) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the signature [3](#0-2) .

`Registry.process` validates only the HMAC and then dispatches using the unverified `request.shop`/`request.topic` fields as the tenant/topic identity for the handler: [4](#0-3) .

The broken identity equality is:
`HMAC-verified(raw_body)` ≠ `shop attributed to handler (request.shop, from header)`

Because a single app's `api_secret_key` is shared across every shop that installs the app, an unprivileged actor who controls (or has installed) their own shop instance of the same app can trigger genuine webhooks against their own tenant, capture a valid `(raw_body, hmac)` pair, and replay it directly to the app's public webhook endpoint with a forged `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at a different, victim shop. `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` will hand the attacker-controlled body to the handler labeled as belonging to the victim shop.

### Impact Explanation
This breaks the tenant boundary that host applications rely on this gem to enforce: the `shop` value produced by `Webhooks::Registry`/`Webhooks::Request` is meant to reliably identify which merchant a webhook payload belongs to. Since it is not bound to the HMAC, an attacker can inject data attributed to another tenant (cross-tenant access), which is explicitly listed as Critical impact in scope.

### Likelihood Explanation
Any developer/user who can install the target app on their own store (a normal, unprivileged action) can generate a legitimately-signed webhook body/HMAC pair at will, then replay it with a modified `shop-domain` header to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is required — only knowledge of the app's public webhook URL, which is not treated as secret.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, and ideally `webhook_id`) in the signable content used for HMAC verification, or otherwise cryptographically bind `request.shop`/`request.topic` to the verified payload before they are passed to `WebhookMetadata` in `Registry.process`. At minimum, document that host applications must not trust `shop`/`topic` from `WebhookMetadata` unless they independently cross-check it against the shop record associated with the specific `webhook_id`/subscription.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store (`attacker.myshopify.com`).
2. Attacker triggers a real event (e.g., updates a product) causing Shopify to send a genuine webhook to the app's endpoint, signed with the app's shared `api_secret_key`; attacker captures `raw_body` and the `x-shopify-hmac-sha256` value from their own delivery (e.g., via a request-logging proxy they control).
3. Attacker replays the exact same `raw_body` and `hmac` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/webhooks/request.rb`/`hmac_validator.rb` succeeds (body unchanged), and `Registry.process` invokes the handler with `shop: "victim.myshopify.com"` [4](#0-3) , causing the host app to process attacker-controlled data as if it originated from the victim tenant.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
