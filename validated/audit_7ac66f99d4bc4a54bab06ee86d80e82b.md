### Title
Webhook shop-domain identity spoofing via HMAC that only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature exclusively over the raw request body, while the `shop` (tenant) identifier is taken from an unsigned header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then dispatches the webhook payload to the app's handler using this unverified `shop` value, allowing the tenant identity delivered to the handler to diverge from the tenant whose body/HMAC pair was actually authenticated.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
and `hmac` is derived purely from the `hmac-sha256` header, decoded/hex-encoded, with no binding to `shop`, `topic`, or `webhook-id`: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `HMAC(api_secret_key, to_signable_string)`, i.e. against the body alone: [3](#0-2) 

`Registry.process` only checks this body-bound HMAC, then immediately trusts `request.shop` (read straight from the `shop-domain` header) to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

Because `api_secret_key` is a single value shared across every shop that has the app installed (it is not per-shop), any tenant that legitimately receives one genuine webhook (body + valid HMAC) from Shopify can replay that exact `(raw_body, hmac-sha256)` pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header. `HmacValidator.validate` still succeeds because the header it never inspects (`shop-domain`) is not part of the signed material — breaking the identity binding: `shop authenticated by HMAC == shop delivered to handler` does not hold. The equality that should hold, `hmac-verified-tenant == request.shop passed downstream`, is violated because `to_signable_string` binds only the body, not the tenant.

### Impact Explanation
Applications built on this gem generally use `WebhookMetadata#shop` (or `request.shop`) as the tenant key to look up sessions, update per-merchant data, or trigger merchant-scoped side effects (e.g. `app/uninstalled`, `shop/update`, `customers/data_request`). An attacker who controls one shop with the app installed can forge a cross-tenant webhook delivery for any other shop that also uses the same app instance, since the HMAC does not bind the claimed shop. This is a cross-tenant access primitive: the attacker injects attacker-chosen (but HMAC-valid) payloads that the host app will process as belonging to a victim tenant.

### Likelihood Explanation
Exploitation requires only that the attacker be able to install the app on at least one shop (which for public apps is available to any unprivileged internet user) and be able to send an arbitrary HTTP POST to the app's public webhook endpoint with headers of their choosing — both are ordinary capabilities for an attacker with no special privileges beyond running their own shop instance.

### Recommendation
Bind the identifying request attributes (`shop`, `topic`, `webhook-id`) into the signable content used for HMAC verification, or additionally verify that `shop` in the payload/headers matches an expected/allow-listed shop for the resource before dispatching to handlers, rather than trusting the unsigned `shop-domain` header as-is.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Shopify sends a genuine webhook (e.g., `orders/create`) to the app for that shop; attacker captures the raw body `B` and the resulting `x-shopify-hmac-sha256` header value `H` (this pair is valid because `H = HMAC(api_secret_key, B)`, independent of shop).
3. Attacker crafts their own POST to the app's public webhook endpoint reusing body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this passes: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the host app to process attacker-controlled data as if it originated from the victim shop.

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
