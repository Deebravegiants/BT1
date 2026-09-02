### Title
Webhook `shop-domain` header trusted for tenant routing without HMAC coverage - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the HMAC-signable content solely from the raw request body, while the `shop` (and `topic`) values used to route and label the webhook payload are read from unauthenticated HTTP headers. This breaks the binding: "bytes verified" (the raw body) versus "bytes/identity acted on" (the `shop-domain` header used as the tenant key when the handler is invoked).

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from HTTP headers with no relation to the HMAC computation: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., only the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately constructs `WebhookMetadata` using `request.shop` (the unauthenticated header) as the tenant identifier passed to the app's handler: [4](#0-3) 

Because the `shop-domain` header is never included in the HMAC-signed material, an entity that has ever obtained one legitimate `(raw_body, hmac)` pair for a topic they can trigger (e.g., a developer with a test store where the app is installed, or anyone able to capture one delivery) can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header value. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to a different, victim shop domain.

### Impact Explanation
This satisfies the "field acted on but not covered by the HMAC" analog class explicitly called out in scope: the `shop` field is used by the app's webhook handler as the tenant/session key for storage or processing decisions, yet it is excluded from the cryptographic binding that the gem provides via `HmacValidator`. Any app that relies on `WebhookMetadata#shop` (as documented/intended usage of `Registry.process`) for per-tenant persistence or logic can have data attributed to, or processed for, the wrong shop — a cross-tenant integrity break driven purely by unauthenticated header replay, without needing the app's `client_secret` or access token.

### Likelihood Explanation
Likelihood is bounded by the need for the attacker to first obtain one valid `(raw_body, hmac)` pair, which normally requires being a legitimate merchant/developer on some shop where the target app is installed and able to trigger a webhook (e.g., `orders/create`, `customers/create`) — an unprivileged-but-authenticated-as-a-different-tenant scenario, not requiring the app's secret. Given the low bar (any shop that can install the app), likelihood is meaningful though not universal.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) header values in the HMAC-signable string, or otherwise cryptographically bind the tenant identity to the signed payload, so `HmacValidator.validate` fails if the shop header is altered relative to the originally signed delivery. At minimum, document that `WebhookMetadata#shop` is not authenticated and must not be trusted as a tenant key without additional verification (e.g., cross-checking against a known/allow-listed shop list per registered webhook).

### Proof of Concept
1. App registers a webhook handler for `orders/create` via `ShopifyAPI::Webhooks::Registry`.
2. Attacker (a merchant with the app installed on `attacker-shop.myshopify.com`) triggers an `orders/create` event and captures the legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
3. Attacker replays a POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, since only `B` is hashed: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the app to process/store attacker-controlled order data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
