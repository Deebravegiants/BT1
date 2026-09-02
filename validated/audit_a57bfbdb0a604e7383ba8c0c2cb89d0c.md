### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (tenant) identifier is read from a separate, unsigned HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates only the body's HMAC and then trusts the header-derived `shop` value for tenant attribution, breaking the binding `signed_bytes == (body, shop)` down to `signed_bytes == body`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over the body only) and then immediately hands the header-derived `shop` to the app's webhook handler as the tenant identifier, with no cross-check that the signed body is actually associated with that shop: [3](#0-2) 

`HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (the raw body) against the computed signature — it never incorporates `shop`: [4](#0-3) 

Because every shop installed on the same app shares the same `api_secret_key` (there is no per-shop signing key visible to this gem), any entity that has ever observed one valid `(raw_body, hmac)` pair for the app — for example, its own shop's legitimately delivered webhook — can replay that exact body/HMAC pair while substituting a different `shop-domain` header. `HmacValidator.validate` will still return `true` because the signature check never inspects the header, and `Registry.process` will pass the attacker-chosen `shop` value straight to the handler as if it originated from that shop.

This is the same identity-binding class as the Sherlock report's core issue (a value acted upon that isn't actually verified/covered by the check protecting it) mapped onto this gem's webhook trust boundary: the field acted on (`shop`) is not covered by the cryptographic check (HMAC over `raw_body`).

### Impact Explanation
A host application that keys its data store, authorization decisions, or side effects (e.g., disabling a shop, deleting data, updating billing state) off `WebhookMetadata#shop` as returned by this gem can be tricked into applying another tenant's webhook payload under an attacker-chosen shop domain, or vice versa — an attacker-controlled shop's payload being attributed to a victim shop. This is a cross-tenant integrity issue: the gem asserts a trust guarantee ("if `Registry.process` doesn't raise, the body and shop both came from Shopify for that shop") that the code does not actually provide.

### Likelihood Explanation
Exploitation requires the attacker to have obtained at least one legitimately signed `(raw_body, hmac)` pair for the same app (trivial if the attacker runs their own store installed on the same app, which is the normal unprivileged-merchant scenario), and to be able to submit an HTTP request with the same body/HMAC headers but a modified `shop-domain` header directly to the app's webhook endpoint (bypassing the normal delivery path, which any internet client can do since the endpoint is just an HTTP route). No access token, `client_secret`, or other privileged credential is needed.

### Recommendation
Include the `shop` header (and other tenant-identifying headers such as `webhook_id`/`api_version` if they influence behaviour) in the HMAC-covered signable string, or have `HmacValidator`/`Registry.process` independently verify that the `shop` used for the handler matches metadata embedded in the verified body/payload rather than trusting the unsigned header alone.

### Proof of Concept
1. App installs on `victim-shop.myshopify.com` and `attacker-shop.myshopify.com`, both under the same app (same `api_secret_key`).
2. Attacker's own shop receives (or triggers, e.g. via an action in their own admin) a legitimate webhook delivery, capturing `raw_body` and the valid `x-shopify-hmac-sha256` header Shopify computed for it.
3. Attacker crafts a request to the app's webhook endpoint reusing the captured `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the HMAC — it passes. [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker's payload>, ...)`, and the host app processes attacker-controlled data under the victim shop's identity.

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
