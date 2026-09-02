### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` checks is computed only over the raw request body. The `shop` field that is later trusted and passed to the application's webhook handler is therefore never bound to the cryptographic signature that authenticates the request.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `#hmac` reads the `hmac-sha256` header: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC strictly against `to_signable_string`, i.e. the body only: [3](#0-2) 

`Registry.process` accepts any request whose HMAC (over the body) matches, then builds `WebhookMetadata` using `request.shop`, taken straight from the unauthenticated header, and dispatches it to the app's handler as the tenant identity: [4](#0-3) 

This reproduces the exact bug class from the report: two logically-linked values (here, "the bytes verified by the HMAC" and "the `shop` value acted upon by the handler") are expected to correspond to the same authenticated source, but only one of them is actually covered by the cryptographic check. The equality that should hold is:
`bytes_covered_by_hmac == bytes_the_application_trusts_as_tenant_identity`
but in this gem it is actually:
`bytes_covered_by_hmac = {raw_body}` while `tenant_identity_trusted = header["shop-domain"]`, and the two are disjoint.

Because Shopify signs webhooks with the single app-level `api_secret_key` shared across every shop that has installed the app (it is not a per-shop secret), any merchant who installs the app receives legitimately-signed webhooks for their own shop. That merchant (an "unprivileged" party relative to any other tenant of the same app) can capture one such valid `(body, hmac)` pair from their own store and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. The signature still validates because it never covered the shop header, and the handler receives `WebhookMetadata` attributing the (attacker-controlled) body to the victim shop.

### Impact Explanation
This is a cross-tenant attribution/spoofing vulnerability: an app that keys any state, side effects, or data lookups off `WebhookMetadata#shop` (e.g., updating that shop's local records, triggering GDPR/compliance actions, inventory/order changes, etc., as intended by the `topic`/`body`) can be made to apply attacker-influenced webhook data under another tenant's identity. This satisfies the "Critical - cross-tenant access" category defined in scope, since the trust boundary between tenants (shops) sharing the same app is broken using only a webhook the attacker's own shop legitimately received — no access token, `client_secret`, or privileged credential is required.

### Likelihood Explanation
Likelihood is high for any app relying on this gem's webhook signature verification as the sole authentication mechanism (as documented/intended usage): any merchant who installs the app can become the attacker, and the attack requires nothing beyond triggering a webhook to their own store and replaying it with a modified header — no secret material, social engineering, or privileged access needed.

### Recommendation
Include the tenant-identifying header (`shop-domain`, and ideally `topic`/`api-version`) in the signed payload used for HMAC verification, e.g. by having `to_signable_string` bind the raw body together with a canonical representation of `shop`, or by validating that a shop obtained independently (e.g., a stored per-shop webhook secret, or comparing against a previously registered/authenticated shop for that endpoint) matches `request.shop` before dispatching to the handler. Document clearly that host applications must not trust `WebhookMetadata#shop` as authenticated unless such a binding is added.

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` and subscribes to a webhook topic (e.g. `orders/create`).
2. Shopify sends a legitimately HMAC-signed webhook to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid signature over raw body>`, and some JSON body.
3. Attacker captures this exact `(raw_body, hmac_header)` pair.
4. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged header into `shop`, `Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) body against the (unchanged) valid signature: [5](#0-4) 
6. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop = "victim-shop.myshopify.com"` and invokes the app's handler, causing the app to act as if the (attacker-controlled) webhook body came from the victim tenant: [6](#0-5) [7](#0-6)

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
