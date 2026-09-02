## Title
Webhook shop/topic identity is not authenticated by HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC over the raw request body, but then dispatches the handler using the `shop` and `topic` values taken from HTTP headers that are **not** part of the signed content. Because the same `api_secret_key` is shared across every shop that has installed the app, a valid `(raw_body, hmac)` pair captured from any one legitimate webhook delivery (e.g., one sent to the attacker's own store) remains cryptographically valid no matter which `x-shopify-shop-domain` (or `x-shopify-topic`) header it is replayed with. This breaks the intended binding `shop authenticated == shop the handler acts on`.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the HMAC over `to_signable_string`, which for `Webhooks::Request` is simply the raw body: [1](#0-0) 

The `shop`, `topic`, `api_version` and `webhook_id` accessors are read straight from HTTP headers and are never included in `to_signable_string`: [2](#0-1) 

`Registry.process` validates only the HMAC of the request, then immediately trusts `request.shop` and `request.topic` to build the metadata handed to the application's handler: [3](#0-2) 

`HmacValidator.validate_signature` recomputes the HMAC using `Context.api_secret_key`, which is a single secret shared by the app across **all** installed shops — it is not per-shop or bound to any shop identifier: [4](#0-3) 

Because the signature only covers `@raw_body`, the (body, hmac) pair generated for a webhook delivered to Shop A remains valid when replayed with headers claiming it belongs to Shop B. The equality that should hold — `HMAC-authenticated bytes == bytes that determine which shop/topic the handler is told to act on` — does not hold, since the header-derived `shop`/`topic` are outside the HMAC's scope.

### Impact Explanation
An attacker who is a legitimate merchant with the app installed (or who otherwise obtains one valid `(raw_body, hmac)` webhook pair for any shop) can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. The HMAC check still passes because it never inspected the header. The app's webhook handler will then process attacker-controlled data as if it originated from the victim shop's store — a cross-tenant data injection into the handler logic (e.g., triggering shop-scoped side effects, cache/database writes, or business logic keyed by `shop`). This matches the Critical category "cross-tenant access."

### Likelihood Explanation
The webhook endpoint is deliberately public/unauthenticated (that is the point of the design), and merely requires the attacker to be able to capture at least one valid webhook body+HMAC combination — trivially available to any merchant using the app, since they receive their own webhooks. No access token, `client_secret`, or privileged credential is needed. Likelihood is High.

### Recommendation
Include the security-relevant header fields (`shop`, `topic`, and ideally `webhook_id`) in the HMAC-signed content used for verification, or independently validate that the shop asserted in the header matches a shop the app has an active session/installation for before dispatching to handlers. At minimum, `Registry.process` should cross-check `request.shop` against known/expected values rather than trusting it unconditionally after only body-HMAC validation.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook: raw body `B` with header `x-shopify-hmac-sha256: H` (valid per `HmacValidator.validate`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with the same body `B` and same header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` — this passes because it only validates `B` against `H` using the shared `api_secret_key`.
4. `Registry.process` builds `WebhookMetadata` using `request.shop` = `"victim-shop.myshopify.com"` and dispatches to the topic handler, which now executes shop-scoped logic under the victim's identity using attacker-supplied body content.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
