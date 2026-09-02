### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted from unauthenticated headers not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` and passed into `WebhookMetadata` are read directly from HTTP headers that are never part of the signed payload. Any party able to produce one validly-signed webhook body for the shared app `client_secret` (e.g., a malicious merchant who has installed the app and receives their own genuine webhooks) can replay that body with forged `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers, and the signature check will still pass.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — i.e., only the raw body bytes are cryptographically bound to the signature: [2](#0-1) 

However, `Request#shop`, `#topic`, and `#webhook_id` are all parsed straight from headers with no binding to the HMAC: [3](#0-2) 

`Registry.process` uses `Utils::HmacValidator.validate(request)` purely as a gate, then dispatches the handler using the unverified `request.topic` and constructs `WebhookMetadata` directly from the unverified `request.shop`, `request.webhook_id`, and `request.api_version`: [4](#0-3) 

`WebhookMetadata` is the struct handed to the host application's `WebhookHandler#handle`, and its `shop` field is what downstream app code will use to identify the tenant whose data the webhook body applies to: [5](#0-4) 

The identity binding that should hold is: `hmac == HMAC(secret, shop ‖ topic ‖ webhook_id ‖ body)`, so that the shop/topic/id the app acts on are cryptographically tied to the signature. Instead the gem enforces only `hmac == HMAC(secret, body)`, leaving `shop`, `topic`, and `webhook_id` — the very fields used to route and attribute the webhook to a tenant — completely unauthenticated. This is exactly the "field acted on but not covered by the HMAC" class described in the report's bug family (an update to state driven by inputs excluded from the integrity check).

### Impact Explanation
Because the app `client_secret` (the HMAC key) is shared by all shops that install the app, any shop that installs the app can obtain a validly HMAC-signed webhook body (from its own genuine webhook deliveries) and then replay that exact body to the app's webhook endpoint while substituting the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers to any values it chooses. `HmacValidator.validate` will still return `true` because it only checks the body bytes, and the app's `WebhookHandler#handle` will receive a `WebhookMetadata` claiming to be from an arbitrary victim shop/topic/webhook-id. If the host application (following this gem's documented `WebhookMetadata.shop` contract) uses that field to select which tenant's records to create/update/delete, this results in cross-tenant data corruption/injection — data intended for shop A can be attributed to and processed as shop B. This satisfies the "cross-tenant access" Critical impact category, since the boundary crossed is the per-shop identity binding the gem is expected to guarantee via HMAC verification.

### Likelihood Explanation
Any developer/merchant who can install the app on one shop (a normal, unprivileged action, not requiring `api_secret_key`, access tokens, or leaked credentials) automatically receives a legitimately-signed webhook body for that shop, satisfying the entire prerequisite. No secret material needs to be obtained — only the ability to install the app and intercept/replay its own inbound HTTP webhook request with modified headers, which is trivial for anyone controlling the receiving endpoint's network path or replaying a captured request via a simple HTTP tool.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the signable string (or otherwise cryptographically bind them, e.g., by hashing them alongside the body before HMAC verification), so `HmacValidator.validate` fails if any of these fields are altered independently of the body. At minimum, document prominently that `WebhookMetadata.shop`/`topic`/`webhook_id` are NOT covered by the HMAC and must not be trusted for tenant attribution without additional verification (e.g., cross-checking against a known/allow-listed shop domain looked up via the session store).

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com`, and Shopify delivers a genuine webhook with body `B` and headers including `x-shopify-hmac-sha256: H(secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-webhook-id: X`.
2. Attacker resends the exact same body `B` and hmac header `H(secret, B)` to the app's webhook endpoint, but rewrites `x-shopify-shop-domain: victim.myshopify.com` and/or `x-shopify-webhook-id`/`x-shopify-topic`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` (`request.rb:35-38`) and succeeds because `B` is unchanged.
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built using the attacker-forged `shop` value (`registry.rb:198-199`) and passed to the host app's handler, which believes the webhook body legitimately originates from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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
