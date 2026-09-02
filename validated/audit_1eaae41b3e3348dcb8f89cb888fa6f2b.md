Based on my investigation, I found a concrete analog matching the report's identified bug class — a field acted upon but not covered by the HMAC signature.

### Title
Webhook `shop`, `topic`, and `webhook-id` headers are trusted for tenant/routing decisions without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers and passed downstream as if they were verified.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes the signature over exactly that signable string using the app's shared `api_secret_key` [2](#0-1) . Meanwhile, `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are parsed straight from HTTP headers with no cryptographic binding to the signature at all [3](#0-2) .

`Registry.process` validates the HMAC and then immediately forwards the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to the app's handler as `WebhookMetadata`, treating them as if they had passed authentication together with the body: [4](#0-3) 

The broken identity binding is:
`bytes verified by HMAC (raw_body only)` ≠ `bytes acted upon (raw_body + shop + topic + webhook_id + api_version)`

Because every shop installation of a given app shares the same `api_secret_key` (webhooks are signed with the app's secret, not a per-shop secret) [5](#0-4) , any merchant who has installed the app can trigger a legitimately-signed webhook from their own store (a valid `raw_body` + valid HMAC computed with the shared secret), then replay that exact body and signature to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `topic`/`webhook-id`) header to claim it originated from a different, victim shop. The signature still validates because the shop identity was never part of the signed content, and `Registry.process` hands the forged shop identity to the handler as trusted metadata.

### Impact Explanation
This crosses a tenant boundary: the library-level authentication check (`HmacValidator.validate`) gives a false assurance that the entire webhook event — including which shop it is "from" — is authentic, when in fact only the body bytes are authenticated. Any host application that follows the documented pattern of using `WebhookMetadata#shop` (as shown in the library's own examples, e.g. `test/webhooks/registry_test.rb` assertions on `data.shop`) to route or attribute webhook data to a specific merchant/tenant record can have data injected under the wrong tenant, since the shop attribution was never actually authenticated.

### Likelihood Explanation
Any unprivileged party who can install the app on their own store (a normal, unprivileged action) can capture a validly-signed webhook body/HMAC pair and replay it with a forged shop header to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is required — only the ability to trigger an ordinary webhook to one's own installation and resend it with a modified header.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable content, or otherwise require the host application to independently verify the shop attribution against a value not derived from these headers before `Registry.process` forwards them as trusted `WebhookMetadata`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`. Trigger any subscribed webhook topic (e.g. `orders/create`); Shopify sends a POST with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's shared `api_secret_key`, plus `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture the raw body and the HMAC header value unmodified.
3. Replay the identical raw body and HMAC header to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` recomputes the signature over `request.to_signable_string` (the unmodified raw body) and it matches, so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: <attacker-controlled body>, ...)` [6](#0-5) , causing the app to process attacker-controlled webhook content under the victim shop's identity.

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
