This confirms the vulnerability: the HMAC signature in `Webhooks::Request` only covers the raw request body via `to_signable_string` returning `@raw_body`, while `shop` (the tenant identifier used by the host application to route/attribute webhook processing) is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is completely outside the HMAC-signed content.This confirms `Registry.process` trusts `request.shop` (from the unsigned header) to construct the `WebhookMetadata` passed to the app's handler, while `Utils::HmacValidator.validate(request)` only verifies `request.hmac` against `request.to_signable_string` (the raw body) — the `shop` field never enters the HMAC computation at all.### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing shop-domain spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw webhook body for HMAC validation, but exposes an unauthenticated `shop` accessor that is read straight from the `x-shopify-shop-domain` HTTP header. `Webhooks::Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to build the `WebhookMetadata` object passed to the app's handler, without the shop ever being bound to the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from a header, independent of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC only against `verifiable_query.to_signable_string` (the raw body), never touching `shop`: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.shop` to construct `WebhookMetadata`, which is handed to the app's handler as the tenant identity for the webhook: [4](#0-3) 

The identity binding that is broken, expressed as an equality that the gem fails to enforce:
`HMAC-verified(raw_body)` ≠ `HMAC-verified(shop, raw_body)` — i.e., the gem verifies "these bytes came from Shopify using our secret" but the code (and app authors relying on this API) treat that as "this webhook, attributed to `request.shop`, came from Shopify for that shop." Since all shops installed on a single app share the same `api_secret_key`/`old_api_secret_key` (there is no per-shop secret in `Context`), a valid HMAC over a given body proves only that *some* shop's genuine webhook produced that exact body+signature pair — it proves nothing about which shop the body belongs to. Any attacker who can capture one legitimate raw-body/HMAC pair sent to the app's public webhook endpoint (e.g., from their own Shopify store, which they legitimately control) can replay that exact body and HMAC while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` because it never inspects the header, and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen shop domain instead of the shop that actually generated the event.

### Impact Explanation
This breaks the tenant/shop authentication boundary that `WebhookMetadata#shop` is documented and relied upon to provide to host applications: apps commonly use this field to look up the correct shop's session/access token or to scope data writes to the correct tenant. An attacker who owns (or has access to) any shop installed on the target app can capture a legitimate webhook and replay it against the same endpoint with a spoofed `shop` value, causing the host app to process/attribute data under a victim shop it does not control — a cross-tenant confusion vector that stems entirely from this gem's `Request`/`Registry`/`HmacValidator` design not binding `shop` into the signed payload. This maps to the "High: cross-tenant access" impact category, since it lets one tenant's authenticated request bytes be replayed to impersonate another tenant.

### Likelihood Explanation
Likelihood is realistic for any multi-tenant app built on this gem: an attacker only needs to be a legitimate, unprivileged merchant of the target app (no leaked secrets, no TLS interception, no social engineering) to capture one genuine webhook body+HMAC pair from their own store and then POST it to the app's public webhook endpoint with a forged shop-domain header. The gem provides no built-in defense (e.g., binding `shop`/`webhook_id`/timestamp into the signed string, or replay/nonce protection), so the entire mitigation burden falls on host apps correctly ignoring `request.shop`/`WebhookMetadata#shop` for security decisions — which is not how the API is designed to be used.

### Recommendation
Bind the shop identity to the verified content, e.g., include `shop-domain` (and ideally `webhook-id`/timestamp) inside the HMAC-covered signable string, or independently verify `request.shop` against a shop known to be associated with the specific access token/registration used to create that webhook subscription, before constructing `WebhookMetadata`. At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is not authenticated by `HmacValidator.validate` and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own Shopify store (Shop A) and registers to receive a webhook topic.
2. Shopify sends a legitimate webhook to the app's endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: shop-a.myshopify.com`.
3. Attacker replays the exact same body `B` and HMAC header to the same endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com` (a victim shop also installed on the app).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "shop-b.myshopify.com"...})` is constructed; `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes HMAC over `B`. [5](#0-4) 
5. `Registry.process(request)` invokes `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: parsed_body, ...))`, causing the app to process Shop A's data as if it belonged to Shop B. [6](#0-5)

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
