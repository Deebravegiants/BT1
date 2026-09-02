### Title
Webhook shop-domain header not covered by HMAC signature enables cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the Shopify HMAC signature over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values that the registry treats as the authoritative tenant identity for a webhook are read from unauthenticated HTTP headers that are never included in the signed material. This breaks the intended identity binding `hmac_signature == sign(body ‖ shop)`, actually enforcing only `hmac_signature == sign(body)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are all read straight from HTTP headers, which are attacker-controlled on any request reaching the app's public webhook endpoint, and are not part of the signable string: [2](#0-1) 

`Registry.process` only validates the HMAC over that signable string, then trusts `request.shop` as the tenant identity handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` simply checks that the received HMAC matches `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it authenticates the body bytes, not the headers: [4](#0-3) 

Because the signature only binds the body, any party in possession of one legitimately-signed `(body, hmac)` pair — for example an ordinary merchant who has installed the app on their own store and thus legitimately receives webhooks with a valid signature for that body — can replay that exact body and HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with a different (victim) shop's domain. `Utils::HmacValidator.validate` will still pass because it re-derives the signature from the same raw body, and `Registry.process` will hand the forged `shop` value to the app's handler as if it were authentic: [5](#0-4) 

This is the classic "field acted on but not covered by the HMAC" identity-binding break: the equality the library implicitly claims to enforce is `verified(shop, body) `, but what it actually enforces is `verified(body)` while `shop` is merely parsed and trusted.

### Impact Explanation
If the host application (following the documented usage pattern in `docs/usage/webhooks.md`, which explicitly says `data.shop` identifies "The shop domain of the webhook") uses `data.shop` to select which tenant's data/record to update in response to the webhook, an attacker who controls at least one legitimately-signed body/HMAC pair (trivially obtainable by installing the app on their own store, which is unprivileged from the perspective of any other tenant) can inject or mutate data under an arbitrary victim shop's identity — a cross-tenant access/write. This matches the Critical impact bucket ("cross-tenant access") defined in scope.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that follows the gem's own documented pattern (trusting `data.shop`/`data.topic` from `WebhookMetadata` as the tenant key) without independently re-validating that the shop is one for which a webhook of that topic/body was actually expected. No secrets, tokens, or privileged access are required — only the ability to install the app once (as any unprivileged merchant) to harvest a valid `(body, hmac)` pair, and the ability to send an HTTP POST to the app's public webhook route with modified headers.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material used for verification, or otherwise cryptographically bind the shop asserted in the header to the payload before trusting it (e.g., require the host app to independently confirm the shop has an active session/install before acting on the webhook). At minimum, update `Request#to_signable_string` so the computed signature commits to the exact `shop` value that `Registry.process` passes to the handler, and document clearly that `data.shop` must not be treated as authenticated unless this binding exists.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook (e.g. `orders/create`) to the app's endpoint. Attacker captures the raw body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` for that delivery (computed by Shopify over `B` using the app's shared secret).
2. Attacker sends a new POST to the same webhook endpoint with:
   - Body: same `B`
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because only `B` is signed)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic`/`X-Shopify-Webhook-Id` optionally changed as well
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds a `Request` whose `to_signable_string` is still `B`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` and matches `H` — validation succeeds.
5. The app's handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, i.e., data is now processed as if it belonged to `victim-shop.myshopify.com`, even though Shopify never sent this webhook for that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
