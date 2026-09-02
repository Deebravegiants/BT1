### Title
Webhook shop/topic/webhook-id attribution not bound to HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated headers and never included in the HMAC-verified data. [1](#0-0) 

### Finding Description
`Registry.process` validates a webhook solely with `Utils::HmacValidator.validate(request)`, which delegates to `validate_signature`, computing the signature over `verifiable_query.to_signable_string` and comparing it against the `hmac` value. [2](#0-1) [3](#0-2) 

For `Webhooks::Request`, `to_signable_string` is defined as `@raw_body` only — none of the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, or `shopify-api-version` headers are part of the signed data. [4](#0-3) 

After the HMAC check passes, `process` reads `request.topic` (to look up the handler) and passes `request.shop`, `request.webhook_id`, and `request.api_version` — all header-derived, unverified values — straight into `WebhookMetadata` given to the app's handler. [5](#0-4) 

The binding that should hold is: `shop_bound_by_hmac == shop_used_for_business_logic`. Here, only `raw_body` is bound by the HMAC; `shop` (and `topic`/`webhook_id`) are not. Because the HMAC is computed with a single shared `client_secret` for every shop that installs the app (not a shop-specific key), any party who can obtain one validly-signed `(raw_body, hmac)` pair — trivially, by installing the app on their own store and capturing a legitimate webhook delivery — can resend that exact `raw_body`/`hmac` to the app's webhook endpoint with the `shopify-shop-domain` header (and/or `shopify-topic`) rewritten to a victim shop. The signature still validates because it only covers the body, but the app will process the payload as if it originated from the victim shop.

### Impact Explanation
This breaks the shop-authentication binding at the point where a webhook is attributed to a tenant, letting an attacker who is a legitimate (even free-tier) installer of the app forge webhook events "from" another shop. Depending on what the host application's webhook handler does with `data.shop` (e.g., writing order/customer/inventory data keyed by shop, updating billing state, revoking access, etc.), this can lead to cross-tenant data corruption or state manipulation — satisfying the "cross-tenant access" Critical impact category, since the trust boundary between shops is defined entirely by the (forgeable) `shop` header rather than by anything cryptographically bound to the request.

### Likelihood Explanation
Moderate-to-high: the attacker only needs their own valid app installation (no theft of the app's `client_secret`, no TLS interception, no privileged account) to capture one legitimate `(raw_body, hmac)` pair for a chosen topic, then replay it against the public webhook endpoint with a different `shop` header. This is directly reachable through this gem's own `Webhooks::Request`/`Registry.process` code path, not a host-application misuse.

### Recommendation
Bind the routing/attribution fields to the HMAC-verified payload: either (a) include `shop`, `topic`, and `webhook_id` in `to_signable_string` if Shopify's webhook signing were extended to cover them (not currently the case for Shopify's HMAC scheme), or, more practically, (b) require that the app independently confirm the `shop` header corresponds to a shop with a currently valid installation/session before trusting `data.shop`, and reject topic/webhook_id mismatches against the known registration for that shop, so a replayed body from one shop cannot be re-attributed to another. At minimum, document prominently that `request.shop`/`topic`/`webhook_id` are unauthenticated header values and must be cross-checked by the host application against a known-installed shop before use.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook for topic `orders/create`, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header (both are visible to the attacker as the destination server of their own store's webhook, or via any webhook proxy they control).
2. Attacker sends a new HTTP POST to the app's webhook endpoint with:
   - Body: the exact `raw_body` captured in step 1 (unchanged)
   - Header `X-Shopify-Hmac-Sha256`: the exact hmac captured in step 1 (unchanged)
   - Header `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic`/`X-Shopify-Webhook-Id`: optionally altered
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks presence, not content), and `Utils::HmacValidator.validate` succeeds because it only verifies `@raw_body` against the unchanged `hmac`. [6](#0-5) 
4. `Registry.process` dispatches the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)`, causing the app to act on attacker-controlled data under the victim shop's identity. [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
