### Title
Webhook shop identity spoofing — HMAC covers only the raw body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Utils::HmacValidator.validate` computes/verifies the HMAC solely over that body. The `shop-domain` (and `topic`, `webhook-id`, `api-version`) HTTP headers are never included in the signed material, yet `Registry.process` uses `request.shop` — taken straight from the unauthenticated header — as the tenant identity passed to the app's webhook handler.

### Finding Description
`Webhooks::Request` exposes `shop` by reading the `x-shopify-shop-domain`/`shopify-shop-domain` header directly: [1](#0-0) 

The signable string used for HMAC verification is only the raw JSON body, excluding all headers: [2](#0-1) 

`HmacValidator.validate` verifies `hmac` against `to_signable_string` (the body) only: [3](#0-2) 

`Registry.process` checks only that the HMAC is valid for the body, then dispatches to the handler using `request.shop`, which is not covered by that check: [4](#0-3) 

The binding that is broken is: **shop the HMAC authenticates (none — HMAC only covers `body`) ≠ shop the handler trusts as tenant identity (`request.shop`, from an unsigned header)**.

Because the webhook secret (`api_secret_key`) is a single shared per-app secret, any entity that can obtain one valid `(raw_body, hmac)` pair for the app — e.g., a merchant who has installed the app and receives a legitimate webhook to their own store — possesses a message whose HMAC will validate successfully. Since `shop-domain`, `topic`, and `webhook-id` are not part of the signed content, that same `(raw_body, hmac)` pair can be POSTed directly to the app's public webhook endpoint with an arbitrary `x-shopify-shop-domain` header value naming a victim shop. `HmacValidator.validate` will pass, and `Registry.process` will invoke the handler with `WebhookMetadata` reporting the attacker-chosen `shop`, `topic`, and `webhook_id`, while the `body` is whatever content the attacker legitimately signed for their own store.

### Impact Explanation
This breaks the tenant boundary the whole webhook system is meant to enforce: the app has no cryptographic evidence that the `shop` value it will use to route/attribute a webhook event actually matches the shop that produced the body. A host application built on this gem's documented `Registry.process` API (which explicitly exposes `data.shop` and `data.topic` from `WebhookMetadata` for the handler to act on) will process the spoofed event as belonging to a different, targeted merchant — enabling cross-tenant data confusion/injection (e.g., faking `orders/create`, `app/uninstalled`, `shop/redact`, or GDPR-style topics for a shop the attacker doesn't operate) without ever needing the target's credentials, the app's `client_secret`, or an access token. This matches the Critical "cross-tenant access" impact category defined in scope.

### Likelihood Explanation
Likelihood is moderate-to-high: the attacker needs no special access beyond having (or being able to trigger) one legitimate webhook delivery to any shop of the app they control — which is trivial for any merchant that installs a public app and performs an action that triggers a webhook (e.g., creating an order in their own store). They then only need to know the app's public webhook endpoint (documented/discoverable) and can freely swap the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers while keeping the original signed body and HMAC.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before dispatching to the handler. At minimum, `Registry.process` (or a wrapping check) should validate that the shop associated with a webhook delivery corresponds to a shop with a currently valid session/registration for that specific topic, rather than trusting the `shop-domain` header as-is.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`) for it. They capture the raw POST body `B` and its valid `x-shopify-hmac-sha256` header value `H` (computed by Shopify using the app's shared `api_secret_key`).
2. Attacker sends a new POST directly to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid because it only covers the body)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (changed)
   - `x-shopify-topic`, `x-shopify-webhook-id` optionally changed
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` succeeds because it only recomputes over `raw_body`.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the host application to process attacker-supplied data as if it originated from `victim-shop.myshopify.com`.

### Citations

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
