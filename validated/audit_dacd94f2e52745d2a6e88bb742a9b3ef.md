### Title
Webhook shop identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` header verbatim as the tenant identity passed to the host application's handler. Because the HMAC signable string is only the raw body, the `shop`, `topic`, and `webhook-id` headers are never covered by the signature, so a valid `(body, hmac)` pair can be replayed with an arbitrary `shop-domain` header and still pass validation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor simply reads the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (the body) and compares it against the `hmac` field, with no reference to the shop or any other header: [3](#0-2) 

`Registry.process` performs exactly that HMAC check and then forwards `request.shop` straight into `WebhookMetadata` for the application handler, with no additional binding between the verified body and the claimed shop: [4](#0-3) 

This breaks the intended identity equality: `shop authenticated by HMAC == shop delivered to handler`. In reality the equation is `shop authenticated by HMAC (over body only) != shop header (unauthenticated, attacker-suppliable)`. Any party capable of sending an HTTP request to the app's webhook endpoint with a previously-observed, genuinely-signed `(body, hmac)` pair — e.g., the operator of one shop that has installed the app and therefore legitimately receives real webhook deliveries for their own store — can resend that exact body/HMAC pair while substituting a different `shop-domain` header. `Registry.process` will accept it (HMAC still matches, since it only covers the body) and deliver it to the handler tagged with the attacker-chosen shop, i.e., a different merchant's tenant identity.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem hands the host application webhook data that is verified-authentic-content but falsely-attributed-tenant. A host application (following this gem's documented API, using `WebhookMetadata#shop` to select which merchant's records the payload applies to) will process attacker-controlled shop attribution as if Shopify itself vouched for it, since the only cryptographic guarantee (HMAC) never covered that field. This enables cross-tenant data confusion/injection under the identity of a shop the attacker does not control, satisfying the "cross-tenant access" criteria.

### Likelihood Explanation
Any merchant/developer who has legitimately installed the app (an "unprivileged internet user" relative to other tenants of the same app) automatically receives real webhook deliveries with valid `(body, hmac)` pairs for their own topics. Capturing and replaying one such pair with a modified `shop-domain` header requires no knowledge of `api_secret_key` and no privileged access — only the ability to send an HTTP POST to the app's public webhook endpoint, which is by design internet-reachable.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signable string / verification, or otherwise cryptographically bind the shop identity to the HMAC-verified payload before it is trusted as tenant identity. At minimum, `Registry.process` should not treat `request.shop` as fully authenticated by `HmacValidator.validate`; the gem should document this gap clearly, or require the host to cross-check `request.shop` against an out-of-band verified source (e.g., session lookup) rather than relying on the header alone.

### Proof of Concept
1. Shop A (attacker-controlled, has installed the app) receives a genuine webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `api_secret_key`), `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker resends the identical request to the app's webhook endpoint, only changing `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` (unchanged) and matches `H`, so validation passes: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-influenced body `B`, even though Shopify never sent this webhook for that shop.

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
