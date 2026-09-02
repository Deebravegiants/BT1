### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `shop`, `topic`, `webhook-id`, and `api-version` are all read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` accepts any request whose body's HMAC matches, then trusts `request.shop` — sourced from the un-signed `x-shopify-shop-domain` header — as the tenant identity handed to the app's webhook handler. This breaks the equality that should hold: `hmac_covers(shop) == shop_used_for_tenant_binding`.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns `@raw_body` only, whereas `shop` is read from a header that is completely outside the signed material: [2](#0-1) 

`Registry.process` validates only the body's HMAC and then immediately forwards the unauthenticated `request.shop` to the app-level handler as the tenant identity: [3](#0-2) 

`Utils::HmacValidator.validate` computes/compares the signature purely against `verifiable_query.to_signable_string`, i.e. the body: [4](#0-3) 

This mirrors the H-04 root cause exactly: the value that is checked (`HMAC(body)`) is not the value that is acted upon (`shop`, used for tenant binding downstream). Because the body's HMAC is independent of the `shop` header, any (body, HMAC) pair that is valid for one shop remains a byte-for-byte valid signature no matter what `x-shopify-shop-domain` value accompanies it.

### Impact Explanation
An unprivileged actor who can install the target app on their own store (a normal, non-privileged Shopify merchant/dev-store — no `api_secret_key`, access token, or client_secret required) will receive genuine webhook deliveries containing a valid `HMAC(body)` signed with the app's real secret. That attacker can capture one such (body, hmac) pair from their own tenant and replay it to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header naming a victim shop. `Registry.process` will accept the request (the HMAC still validates because only the body is signed) and pass `shop: <victim-domain>` to the app's handler, causing the application to attribute attacker-controlled webhook data to a shop it does not control. Depending on how the host app consumes `WebhookMetadata#shop` (e.g., to route data ingestion, look up sessions, or perform per-tenant side effects), this can result in cross-tenant data confusion/corruption — a Critical-tier cross-tenant access impact.

### Likelihood Explanation
Likelihood is high for any developer/attacker who can create their own trial/dev store and install the target Shopify app — a normal, unauthenticated onboarding flow requiring no credentials belonging to the victim or the app owner. Capturing a legitimate (body, HMAC) pair from their own store's webhook deliveries and replaying it with a forged shop header is trivial once the webhook endpoint is known/public.

### Recommendation
Bind the trusted tenant identity to the signed material instead of an independent header:
- Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed payload, or
- Cross-check the header-derived `shop` against a shop value embedded in and covered by the signed body (or against the shop associated with the specific webhook subscription id looked up from Shopify), rejecting the request if they disagree.

### Proof of Concept
1. Install the app on attacker-controlled store `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the delivered `raw_body` and `x-shopify-hmac-sha256` header — this HMAC is valid because it only signs `raw_body`.
2. Replay to the app's webhook endpoint with headers:
   - `x-shopify-topic: <original topic>`
   - `x-shopify-hmac-sha256: <captured valid hmac>`
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - same `raw_body`
3. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC successfully (body unchanged) and invokes the handler with `shop: "victim-shop.myshopify.com"`, confirming the app processes attacker data as if it originated from the victim tenant.

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
