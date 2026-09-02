### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop spoofing on replayed webhooks - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from only the raw request body, while the `shop` identity attribute used downstream is read from an unsigned HTTP header. This breaks the binding: `HMAC(raw_body) == valid` should imply `shop-domain header == the shop that produced raw_body`, but the gem never enforces that equality.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which plays no part in the signed content: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC against the body only, then forwards `request.shop` unchecked to the handler as the authoritative tenant identity: [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it only to the received HMAC — it has no visibility into, and does not bind, the `shop` header at all: [4](#0-3) 

Because the app's `client_secret` is shared across all shops that install the app (it is a single per-app secret, not per-shop), any legitimate merchant using the app receives genuine, validly-signed webhooks for their own shop. Since the `shop-domain` header is excluded from the signed bytes, that merchant can replay the exact same `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds (the body/HMAC pair is untouched), and `Registry.process` calls the handler with `shop: <victim-domain>` even though the body content actually originated from the attacker's own shop.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the authenticated bytes (`raw_body`) are not bound to the shop identity (`shop-domain` header) that the rest of the pipeline trusts and forwards to the host application via `WebhookMetadata`. Any host application that keys per-tenant records off `WebhookMetadata#shop` (the documented/intended usage) can have another tenant's genuine webhook payload attributed and applied to a different, arbitrary shop record — a cross-tenant data-integrity/isolation violation, matching the "cross-tenant access" impact class.

### Likelihood Explanation
Any user who has installed the target app on their own Shopify store already receives real, validly-HMAC-signed webhooks from Shopify for that store — no credential leakage or privileged access is required beyond being an ordinary merchant/tenant of the app. Replaying the request to the app's public webhook endpoint with a modified `shop-domain` header is a trivial HTTP-level manipulation.

### Recommendation
Include the shop identity in the HMAC-signed content, or otherwise cryptographically bind the `shop-domain` header to the payload before trusting it (e.g., require the host app to cross-check `request.shop` against an independently known/registered domain, or extend `to_signable_string` to incorporate the shop header so the HMAC computation, and thus `HmacValidator.validate`, fails whenever the shop header is altered relative to the originally signed request).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Shopify sends a genuine webhook, e.g. `customers/create`, to the app's webhook endpoint with headers:
   - `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body>`
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - body: `{"id": ..., "email": "attacker@example.com", ...}`
3. Attacker intercepts/replays this exact request to the app's webhook endpoint, changing only the `X-Shopify-Shop-Domain` header to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the tampered headers; `HmacValidator.validate(request)` succeeds because `to_signable_string` only covers `raw_body`, which is unchanged. [5](#0-4) 
5. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, causing the host app to process/attribute attacker data as belonging to the victim tenant. [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
