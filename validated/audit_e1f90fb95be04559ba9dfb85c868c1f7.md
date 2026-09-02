### Title
Webhook `shop-domain`/`topic`/`webhook-id` headers are trusted for routing and identity but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw HTTP body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` for routing and building `WebhookMetadata` are taken directly from unauthenticated HTTP headers. This breaks the identity binding `hmac-signed-bytes == bytes-that-determine-shop-identity`, allowing any holder of a validly-signed webhook body (e.g. a merchant who legitimately installed the app) to relabel that request as coming from a different shop.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` against the HMAC header [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight out of HTTP headers, which are never part of the signed material: [3](#0-2) 

`Registry.process` validates the HMAC over the body and then unconditionally trusts these header-derived fields to select the handler and construct the `WebhookMetadata` object dispatched to app code: [4](#0-3) 

Because the shop identity (`shop-domain` header) is not cryptographically bound to the HMAC, an attacker who can obtain one validly-signed webhook body/HMAC pair (trivially available to anyone who installs the target app on their own store and receives a genuine Shopify webhook) can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a different, victim shop. `HmacValidator.validate` still returns `true` because it only checks the raw body, and `Registry.process` then invokes the app's handler with `shop: request.shop` set to the victim's domain — a cross-tenant identity confusion inside the gem's own trusted API surface.

### Impact Explanation
This is a cross-tenant identity bypass: the gem asserts to the host application (via the `WebhookMetadata#shop` field passed to `handler.handle`) that a webhook came from a specific shop, based solely on an unauthenticated header, despite exposing an HMAC-verification API whose entire purpose is to authenticate the request's origin. Any app logic that trusts `WebhookMetadata#shop` after `Registry.process` HMAC validation (e.g. GDPR redaction, uninstall handling, billing state changes, data sync keyed by shop) can be triggered for an arbitrary victim shop by a user who only controls their own shop's webhook traffic. This matches the "Critical – cross-tenant access" impact category, since the binding broken is exactly "shop authenticated" vs. "shop the gem reports to the app."

### Likelihood Explanation
Likelihood is moderate-to-high: no special credentials, access token, or `client_secret` are needed. Any actor able to install the app on a shop they control receives genuine, correctly-HMAC'd webhook deliveries from Shopify and can capture the raw body/HMAC pair with an ordinary HTTP proxy. Replaying that exact body to the app's public webhook endpoint with a modified `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header requires no cryptographic secret at all, since those fields are excluded from the signed content by design of `to_signable_string`.

### Recommendation
Include `shop`, `topic`, and any other header-derived fields that influence routing or downstream trust decisions in the HMAC-signed payload (e.g., by having Shopify sign a canonical string of headers+body, or by requiring the host application to independently confirm the shop identity via a value that Shopify actually signs). At minimum, `Webhooks::Request#to_signable_string` should not allow `shop`/`topic` to be treated as authenticated once `HmacValidator.validate` returns `true`, and `Registry.process`/`WebhookMetadata` documentation should make clear that `shop` is unauthenticated and must not be trusted for tenant-identifying decisions without additional verification (e.g. cross-checking against a known/installed-shop list before acting).

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store; the app registers a webhook (e.g. `orders/create`) via `ShopifyAPI::Webhooks::Registry`.
2. Trigger a real event in the attacker's store so Shopify sends a legitimately signed webhook: headers include `shopify-hmac-sha256: <valid HMAC over raw body>`, `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: orders/create`.
3. Capture the raw request body and the `shopify-hmac-sha256` value unmodified.
4. Replay an HTTP POST to the app's public webhook endpoint with the identical raw body and `shopify-hmac-sha256` header, but set `shopify-shop-domain: victim-shop.myshopify.com`.
5. The app's endpoint calls `ShopifyAPI::Webhooks::Registry.process(request)`, which calls `Utils::HmacValidator.validate(request)` — this only hashes `@raw_body` [2](#0-1)  — so validation succeeds.
6. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim-shop.myshopify.com"` [5](#0-4) , causing the app to process an order-creation (or other) event attributed to a shop the attacker never interacted with.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
