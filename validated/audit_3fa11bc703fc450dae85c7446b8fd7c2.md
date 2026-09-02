### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values used by the handler for tenant identification are read from unauthenticated HTTP headers. This breaks the intended binding: **bytes verified (raw body) ≠ bytes/fields acted on (shop-domain header)**, mirroring the reported bug class where a field that is acted upon (`maxPrincipal`) is not actually protected by the mechanism meant to guard state consistency (front-run overwrite). Here, the tenant-identifying `shop` field is never included in the cryptographic check at all.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop`, `#topic`, and `#webhook_id` are pulled directly from attacker-influenceable HTTP headers with no cryptographic linkage to the body or to each other: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then dispatches the handler using the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

Because the app's `client_secret`/`api_secret_key` is shared across every shop that installs the app (confirmed by `HmacValidator.validate_signature` using `Context.api_secret_key`), any shop that has legitimately installed the app receives real, validly-signed webhooks from Shopify for its own tenant: [4](#0-3) 

An installed (unprivileged, non-admin) merchant/tenant can capture one of their own genuine webhook deliveries (raw body + valid `X-Shopify-Hmac-Sha256`), and replay that exact body/signature pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. Since `to_signable_string` never includes the shop header, `Utils::HmacValidator.validate` still succeeds, and `Registry.process` forwards `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the app's handler as if the event genuinely originated from the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler will process/act on data tagged with an attacker-chosen `shop` value that was never authenticated, using a signature that was only ever proven for a *different* tenant's payload. Any app logic that trusts `data.shop` (e.g., updating per-shop state, redact/data-request handling for GDPR topics, billing, or notification routing) can be manipulated by one tenant to affect another tenant's stored data — a cross-tenant access condition, which maps to the "Critical" impact bucket.

### Likelihood Explanation
Exploitability requires only that the attacker be a legitimate, unprivileged merchant who has installed the app (no `api_secret_key`, no admin access, no TLS interception needed) — they simply capture a webhook Shopify already delivered to their own store and resend it with a modified `shop-domain` header. This is a low bar to clear and directly reachable through this gem's own documented webhook-processing API (`Registry.process`).

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind the shop/topic to the payload before dispatch, so that `Utils::HmacValidator.validate` fails if any of these values are altered independently of the body.

### Proof of Concept
1. App is configured with a shared `api_secret_key` used for HMAC validation of all shops' webhooks (`lib/shopify_api/utils/hmac_validator.rb`).
2. Attacker installs the app for `attacker-shop.myshopify.com` and receives a real webhook: body `B`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, header `X-Shopify-Hmac-Sha256: H` (valid for body `B`).
3. Attacker resends the same raw body `B` and same `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim-shop.myshopify.com", hmac-sha256: H...})` is constructed; `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` returns `B` only, unaffected by the header change (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to act on victim-shop's behalf using attacker-supplied data.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
