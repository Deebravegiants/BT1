Confirmed: `ShopifyAPI::Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) computes the HMAC only over `verifiable_query.to_signable_string`, and for webhooks `Request#to_signable_string` returns just `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`). The `shop`, `topic`, `webhook_id`, and `api_version` fields are all pulled straight from unauthenticated headers (`lib/shopify_api/webhooks/request.rb:15-33`) and are never part of the signed payload. `Registry.process` validates only the HMAC and then trusts `request.shop` to build `WebhookMetadata` for the handler (`lib/shopify_api/webhooks/registry.rb:188-199`).

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/utils/hmac_validator.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body. The `x-shopify-shop-domain` (and `topic`/`webhook-id`/`api-version`) headers, which identify which merchant/tenant the webhook belongs to, are not included in the signed content, so they can be freely modified without invalidating the signature.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers that are never fed into the signature computation [3](#0-2) .

`Registry.process` relies on this incomplete check: it raises only if `Utils::HmacValidator.validate(request)` fails, then immediately trusts `request.shop` (and `request.topic`) to construct the `WebhookMetadata` passed to the app's handler [4](#0-3) .

Because the HMAC secret (`api_secret_key`) is shared across the whole app (not per-shop), any merchant who has installed the app on their own store receives genuinely Shopify-signed webhooks for their own shop. That merchant — an "unprivileged internet user" relative to any *other* tenant of the same app — can capture one legitimate `raw_body` + `hmac` pair from their own store's webhook deliveries, then replay the exact same HTTP request to the app's webhook endpoint while only changing the `x-shopify-shop-domain` header to an arbitrary victim shop. Since the header is not part of the signed content, `HmacValidator.validate` still succeeds, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the body came from the victim's shop.

This breaks the identity binding: **the shop that produced the authenticated bytes (the body, actually the requester's own shop) ≠ the shop the library reports to the handler (`request.shop`, attacker-controlled)**. Any downstream logic that uses `data.shop` to look up a session/access token (the intended, documented usage pattern for webhook handlers) will act as if the event originated from the victim shop, using the victim shop's session context while data content is controlled by the attacker.

### Impact Explanation
This allows cross-tenant impersonation of one shop's webhook traffic as another's: an attacker-controlled webhook body can be attributed to an arbitrary victim shop, letting a malicious merchant trigger the app's webhook-handling logic (e.g., data sync, order/customer processing, GDPR redact flows) against a victim tenant's stored session/state. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any user who can install the app on their own Shopify store (a low bar — this is the normal onboarding flow for any public/unlisted app) can obtain a validly-signed webhook and replay it with a modified `shop-domain` header. No secret, TLS interception, or privileged access is required — only capturing traffic to an endpoint the attacker's own browser/webhook receiver already sees.

### Recommendation
Include the shop domain (and other trust-relevant headers such as topic/webhook_id) in the HMAC-signed content, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`/`WebhookMetadata`. At minimum, document and enforce that `WebhookMetadata#shop` must never be used to select a session/access token without independent verification (e.g., cross-checking against the shop already associated with the resource in the payload).

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g., `orders/updated`) so Shopify sends a legitimately-signed webhook to the app's endpoint. Capture `raw_body` and the `x-shopify-hmac-sha256` header value.
2. Replay the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` still succeeds because it only checks `raw_body` against the secret [1](#0-0) .
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` [5](#0-4)  and passes it to the app's handler, which processes attacker-supplied content as if it belonged to `victim-shop.myshopify.com`.

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
