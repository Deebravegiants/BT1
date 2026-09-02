Confirmed: this matches the analog pattern exactly — the `shop` header is a "field acted on but not covered by the HMAC."

### Title
Webhook `shop`, `topic`, and `webhook-id` fields are trusted without being covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the shop identity (`X-Shopify-Shop-Domain`), topic, and webhook id are read directly from unauthenticated HTTP headers and handed to the host application's webhook handler as trusted values.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` verifies the received HMAC solely against that signable string [2](#0-1) . Meanwhile `Request#shop`, `#topic`, and `#webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the body or its HMAC [3](#0-2) .

`Webhooks::Registry.process` validates only the HMAC, then dispatches `request.shop`, `request.topic`, and `request.webhook_id` straight to the app-supplied handler as authenticated `WebhookMetadata`, with no separate check that the claimed shop actually corresponds to the body that was HMAC-signed [4](#0-3) .

Because the app's `client_secret` (used to compute the webhook HMAC) is shared across every shop that installs the app, an unprivileged attacker can install the app on their own shop, capture a legitimately-Shopify-signed webhook (valid `body` + `X-Shopify-Hmac-Sha256`), and replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header with a victim shop's domain. `HmacValidator.validate` still returns `true` because the HMAC only ever verified the body, not the headers, so `Registry.process` will happily invoke the handler with `WebhookMetadata` claiming the data came from the victim shop.

The identity binding that should hold is: `shop_claimed_in_header == shop_that_actually_produced_and_owns_this_HMAC-signed_body`. Since the HMAC computation excludes the header entirely, this equality is never checked, breaking the tenant binding.

### Impact Explanation
Any application built on this gem that uses `data.shop` from `WebhookMetadata` to key storage, dispatch background jobs, or update per-tenant state (as the gem's own documented usage pattern shows: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to attribute attacker-supplied (but Shopify-legitimately-signed-elsewhere) webhook data to an arbitrary victim shop domain. This is a cross-tenant data injection/confusion vulnerability: an attacker with no access to the victim shop can cause events to be recorded, processed, or acted upon under the victim's tenant identity.

### Likelihood Explanation
Likelihood is high for any consumer of this gem that follows the documented pattern of trusting `data.shop`: the attack requires only the ability to install the app on an attacker-owned shop (an ordinary, unprivileged action available to any Shopify merchant) plus the ability to POST an HTTP request with a spoofed header, both trivial and requiring no leaked secrets or elevated access.

### Recommendation
Include the shop domain, topic, and webhook id (or the full raw request context) in the HMAC-signable string, or otherwise cryptographically bind the header-derived identity to the verified body before trusting `request.shop` in `Registry.process`. At minimum, document loudly that `request.shop` is not authenticated by the HMAC and must be independently validated (e.g., against a known/installed shop list) by the host application before use.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, a shop they legitimately control.
2. Shopify sends a legitimate webhook to the app's registered endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`. The attacker captures this request.
3. Attacker replays the exact same `B` and `H`, but changes the header `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. In `Webhooks::Request`, `to_signable_string` still returns `B`, so `Utils::HmacValidator.validate(request)` succeeds (`H` matches `HMAC-SHA256(client_secret, B)`) [1](#0-0) [5](#0-4) .
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)` [6](#0-5) , causing the host application to process attacker-controlled webhook content as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
