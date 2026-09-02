## Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only, while the `shop` value used for tenant attribution is read from an HTTP header that is never included in the signed bytes. Any attacker who obtains one valid `(body, hmac)` pair for the app's shared secret can replay it while substituting an arbitrary `shop-domain` header, and `Registry.process` will accept it as authentic for that spoofed shop.

### Finding Description
`Request#hmac` decodes the signature and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is populated purely from the `x-shopify-shop-domain`/`shopify-shop-domain` header, with no relationship to the signed bytes: [2](#0-1) 

`Registry.process` validates only that the HMAC matches the body, then immediately forwards `request.shop` (the unauthenticated header value) to the handler for tenant-scoped processing: [3](#0-2) 

The `HmacValidator` confirms this: it signs/verifies exactly `verifiable_query.to_signable_string` (the raw body for webhooks) against `Context.api_secret_key`, which is a single secret shared across every shop that has installed the app - it is not shop-specific: [4](#0-3) 

The equality the code implicitly assumes is:
`shop used by the handler (request.shop, from an unauthenticated header) == shop that produced the HMAC-signed body`

But nothing enforces that equality. Because `api_secret_key` is shared across all shops of the same app, an attacker who is a legitimate merchant of the app (or otherwise obtains one valid webhook body+HMAC, e.g. by installing the app on their own store and capturing a webhook), can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while setting `x-shopify-shop-domain` to a victim shop's domain. `HmacValidator.validate` will still return `true` (it only checks the body against the shared secret), and the handler will receive `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This breaks the tenant boundary the host application relies on: any app that uses `WebhookMetadata#shop` to select which merchant's session/data to update (a documented, expected usage pattern of this field) can be tricked into attributing attacker-controlled webhook data to a different, victim tenant. This satisfies the "cross-tenant access" Critical impact criterion, since the vulnerability lets one tenant's webhook traffic be mistaken for another tenant's traffic purely through this gem's verification logic.

### Likelihood Explanation
Likelihood is Low-to-Medium: exploitation requires the attacker to already control (or observe) at least one legitimately-signed webhook body from the same app (e.g., by installing the multi-tenant app on their own shop, which any user can do), then replay it against the shared endpoint with a forged shop header naming a different, victim shop.

### Recommendation
Bind the `shop` field to the signed payload, or otherwise verify it against a value not controlled by the sender:
- Include the shop-domain header value in the bytes/string that is HMAC-verified (mirroring how `AuthQuery#to_signable_string` binds `shop` into its signed string), or
- Cross-check `request.shop` against the shop associated with the session/access token used to originally register the specific webhook subscription, rejecting any mismatch before invoking the handler.

### Proof of Concept
1. App merchant "attacker.myshopify.com" installs the app; Shopify delivers a legitimate webhook with `x-shopify-hmac-sha256: H` computed over `raw_body: B` using the shared `api_secret_key`.
2. Attacker captures `(B, H)` and replays a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` using the shared secret: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, achieving cross-tenant spoofing.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
