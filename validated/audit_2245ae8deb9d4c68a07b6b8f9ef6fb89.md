### Title
Webhook shop-domain identity is not bound to the HMAC-verified payload, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the shop identity (`shop-domain` header) used downstream by webhook handlers is never included in that signable string or otherwise cross-checked against it.

### Finding Description
`Registry.process` authenticates an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which validates `request.hmac` against `compute_signature(request.to_signable_string, secret)`. [1](#0-0) 

`Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

But the shop identity handed to the handler comes from a separate, unsigned header: [3](#0-2) 

`Registry.process` then passes this unauthenticated `request.shop` straight into `WebhookMetadata`, which the app's handler uses to attribute the webhook payload to a tenant: [1](#0-0) 

The identity binding that should hold is:
`authenticated_source(raw_body via HMAC(api_secret_key)) == shop_that_handler_attributes_data_to (request.shop header)`

This equality is never enforced. Because the `api_secret_key` used to compute webhook HMACs is a property of the app, not of an individual shop, any shop that has installed the app can obtain genuinely, validly-signed webhook bodies for events in its own store (e.g. by installing the app on an attacker-controlled development store and receiving real webhook deliveries). An attacker can then POST that exact raw body (with its still-valid HMAC) directly to the app's public webhook endpoint, but with the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body bytes, and `Registry.process` hands the handler `shop: <victim-shop>` together with attacker-chosen body content, `topic`, and `webhook_id`.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce: an unprivileged user (any merchant who can install the app on their own shop) can make a target app process arbitrary attacker-controlled webhook payloads while believing they originated from a different (victim) shop, since `request.shop` is trusted without being covered by the same authentication mechanism as the body. Depending on how the host app keys data or triggers actions off `data.shop` and `data.body` (e.g. updating shop-scoped records, order state, fulfillment, or billing based on webhook content), this enables cross-tenant data corruption or cross-tenant read/write, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires only: (1) the attacker owns/controls a shop that has installed the target app (a normal, unprivileged app install — no leaked secrets or privileged access needed), (2) the app's webhook endpoint is reachable over the internet (true by design, since Shopify itself POSTs to it), and (3) the ability to replay an HTTP POST with a modified header, which is trivial. The `api_secret_key` is shared across all shops of the app, so the attacker never needs the victim's credentials. This makes the likelihood high for any app that keys business logic on `WebhookMetadata#shop` without independent verification.

### Recommendation
Bind the shop identity into the authenticated material, e.g. by including the shop-domain header (and ideally topic/webhook-id) in the HMAC signable string (mirroring how `AuthQuery#to_signable_string` binds `shop`), or by cross-validating `request.shop` against a shop already known/registered for that specific webhook subscription before invoking the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, receiving a legitimate webhook POST for topic `orders/create` with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's `api_secret_key`.
2. Attacker replays the identical raw body and HMAC header to the app's webhook endpoint but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request; `Utils::HmacValidator.validate` succeeds because it only verifies `@raw_body`, per [4](#0-3)  and [5](#0-4) .
4. `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, as shown at [1](#0-0) , causing the host application to act on victim-shop data using attacker-supplied content.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
