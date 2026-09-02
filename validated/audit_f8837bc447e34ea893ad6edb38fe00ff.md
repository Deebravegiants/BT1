### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw request body, then dispatches to the app's handler using the `shop` and `topic` values taken from HTTP headers that are never included in the HMAC input.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `topic`/`shop`/`webhook_id`/`api_version` are all read from unauthenticated headers via `shopify_header` [2](#0-1) . `Registry.process` validates the request purely with `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` (body-only) and compares against `Context.api_secret_key` [3](#0-2) [4](#0-3) . After that check passes, the *tenant identity* (`request.shop`) and the *event type* (`request.topic`) used to build `WebhookMetadata` — and route to the app's handler — come straight from the unauthenticated `shop-domain`/`topic` headers [5](#0-4) .

The binding that should hold is: `bytes verified by HMAC == bytes used to determine which shop/topic the event applies to`. Because the HMAC only proves "this body was produced with the app's secret," while the shop and topic used for dispatch are separate, unsigned bytes, an attacker who can obtain one valid `(raw_body, hmac)` pair for their own shop can freely replace the `shop-domain` and `topic` headers on the same request and still pass `HmacValidator.validate`, because that validator never inspects headers.

### Impact Explanation
This breaks the identity binding between the cryptographically verified payload and the tenant/topic used by the host application to act on it, enabling cross-tenant confusion at the webhook layer: a webhook whose HMAC is valid (because it was legitimately produced by Shopify for the attacker's own shop, or for any shop, since `api_secret_key` is shared across all installs of one app) can be replayed to the endpoint with a forged `shop-domain` claiming to be a different merchant, and/or a forged `topic` (e.g. relabeling a benign event as `app/uninstalled` or a `redact` topic). Any handler that trusts `data.shop`/`data.topic` from `WebhookMetadata` without an independent, out-of-band verification of shop-to-body correspondence can be induced to act on another tenant's account (deleting data, deactivating installs, mis-attributing GDPR redaction, etc.) — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires the attacker to control raw HTTP requests to the app's webhook endpoint (any unprivileged internet user with network access can do this once the endpoint URL is known/guessable) and to possess at least one legitimate `(raw_body, hmac)` pair, which any merchant with the app installed can obtain by triggering a real webhook from their own store. No `api_secret_key`, access token, or privileged account is needed beyond being a normal merchant of the target app. The main constraint is that the replayed body content must be plausible for whatever topic/shop the attacker claims, which is achievable for topics where the body shape is generic or attacker-influenced (e.g., product/order data the attacker fully controls in their own store).

### Recommendation
Bind the routing fields to the authenticated bytes: include `shop-domain`, `topic`, and `webhook-id` in the HMAC signable string (as Shopify's HMAC header itself is computed over body+relevant metadata in other Shopify verification schemes), or otherwise cryptographically bind headers to the payload before dispatch. At minimum, `Webhooks::Registry.process` should not treat header-derived `shop`/`topic` as trusted identifiers for authorization decisions unless they are covered by the same signature check that gates processing.

### Proof of Concept
1. App developer registers a webhook handler for topic `app/uninstalled` that deactivates/deletes the shop record identified by `data.shop`.
2. Attacker (a normal merchant using the app) triggers any legitimate webhook delivery from their own store, capturing the raw body `B` and its valid `hmac-sha256` header `H` (computed by Shopify with the app's `client_secret` over `B`).
3. Attacker replays a POST to the app's webhook endpoint with the same body `B` and header `H` (passes `Utils::HmacValidator.validate`, per `lib/shopify_api/utils/hmac_validator.rb`), but sets `X-Shopify-Topic: app/uninstalled` and `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` accepts the request (HMAC over `@raw_body` matches) and calls the `app/uninstalled` handler with `shop: "victim-shop.myshopify.com"`, causing the app to act on the victim tenant's record despite the request never having been authenticated for that shop or topic. [3](#0-2)

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
