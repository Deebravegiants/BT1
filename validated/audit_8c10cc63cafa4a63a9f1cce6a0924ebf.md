### Title
Webhook shop-domain header not covered by HMAC allows cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` validates only the body HMAC and then forwards the header-derived `shop` value to the app's webhook handler as the tenant identifier. Because the app-level `api_secret_key` used to compute the HMAC is shared across every shop that installs the app (it's the app's client_secret, not a per-shop secret), an attacker who controls one shop with the app installed can capture a validly-signed webhook body from their own shop and replay it with the `X-Shopify-Shop-Domain` header (and/or topic/webhook-id) changed to point at a different (victim) shop.

### Finding Description
`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns `@raw_body` exclusively: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are read straight from request headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` verifies only this body-based HMAC, then immediately trusts `request.shop` and `request.topic` (taken from headers) to dispatch the payload to the app's handler as the identified tenant: [3](#0-2) 

The `HmacValidator` itself confirms the signature is computed solely over the signable string with the app's static `api_secret_key`, which is identical for every shop that installs the app: [4](#0-3) 

This breaks the identity binding: `shop authenticated by HMAC` should equal `shop used as the tenant/session key by the handler`, but here `to_signable_string` (what the HMAC actually authenticates) never includes `shop`, so `shop_verified_by_hmac == ∅ ≠ shop_used_for_dispatch (header value)`.

### Impact Explanation
Because the signing secret (`api_secret_key`) is shared across all shops of a given app, any merchant who installs the app can generate a validly-HMAC'd webhook body for their own shop, then replay/forge an HTTP POST to the app's webhook endpoint with the same signed body but an arbitrary `X-Shopify-Shop-Domain` (and topic/webhook-id) header pointing at a different shop. `Registry.process` will accept the HMAC as valid (it only checks the body) and pass the forged `shop` value straight into `WebhookMetadata`, which host applications use to select which tenant's data/session the payload applies to. This enables cross-tenant data injection/confusion — an attacker can make the app process fabricated events (e.g. `customers/redact`, `orders/updated`, `app/uninstalled`, etc.) as if they originated from a victim shop the attacker does not control, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even low-tier) merchant who has installed the target app — no leaked secrets, no privileged access, and no interaction with Shopify's TLS or infrastructure is needed. The attacker fully controls the headers of the HTTP request delivered to the app's own webhook endpoint since this gem performs no server-side origin/header authentication beyond the body HMAC. This is a straightforward, repeatable replay/tamper attack reachable through the gem's documented `Registry.process` API.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC validation, or otherwise cryptographically bind them (e.g., derive `shop` only from a value that is itself covered by the signature, similar to how `AuthQuery#to_signable_string` binds `shop`/`host`/`state`). At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate the raw header values that are later trusted for dispatch, so that any tampering with `shop`, `topic`, or `webhook_id` invalidates the HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com`, causing Shopify to send a legitimately signed webhook (e.g. `orders/updated`) to the app's webhook endpoint, with headers `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures this raw request (body + valid HMAC).
3. Attacker resends the identical body/HMAC to the same endpoint, replacing the header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally the `X-Shopify-Topic` header, e.g. to `customers/data_request` or `app/uninstalled`).
4. `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) succeeds because it only checks the (unmodified) body against the shared `api_secret_key`.
5. `Registry.process` dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the app's handler with `shop = "victim-shop.myshopify.com"`, causing the host application to process attacker-controlled data as an authentic event from the victim tenant.

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
