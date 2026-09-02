This confirms the finding. The `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the body's HMAC and then trusts `request.shop`/`request.topic` for dispatch [3](#0-2) .

### Title
Webhook shop/topic identity spoofing via HMAC-unsigned headers - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers that are never included in the signed payload. `Registry#process` validates the HMAC and then uses these unsigned header values to route the webhook and to populate `WebhookMetadata` for the handler, so the shop identity that the handler ultimately trusts is not bound to the HMAC-authenticated bytes.

### Finding Description
The binding that should hold is: `shop used by handler == shop cryptographically bound to the verified payload`. Here that equality is broken because:

- `HmacValidator.validate(verifiable_query)` verifies `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, verifiable_query.to_signable_string)` against the `hmac` header [4](#0-3) .
- For webhooks, `to_signable_string` is just the raw body [1](#0-0) ; the `shop-domain`, `topic`, and `webhook-id` headers are completely outside that signed string.
- `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e. body integrity) before trusting `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the application's handler [3](#0-2) .

Because the shop identity is never covered by the HMAC, any request carrying a body/HMAC pair that once validated for one shop (i.e., a genuine webhook the attacker legitimately received, e.g., because they installed the app on their own store) can be replayed to the app's webhook endpoint with the `shop-domain` header rewritten to name a different (victim) shop, or with the `topic`/`webhook-id` headers rewritten. The signature still validates because those fields were never part of the signed bytes, so the handler receives `WebhookMetadata` attributing attacker-controlled data to a shop/topic it did not actually originate from.

### Impact Explanation
This crosses a tenant boundary: an unprivileged party who is a legitimate (even free/trial) app installer for their own shop can forge the apparent origin shop of a webhook payload without needing the app's `api_secret_key`. Any application logic keyed by `WebhookMetadata#shop` (e.g., "update data for shop X", "trigger uninstall cleanup for shop X") can be invoked with an attacker-chosen shop value while carrying attacker-controlled body content, resulting in cross-tenant data manipulation — matching the "Critical: cross-tenant access" impact category driven purely by a gem-level identity-binding gap.

### Likelihood Explanation
Exploitation requires only: (1) install the target app on any shop the attacker controls (or otherwise obtain one valid raw_body + HMAC pair for a topic of interest), and (2) resend that exact body/HMAC to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header replaced. No secret material, TLS interception, or privileged access is needed — this is reachable by any internet user who can install the app once.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed content (e.g., sign a canonical string combining these headers with the raw body), or otherwise cryptographically bind `shop`/`topic` to the verified payload before constructing `WebhookMetadata`, mirroring the fix pattern used for `AuthQuery#to_signable_string` which does include all its identity fields [5](#0-4) .

### Proof of Concept
1. Install the target Shopify app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook (e.g. `orders/create`) and capture the raw request body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` that Shopify computed over `B` using the app's shared secret.
2. Replay a POST to the app's webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com` (and/or a different `X-Shopify-Topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` [6](#0-5) , which recomputes the HMAC over `B` only and succeeds, since `shop`/`topic` were never part of the signed bytes.
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [7](#0-6)  reporting `shop == "victim.myshopify.com"` even though the payload never originated from Shopify for that shop, demonstrating the broken identity binding.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
