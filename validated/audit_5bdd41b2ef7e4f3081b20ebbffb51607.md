### Title
Webhook shop-domain (and topic/api-version/webhook-id) headers are trusted without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the shop identity (`shop-domain` header) that the registry hands to application webhook handlers is read from an unsigned header. This breaks the identity binding `HMAC covers shop` that the report's analog class requires: the bytes cryptographically verified (`raw_body`) are not the same bytes that determine which tenant (`shop`) the webhook is attributed to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers, none of which participate in the signed string: [2](#0-1) 

`Utils::HmacValidator.validate` only ever checks the `hmac` field against `to_signable_string` (the raw body), never against the shop/topic/headers: [3](#0-2) 

`Registry.process` accepts any `Request` whose body HMAC validates, then unconditionally forwards `request.shop` (the unverified header) to the application handler as the tenant identity: [4](#0-3) 

Because the webhook HMAC key is the app's single `api_secret_key` (shared across every shop that installs the app, not a per-shop secret) and the signature covers only the body, a party that can obtain one genuine `(raw_body, hmac)` pair for the app (e.g., by installing the app on a shop they control and receiving a real webhook delivery, which is a normal unprivileged action) can resend that exact body/HMAC pair to the app's own webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop. `HmacValidator.validate` still returns `true` (the body/HMAC pair is valid), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop: [5](#0-4) 

The equality that should hold — `shop_used_by_handler == shop_that_originated_the_signed_bytes` — is never enforced anywhere in the gem, because `shop` is outside the HMAC's coverage.

### Impact Explanation
An attacker who legitimately installs the app on a shop they control can forge which shop a webhook is attributed to when replayed to the app's endpoint, since the signature never binds the shop identity to the payload. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to select which merchant's session/access token to update, process `app/uninstalled`, or fulfill GDPR `customers/redact` / `shop/redact` mandatory topics), this can result in cross-tenant data corruption or processing — e.g., an attacker causing the app to believe a victim shop uninstalled the app, or feeding attacker-controlled (but validly-signed, since it's their own real webhook data) events into a victim shop's data pipeline. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Medium-to-High. No secrets, TLS interception, or privileged access are required — only the ability to install the target app on an attacker-owned store (which is normal, unprivileged usage for any public embedded app) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint, which is by definition internet-reachable.

### Recommendation
Include the shop domain (and topic) in the HMAC-covered signable string, or otherwise independently verify that `request.shop` corresponds to a shop the app actually has an active session/installation for before trusting it as the tenant identity in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a genuine webhook delivery to the app's endpoint with a valid `x-shopify-hmac-sha256` computed over some `raw_body` using the app's shared `api_secret_key`.
2. Attacker captures `(raw_body, hmac)` from the request their own server received (fully legitimate, no interception needed).
3. Attacker sends a new HTTP request to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` and succeeds: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` is `"victim-shop.myshopify.com"`, even though the payload actually originated from the attacker's own shop: [5](#0-4)

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
