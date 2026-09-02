### Title
Webhook shop attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the request's raw body against the `X-Shopify-Hmac-SHA256` signature, but the `shop` value used to attribute the webhook to a tenant is read from the `shopify-shop-domain` HTTP header, which is never included in the signed payload. This breaks the intended identity binding: `HMAC(secret, signed_bytes) == received_hmac` should imply `shop == tenant_the_hmac_was_generated_for`, but `signed_bytes` (`raw_body`) and `shop` (an unauthenticated header) are disjoint.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived independently, from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header, which is not part of the signed content: [2](#0-1) 

`Registry.process` verifies the HMAC against the body only, then unconditionally trusts `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version`) to build `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e., the body, with no header data mixed in: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`) is shared across all shops that install the same app, any unprivileged user who installs the app in their own shop receives genuine `(body, hmac)` pairs for webhooks the app has correctly signed. That same person can then submit an HTTP request directly to the app's webhook endpoint with the exact same body/HMAC but with the `shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` still succeeds (body unchanged), yet `Registry.process` will hand the app's business logic a `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: the gem lets an attacker present a validly-signed payload as belonging to any other merchant's `shop`, because the shop identity is never bound to the HMAC. Any application logic that keys database writes, cache invalidation, order/customer processing, or authorization decisions off `WebhookMetadata#shop` can be made to act on/for a different tenant than the one whose data was actually signed, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate but unprivileged installer of the target app on their own store (a normal, unprivileged flow), and the ability to send an HTTP POST with custom headers to the app's public webhook endpoint — no access to `api_secret_key`, access tokens, or any other party's credentials is needed.

### Recommendation
Bind the shop (and other trust-relevant fields such as topic, webhook id, api version) into the signed material, or otherwise cryptographically bind them to the verified body — e.g., include `shop` in `to_signable_string`, or independently verify the shop against another authenticated channel (mTLS, Shopify’s webhook verification with the shop already known/expected for that endpoint) instead of trusting an unauthenticated header. At minimum, document that `request.shop` is untrusted absent additional binding, and encourage/host verification of the `shopify-shop-domain` header against the shop that installed the app before dispatching the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`; Shopify sends a real webhook to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>` and some JSON body `B`.
2. Attacker captures `(B, hmac)`.
3. Attacker crafts a new POST to the same endpoint, using the identical body `B` and `X-Shopify-Hmac-Sha256: hmac`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against `hmac`: [5](#0-4) 
5. The app's registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and processes attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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
