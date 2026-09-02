### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is not bound to the HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, and `webhook_id` values used downstream to attribute and route the webhook are read directly from unauthenticated HTTP headers. `Webhooks::Registry.process` verifies only the body's HMAC and then trusts these header-derived values, breaking the binding between "shop verified by the signature" and "shop the handler acts on."

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from headers with no cryptographic linkage to the HMAC: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` — i.e., HMAC over the body — and then forwards the unauthenticated `request.shop`/`request.topic` straight to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` confirms this: it signs/compares only `verifiable_query.to_signable_string`, which for webhooks is the raw body, never the shop header: [4](#0-3) 

Binding that should hold but does not: `shop_used_by_handler == shop_cryptographically_bound_by_hmac`. Since the webhook signing secret is the app's single `api_secret_key`/`client_secret` shared across every merchant who installs the app, any installer can trigger a legitimately-signed webhook from their own shop, capture the `(body, hmac)` pair, and resend it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop. `HmacValidator.validate` still passes because the header was never part of the signed content, so `Registry.process` calls the app's handler with `WebhookMetadata` claiming the victim's `shop`.

### Impact Explanation
This is a cross-tenant identity-binding break: a malicious tenant (merchant with the app installed) can make the app process arbitrary shop-attributed webhook data as if it originated from a different tenant's store, causing the host application to run tenant-scoped business logic (e.g., data updates, redaction triggers, entitlement changes) keyed off a `shop` value that was never authenticated. This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
Any account able to install the app on a shop (a normal, unprivileged merchant/tenant) can generate a validly-signed webhook body for a real topic and then freely rewrite the shop-identifying header before delivery, since `Registry.process` never checks that the header matches the HMAC-covered content or any known/expected shop for that delivery. No access token, `api_secret_key`, or privileged credential is required beyond ordinary app installation.

### Recommendation
Bind the shop identity to the verified content: include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (or otherwise cryptographically bind them), or require the caller to independently verify the shop-domain header against a known/registered shop (e.g., an existing session for that shop) before dispatching to `handler.handle`. At minimum, document that `request.shop`/`request.topic` are unauthenticated header values so host applications don't treat them as verified.

### Proof of Concept
1. Malicious actor installs the target app on `attacker-shop.myshopify.com`, triggering a real webhook (e.g., `orders/create`) signed with the app's shared `api_secret_key`.
2. Actor captures the raw body `B` and its valid `X-Shopify-Hmac-SHA256` header `H = HMAC(api_secret_key, B)`.
3. Actor POSTs `B` with the same `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds the request; `to_signable_string` returns `B` only.
5. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and matches `H` — validation succeeds.
6. The registered `handler.handle` is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host app to act as though `victim-shop` sent this webhook, even though it originated from the attacker's own store.

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
