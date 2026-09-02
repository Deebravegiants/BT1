### Title
Webhook shop/topic identity not covered by HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` to dispatch and attribute the event are read from unauthenticated HTTP headers that are never part of the HMAC computation. This breaks the identity binding `hmac_verified_content == fields_acted_on`, letting an attacker who can obtain a genuinely-signed webhook body (e.g. by installing the app on their own shop) replay it with a forged `shop-domain`/`topic` header and have the library accept it as valid for a different tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are pulled straight from HTTP headers with no cryptographic binding to the HMAC at all: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (the body only, for this type) and compares it with `OpenSSL.secure_compare`: [4](#0-3) 

Because the HMAC never covers `shop-domain`, `topic`, or `webhook-id`, any request whose body+HMAC pair is genuinely valid (obtained, for instance, from an app's own legitimate webhook delivery for the attacker's own shop) can be replayed to the same shared webhook endpoint with a different `shop-domain`/`topic` header. The gem will report the HMAC as valid and hand the handler a `WebhookMetadata` that misattributes the verified body to an attacker-chosen shop/topic — breaking the equality `shop bound by HMAC == shop trusted by handler`.

### Impact Explanation
This is a cross-tenant identity confusion: the only cryptographically-verified fact is "this body was HMAC-signed with the app secret," but the library reports it as belonging to whatever `shop-domain`/`topic` header the request carries. A multi-tenant app relying on `WebhookMetadata#shop` (as returned by this library) to route data or authorize side effects per-tenant can be made to apply a legitimately-signed body to another merchant's tenant context, i.e. cross-tenant access without any credential of the target tenant. This matches the Critical "cross-tenant access" impact category defined in scope.

### Likelihood Explanation
Exploitation requires no possession of `api_secret_key`, no TLS interception, and no privileged account: an unprivileged internet user only needs to be able to install the target app on any shop (a normal Shopify merchant action) to receive at least one genuinely HMAC-valid webhook delivery, then replay that raw body to the app's public webhook endpoint with a spoofed `shop-domain`/`topic` header. The webhook endpoint is, by design, a public HTTP(S) endpoint, so this replay is trivially reachable.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them to the verified body, e.g. by having `to_signable_string` incorporate the header values), and have `Registry.process` reject requests where these header-derived values are not verifiably associated with the signed content. At minimum, document that consuming applications must independently re-validate `shop` (e.g. against the shop that owns the currently active session/subscription) before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Install the vulnerable app on `attacker-shop.myshopify.com`; capture a genuine webhook delivery, e.g.
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id":1,...}
   ```
2. Replay the identical body and `x-shopify-hmac-sha256` value, but change the header:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `@raw_body` against the HMAC — validation succeeds. [3](#0-2) 
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` for a body that was never actually generated for `victim-shop`, demonstrating the broken binding.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
