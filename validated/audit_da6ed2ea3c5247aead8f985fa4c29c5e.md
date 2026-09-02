### Title
Webhook HMAC signature only covers the request body, not the `shop`, `topic`, or `webhook-id` headers, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, and `webhook_id` are read from unauthenticated headers and are trusted for tenant/routing decisions after HMAC validation passes.

### Finding Description
The reported CLOB bug is that `order.prevOrderId` is mutated on a memory copy and never persisted, so a value the code *believes* is bound to the order is actually independent of it, breaking the invariant that link pointers reflect committed state. The same class of defect — "a value that is acted upon is not actually covered by the binding mechanism that is supposed to protect it" — exists in this gem's webhook verification.

`Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` are pulled straight from request headers, which are **not** part of the signed string: [3](#0-2) 

`Registry.process` validates only the HMAC (i.e., only the body) and then immediately trusts the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the merchant's handler: [4](#0-3) 

The invariant that should hold is:
`hmac_valid(body) == true` should imply `(shop, topic, webhook_id, body)` as a whole tuple came from Shopify for that shop. Instead, only `hmac_valid(body)` is checked, so `shop` (the tenant identity used downstream) is never bound to the signature that authenticates the request.

### Impact Explanation
If an attacker can ever obtain one valid `(raw_body, hmac)` pair produced by Shopify for their own store (i.e., a webhook legitimately delivered to the app for the attacker's own tenant), they can replay that exact body and HMAC to the app's public webhook endpoint while substituting `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) with a victim shop's domain. `HmacValidator.validate` will still pass because it only checks the body bytes, and the handler will process the payload as if it came from the victim shop — a cross-tenant identity confusion inside the app's webhook handling logic, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires the attacker to first observe a valid `(body, hmac)` pair, which normally only the app's own server receives directly from Shopify (Shopify does not route webhook deliveries through the attacker). This is feasible only if the app or Shopify's tooling exposes the raw delivery (e.g., logging, echoing, or a delivery-inspection feature), so likelihood is conditional rather than trivially exploitable by an anonymous internet user with no further assumptions. However, the root cause — `shop`/`topic`/`webhook_id` being outside the HMAC's scope — is a structural gap in this gem, matching Shopify's own documented webhook verification scheme (which signs only the body), so it is best understood as an inherent trust gap rather than a coding mistake unique to one code path.

### Recommendation
Do not treat `request.shop`, `request.topic`, or `request.webhook_id` as authenticated merely because `HmacValidator.validate` succeeded. Where feasible, cross-check the shop header against the requesting session/shop context already known to the app (e.g., the app's own record of installed shops) before dispatching to a handler, and document clearly in `Webhooks::Registry` that only the body is HMAC-authenticated so integrators do not implicitly trust the header-derived `shop` for tenant isolation decisions.

### Proof of Concept
1. Attacker installs the target app on their own development/trial store (no privileged access needed — self-serve).
2. Attacker triggers an action producing a webhook with a deterministic body (e.g., `orders/create` with attacker-controlled body content) and, through logging/echo/inspection in the app or Shopify tooling, obtains the exact `raw_body` and `X-Shopify-Hmac-Sha256` value Shopify sent to the app.
3. Attacker POSTs the same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain` to the victim shop's domain.
4. `Utils::HmacValidator.validate` succeeds (body+HMAC match), `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"`, causing the app to act on victim-shop data/state using attacker-supplied body content. [4](#0-3)

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
