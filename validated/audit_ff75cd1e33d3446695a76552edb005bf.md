### Title
Webhook `shop-domain` (and `topic`) are trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the webhook HMAC over the raw body only, but the `shop-domain` header used downstream to identify the tenant is never included in the signed payload. This breaks the binding: `shop authenticated == shop the handler acts on`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` and therefore only checks the body bytes against the app's single, global `Context.api_secret_key`: [2](#0-1) [3](#0-2) 

The `shop`, `topic`, and `webhook_id` values are all pulled from HTTP headers, not from the signed body: [4](#0-3) 

`process` then builds `WebhookMetadata` using `request.shop` (the unauthenticated header) as the tenant identifier passed to the app's handler: [5](#0-4) 

Because the same `api_secret_key` is shared by the app across every installed shop, a valid `(raw_body, hmac)` pair obtained from a webhook delivered to one shop remains cryptographically valid when replayed with a different `shopify-shop-domain` header. The gem's `process` method has no mechanism to bind the HMAC to the shop the request claims to be from — it only proves "this body was signed with our app secret," not "this body came from shop X."

### Impact Explanation
This breaks the equality `shop verified by HMAC == shop acted on by the handler`. Any application that uses `WebhookMetadata#shop` from a processed webhook to select a merchant record, session, or perform a tenant-scoped action (the exact pattern this API is designed to support) can be made to act on the wrong tenant if an attacker replays a validly-signed webhook body under a different shop header. This is a cross-tenant data confusion vector: the app processes data believing it originates from shop B when the cryptographic proof only established "signed by our app secret," not "from shop B."

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimate `(raw_body, hmac)` pair — which any merchant who installs the app can generate themselves via their own shop's real webhook deliveries — and then replay it toward the app's public webhook endpoint with a modified `shopify-shop-domain` header. No access to the `api_secret_key` itself is required, only knowledge of a previously observed valid signed body (webhook endpoints are public HTTP(S) endpoints, and webhook payloads/headers are not encrypted end-to-end beyond TLS, and are visible to the receiving app's own operator/any merchant that installed the app for their own shop).

### Recommendation
Include the shop domain (and ideally topic and webhook id) inside the HMAC-signed payload verification, or otherwise cryptographically bind the header-derived `shop` value to the signed body before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document that consuming applications must independently verify that `request.shop` corresponds to a shop that has actually installed the app with a matching stored session/access token before acting on the payload, rather than trusting the header value as an authenticated tenant identifier.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) so the app's endpoint receives a legitimately-signed request:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, `x-shopify-topic: orders/create`
   - Body: `raw_body`
2. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value (both are visible to them as the request originator/receiver).
3. Attacker replays the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint but substitutes `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `raw_body` only and it matches (the shop header was never part of the signed string), so `Registry.process` in `lib/shopify_api/webhooks/registry.rb:190` accepts the request.
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim.myshopify.com"` and handed to the app's registered handler, which now processes attacker-controlled data as if it originated from the victim's shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
