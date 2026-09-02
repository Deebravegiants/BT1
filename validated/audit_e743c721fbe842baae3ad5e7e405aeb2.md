### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant impersonation via header replay/spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the `shop` value that identifies which tenant the webhook belongs to is taken from an HTTP header that is completely outside the HMAC's signable content. This breaks the intended binding: `hmac-signed bytes == authenticated tenant`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` returns only the raw HTTP body: [1](#0-0) 

Meanwhile, `shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only checks the HMAC computed over `to_signable_string` (i.e., the raw body) against the `hmac` header: [3](#0-2) 

`Registry.process` then trusts the unauthenticated `request.shop` value and hands it straight to the host application's handler as the tenant identifier, without any additional check that the shop matches the one the body/HMAC was actually generated for: [4](#0-3) 

Because the header is excluded from the signed bytes, the equality the gem is supposed to enforce — `shop used for tenant routing == shop the HMAC was computed for` — does not hold. Any request whose body+HMAC pair is valid (e.g., a legitimately received webhook for shop A, or any other request an attacker can get validly HMAC'd through the same secret/body relationship) can have its `shopify-shop-domain` header rewritten to shop B, and `Registry.process` will still accept it and dispatch `WebhookMetadata` with `shop: "B"` to the app's handler, while the body content actually belongs to shop A.

### Impact Explanation
This is a cross-tenant identity-binding break: the "bytes verified" (raw body) are not the same as the "bytes acted on" (the shop header used for tenant routing/data association). A host application that uses `WebhookMetadata#shop` from `Registry.process` to determine which merchant's records to update, delete, or process (which is the documented purpose of this field) can be made to associate one tenant's payload with another tenant's identifier, since the gem itself performs no binding between the two. This falls under cross-tenant access, one of the qualifying "Critical" impacts.

### Likelihood Explanation
Exploitation requires the attacker to be able to replay/relay a previously-observed, validly-signed webhook body (or otherwise obtain one HMAC-body pair) while controlling the HTTP headers sent to the app's webhook endpoint — a capability available to an unprivileged actor sitting between the webhook sender and the app's public HTTP endpoint (or one who can trigger delivery and then replay it), since nothing in the gem constrains the header to the signed payload. No possession of `api_secret_key` or any privileged credential is required to perform the header substitution itself — only a legitimately delivered/observed webhook body+HMAC pair is needed, and the substitution step does not require re-signing anything.

### Recommendation
Include the shop-domain header (and ideally topic/api-version) in the value that is HMAC-verified, or otherwise cryptographically bind `shop` to the signed body before it is exposed via `Registry.process`/`WebhookMetadata`. At minimum, the gem should document and/or enforce that host applications cannot rely on `request.shop` as authenticated unless bound to the signature, or the gem should reject/flag any mismatch between the header-derived shop and other verifiable session/registration data known for that webhook subscription.

### Proof of Concept
1. App registers a webhook handler for topic `orders/create` via `Webhooks::Registry.add_registration`.
2. Shopify (or an attacker with network position between Shopify and the app, or one able to replay a captured request) sends a POST to the app's webhook endpoint with:
   - `raw_body`: an untouched, previously observed valid webhook body for shop `victim.myshopify.com` together with its original `x-shopify-hmac-sha256` value (this pair is unmodified, so the HMAC check in `HmacValidator.validate_signature` at [5](#0-4)  passes).
   - `x-shopify-shop-domain`: rewritten to `attacker-shop.myshopify.com` (or any other tenant of the same app).
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully (all required headers present), and `Registry.process(request)` at [4](#0-3)  passes the HMAC check and invokes the handler with `shop: "attacker-shop.myshopify.com"` while `body` still contains `victim.myshopify.com`'s order data.
4. Any host application logic keyed on `WebhookMetadata#shop` (e.g., "look up merchant record for this shop and store body") now cross-associates victim data with the attacker's tenant record.

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
