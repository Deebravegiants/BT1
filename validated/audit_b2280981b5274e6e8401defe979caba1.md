### Title
Webhook `shop` (and `topic`) identity is not covered by the HMAC signature, enabling cross-tenant impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC over the raw request body only, while the `shop` (and `topic`) identity that downstream handlers rely on is read from an HTTP header that is never included in the signed content. An attacker who legitimately receives one valid `(body, hmac)` pair (e.g., by installing the target app on their own store) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the library will accept it as valid and hand the attacker-chosen `shop` value to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` reads the shop identity purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed string: [2](#0-1) 

`HmacValidator.validate` verifies only that `hmac == HMAC(secret, to_signable_string)`: [3](#0-2) 

`Registry.process` performs exactly this check and then forwards `request.shop` (the unauthenticated header) into `WebhookMetadata`, which is the value host applications use to identify which merchant/tenant the payload belongs to: [4](#0-3) 

This breaks the intended identity binding:
`HMAC(secret, body) == received_hmac` is verified, but the equality that actually matters for tenant isolation — `shop_header == shop_that_signed_this_body` — is never checked. Because `shop` (and `topic`) live outside the signable string, any bytes can be substituted there without invalidating the signature.

### Impact Explanation
This is a cross-tenant identity confusion: an app that stores/updates per-shop records keyed off `WebhookMetadata#shop` will process attacker-supplied header values as if they came from Shopify for that shop, while the actual signed content (`body`) may originate from a completely different (attacker-controlled) shop's legitimate webhook delivery. This satisfies the "Critical - cross-tenant access" impact bucket, since it lets an unprivileged actor make the app associate arbitrary payload data with a victim shop's identity.

### Likelihood Explanation
Medium-to-High: no privileged credentials or `api_secret_key` are required. Any internet user can install the target app on their own free/dev store (this is the normal, unprivileged app-installation flow), which causes Shopify to deliver legitimately HMAC-signed webhooks to the app's public endpoint. The attacker fully controls the raw HTTP request they replay to that public endpoint, including all headers, and can freely rewrite `shop-domain` (and `topic`) while preserving the valid `(body, hmac)` pair from their own store's webhook.

### Recommendation
Include the `shop` (and `topic`) values in the material that is HMAC-verified — e.g., require the caller to supply the expected shop/topic out-of-band (from the URL route or session) and compare it against the header value, or extend Shopify's verification contract in this gem to require that the shop domain be corroborated against a source that is itself authenticated (such as validating it against a known list of active installed shops with a matching offline session) before trusting `WebhookMetadata#shop`. At minimum, document prominently that `Request#shop`/`Request#topic` are unauthenticated header values and must not be used as the sole tenant-identity input without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on a store `attacker.myshopify.com` they control (fully unprivileged action).
2. Shopify sends a legitimate webhook to the app's public endpoint with a valid body `B` and header `x-shopify-hmac-sha256: H` (where `H = HMAC(secret, B)`) and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures this request and replays it to the same public endpoint, keeping `B` and `H` identical but changing the header to `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this still passes because `B` and `H` are unchanged: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-originated body `B`, even though Shopify never actually signed anything for `victim.myshopify.com`.

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
