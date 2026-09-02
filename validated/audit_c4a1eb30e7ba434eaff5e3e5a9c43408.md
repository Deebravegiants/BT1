Confirmed. The `Webhooks::Request#shop` value (`shop-domain` header) is not included in `to_signable_string` (only `@raw_body` is HMAC-signed), yet `Registry.process` trusts `request.shop` to attribute the webhook to a tenant without it being cryptographically bound to the signature.

### Title
Webhook `shop-domain` header is not covered by HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The library's webhook signature verification only signs the raw request body, never the `shop-domain` header that `Registry.process` and app handlers use to attribute the webhook to a specific merchant/tenant. This mirrors the "field acted on but not covered by the integrity check" bug class from the external report: the value trusted to establish tenant identity (`shop`) is disjoint from the value actually authenticated (the raw body).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`request.shop` is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `to_signable_string` (the body) and compares it against the `hmac` field, never incorporating `shop`: [3](#0-2) 

`Registry.process` accepts the request once `HmacValidator.validate` passes, then dispatches to the handler using the unauthenticated `request.shop` value as the tenant identity for the callback: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every merchant that installs the app, and only the body is bound to the signature, any body+HMAC pair legitimately generated for one shop (e.g., an attacker's own store using the same app) remains a valid signature no matter what `shop-domain` header accompanies it. An attacker can therefore capture a genuine webhook delivery for their own store, replay the identical body/HMAC to the app's webhook endpoint while substituting the victim's `shop-domain` header, and the host application will process it as authentic data belonging to the victim tenant, breaking the `authenticated shop == tenant the app acts on behalf of` binding.

### Impact Explanation
This breaks the tenant identity binding (`request.shop` used by the handler == the shop whose secret actually produced the signature`) without requiring any credential from the victim. A host application that keys session lookups, order processing, or data mutation off `WebhookMetadata#shop` can be made to act on an attacker-supplied body under a victim shop's identity — a cross-tenant access/data-integrity violation, matching the "Critical: cross-tenant access" impact category.

### Likelihood Explanation
Any user who can install the target app on their own store (public apps, development stores) can trivially trigger a legitimate webhook for a body of their choosing (e.g., by creating an order with attacker-controlled fields), capture the valid raw body + `hmac-sha256` header from that delivery, and replay it to the app's webhook endpoint with a forged `shop-domain`/`x-shopify-shop-domain` header. No secrets, tokens, or elevated access are required — only standard merchant-level access to install/use the app.

### Recommendation
Bind the shop identity into the material that is authenticated, or otherwise cryptographically tie the `shop-domain` header to the signed payload before trusting it (e.g., verify the `shop-domain` header value against a shop that is known to be associated with the specific HMAC/webhook delivery via Shopify's webhook metadata, or require host applications to cross-check `request.shop` against an independently retrieved/authorized session for that shop before acting on webhook contents). At minimum, document that `request.shop` must not be trusted for authorization decisions without additional verification (e.g., confirming an existing installed session for that shop) — however, this gap exists in the gem's `HmacValidator`/`Webhooks::Request`/`Registry.process` implementation itself, so a defensive fix here would raise the security floor for all consumers of the gem.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store (or use any legitimate app install).
2. Trigger a real webhook delivery (e.g., `orders/create`) so Shopify sends a POST with `raw_body` and a valid `x-shopify-hmac-sha256` computed with the app's shared `client_secret`.
3. Capture the exact `raw_body` and `hmac-sha256` header from that delivery.
4. Replay the identical body and `hmac-sha256` header to the app's webhook endpoint, but set `x-shopify-shop-domain` to the victim's `*.myshopify.com` domain.
5. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the HMAC — it never checks `shop`, as shown in [5](#0-4) .
6. `Registry.process` invokes the registered handler with `WebhookMetadata.new(..., shop: request.shop, ...)` where `request.shop` is the attacker-forged victim domain, causing the host application to process attacker-controlled data as if it originated from the victim shop.

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
