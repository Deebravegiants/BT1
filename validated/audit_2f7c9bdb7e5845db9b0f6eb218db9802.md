### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Utils::HmacValidator` verify only the raw request body against the HMAC signature. The `shop-domain` header — which the registry uses as the tenant identity for dispatching webhook data to the host application's handler — is never included in the signed material. This breaks the binding: `shop` used == `shop` authenticated.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `hmac` reads the `hmac-sha256` header: [1](#0-0) [2](#0-1) 

`HmacValidator.validate` computes the signature over `to_signable_string` (the body only) and compares it to the received HMAC — it never incorporates `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` then trusts `request.shop` (taken straight from the unauthenticated header) as the tenant identity passed into the handler: [4](#0-3) [5](#0-4) 

Because the signature covers only the body, an unprivileged actor who owns/controls their own Shopify store can capture a legitimate, validly-signed webhook delivery for their own shop (body + hmac unchanged), then replay the exact same HTTP POST to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header value with an arbitrary victim shop domain. `HmacValidator.validate` still succeeds because the signed bytes (the body) are untouched, yet `WebhookMetadata.shop` — the field the host app uses to look up/act on tenant data — now reports the attacker-chosen shop. This is exactly the "field acted on but not covered by the HMAC" identity-binding break called out in the report's bug class: `shop` is trusted as an authenticated tenant identifier but was never part of the verified bytes.

### Impact Explanation
This enables cross-tenant data injection: an attacker who is a legitimate (if unprivileged) user of the platform (i.e., owns any shop that can install the app and receive webhooks) can forge webhook events "from" any other shop domain, without needing the app's `client_secret` or any victim credentials. Depending on how the host application's `WebhookHandler#handle` implementation uses `data.shop` (e.g., to update records, trigger side effects, or grant/revoke entitlements for that shop), this can lead to cross-tenant state corruption. This matches the "cross-tenant access" Critical impact category since the tenant boundary (`shop`) is not authenticated.

### Likelihood Explanation
Moderate-to-high: webhook endpoints are typically public HTTP endpoints (necessarily, since Shopify calls them), so no privileged network position is required. The attacker needs only to control one legitimate shop to obtain one validly-signed body/hmac pair, then can vary the `shop-domain` header value freely on replay because it is never checked against the signature. No secrets or victim access are required.

### Recommendation
Include the shop domain (and ideally topic and webhook_id) in the HMAC-signed material, or otherwise cryptographically bind the delivered `shop-domain` header to the signed payload before it is trusted as the tenant key in `WebhookMetadata`. At minimum, document/enforce that host applications must independently verify `shop` against a known-registered shop before acting on webhook data, since the header is currently unauthenticated relative to the HMAC check performed by this gem.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` and has the app installed; Shopify delivers a legitimate webhook to the app's endpoint with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of body B>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - body `B`
2. Attacker captures this raw HTTP request (own traffic, no interception needed).
3. Attacker resends the identical request to the same app endpoint, only changing `x-shopify-shop-domain` to `victim-shop.myshopify.com`, keeping body `B` and the HMAC header unchanged.
4. `ShopifyAPI::Webhooks::Request.new` parses the headers/body; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches (per `to_signable_string` returning `@raw_body`), so `Registry.process` proceeds: [6](#0-5) 
5. The host app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload/signature were generated for the attacker's own shop, and acts on it as if it were a genuine event for the victim tenant.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
