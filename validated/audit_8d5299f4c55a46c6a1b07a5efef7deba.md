## Finding: Webhook `shop`, `topic`, and `webhook-id` headers are not covered by the HMAC signature

### Title
Webhook shop/topic identity is trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values — which are extracted from separate, unsigned HTTP headers — are trusted and forwarded unchanged to the app's webhook handler. This is the same class of bug described in the external report: a value (`msg.sender`/here the `shop` identity) is acted on to make a security-relevant decision, but the binding of that value to the authenticated payload is broken.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC purely from this signable string and compares it to the `hmac` header: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the signed payload: [3](#0-2) 

`Registry.process` validates only the body HMAC, then passes the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` straight to the app's handler as the tenant/topic identity: [4](#0-3) 

The identity binding that should hold is: **`shop header == shop that produced/authorizes the signed body`**. Because the HMAC only covers `raw_body`, this equality is never checked — any request with a byte-identical body and a previously-valid HMAC for that body will pass validation regardless of which `shop-domain`/`topic`/`webhook-id` header values accompany it.

### Impact Explanation
An attacker who legitimately receives Shopify webhooks for their own store (e.g., by installing the app in a shop they control) obtains a body + HMAC pair that is valid forever for that exact body under the app's shared secret. They can then replay that same body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop, and/or a different `shopify-topic`/`shopify-webhook-id`. `Registry.process` will accept it as authentic (`Utils::HmacValidator.validate` only checks the body) and the app's handler will process attacker-supplied `body` content attributed to the victim's `shop`. Depending on how the host application's handler acts on `WebhookMetadata#shop` (e.g., updating shop-scoped records, triggering shop-scoped side effects, deduplication keyed by shop), this enables cross-tenant data corruption/confusion without requiring `api_secret_key`, an access token, or TLS interception — the attacker only needs to be a legitimate, low-privileged app installer in their own shop.

### Likelihood Explanation
Requires only running/installing the app in an attacker-controlled shop (an "unprivileged internet user" relative to other tenants) to harvest a valid body+HMAC pair, then a simple HTTP POST with forged headers to the app's public webhook endpoint. No secrets, tokens, or interception are needed.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable string (as Shopify's platform itself does when generating the signature over the full canonical request), or otherwise cryptographically bind these header values to the signed body before they are surfaced to consuming handlers via `WebhookMetadata`.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture a real inbound webhook request, e.g.:
   ```
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC for body B>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: <id>
   body: B
   ```
2. Replay the identical body `B` and `x-shopify-hmac-sha256` value to the same app endpoint, but change:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   x-shopify-webhook-id: <new-id>
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only recomputes the HMAC over `raw_body` (`B`) — it matches, so validation succeeds [5](#0-4) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes attacker-controlled body content as if it originated from the victim shop.

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
