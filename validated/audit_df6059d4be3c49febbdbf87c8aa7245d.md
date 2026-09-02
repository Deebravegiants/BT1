### Title
Webhook `shop-domain`/`topic`/`webhook-id` headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers and forwarded unchanged to the application's webhook handler. Any actor able to send a request with a previously-valid `(body, hmac)` pair — trivially obtainable by any merchant who has the app installed on their own shop — can swap the `shop-domain` header to a victim shop and have `ShopifyAPI::Webhooks::Registry.process` treat attacker-controlled data as though it originated from the victim tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (which validates the body against `Context.api_secret_key`) before trusting `request.shop`, `request.topic`, and `request.webhook_id` and handing them to the registered handler: [3](#0-2) 

`HmacValidator.validate` itself only ever validates `verifiable_query.hmac` against `verifiable_query.to_signable_string`, i.e. exactly the fields the caller decided to sign — for webhooks that's the body alone: [4](#0-3) 

Because the webhook secret (`Context.api_secret_key`) is the same app-level `client_secret` shared across every shop that installs the app (not a per-shop secret), a merchant on shop A receives entirely legitimate webhook deliveries carrying a valid `(body, hmac)` pair signed with that shared secret. Nothing stops that merchant from replaying the same body/hmac to the app's webhook endpoint with the `shop-domain` header changed to shop B. `HmacValidator.validate` still returns `true` because the body is unmodified, yet `WebhookMetadata.new(topic:, shop: request.shop, ...)` will carry shop B's identity into the handler: [5](#0-4) 

This breaks the intended identity binding: `hmac_valid(body) == true` is treated as equivalent to `shop_header == shop_that_actually_sent_this_webhook`, but the header is never covered by the signature.

### Impact Explanation
This is a cross-tenant access primitive: a low-privilege actor (any merchant who installs the app) can make the app process arbitrary attacker-chosen webhook payloads under an arbitrary victim shop's identity, since `shop` is the exact key host apps use to scope all subsequent business logic and data storage for a webhook (per the gem's own documented usage, `data.shop` is the tenant-scoping value the handler is meant to trust). This can lead to data being written into another merchant's account, corruption of unrelated tenants' state, or triggering privileged per-shop actions (e.g., product/order sync) against a shop the attacker doesn't own — matching the Critical "cross-tenant access" bucket.

### Likelihood Explanation
Likelihood is high: the attacker only needs to install the app on any shop (a standard, unprivileged onboarding flow) to receive genuine `(body, hmac)` pairs, and forging the remaining headers when POSTing to the app's public webhook endpoint requires no secret knowledge, since none of `shop-domain`, `topic`, `webhook-id`, or `api-version` are bound by the signature.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signed content, or otherwise cryptographically bind them (e.g., verify `shop` independently against a trusted per-install record) before dispatching to handlers. At minimum, document that `HmacValidator` for webhooks authenticates only the request body and that consuming apps must not trust the `shop`/`topic` headers for tenant scoping without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a normal webhook (e.g. `orders/create`), capturing the delivered `raw_body` and the `x-shopify-hmac-sha256` header value (both are visible to them as the receiving endpoint owner, or logged by their own server).
2. Attacker sends a new POST to the app's public webhook endpoint with:
   - Body: identical `raw_body` captured above (so HMAC still validates via `lib/shopify_api/utils/hmac_validator.rb`)
   - Header `x-shopify-hmac-sha256`: unchanged, still valid
   - Header `x-shopify-shop-domain`: `victim-shop.myshopify.com`
   - Header `x-shopify-topic`/`x-shopify-webhook-id`: attacker's choice
3. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) validates the HMAC successfully (body untouched) and invokes the app's handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, causing the host application to process attacker data under the victim shop's tenant context.

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
