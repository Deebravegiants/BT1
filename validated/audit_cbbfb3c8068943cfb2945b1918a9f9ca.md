This confirms the vulnerability. The `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are pulled directly from unauthenticated HTTP headers [2](#0-1) . The HMAC computed by `HmacValidator.validate_signature` only covers `verifiable_query.to_signable_string`, i.e., the raw body bytes, not the shop-domain header [3](#0-2) . Yet `Registry.process` passes the unauthenticated `request.shop` straight into the tenant-identifying `WebhookMetadata` handed to the app's handler [4](#0-3) .

### Title
Webhook `shop` (tenant identity) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the `shop` (and `topic`/`webhook_id`) fields used to attribute the webhook to a specific merchant are taken directly from HTTP headers that are never included in the signed bytes. This breaks the intended binding `hmac_verified_bytes == shop_used_for_tenant_routing`.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively [1](#0-0) . `Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the body or HMAC [5](#0-4) . `HmacValidator.validate` and `validate_signature` verify only `verifiable_query.to_signable_string` (the body) against the `hmac` header using `OpenSSL.secure_compare` [6](#0-5) . `Registry.process` accepts any request whose HMAC validates against the body, then constructs `WebhookMetadata` using the unauthenticated `request.shop` and hands it to the app's webhook handler, which apps use to key their per-merchant/session data [4](#0-3) .

Because the app's own `api_secret_key` is shared across all merchants for a given app (it's the app's single client secret, not per-shop), any merchant that has installed the app can obtain a validly-HMAC'd body (by triggering any webhook event in their own store) and then replay that exact body to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. The HMAC will still validate — since it was computed over the same body bytes with the shared `api_secret_key` — but the `shop` value delivered to the handler, and consequently any tenant-scoped action or record lookup performed by the host app, will incorrectly point at the victim shop.

### Impact Explanation
This crosses the tenant boundary the HMAC is meant to enforce: an unprivileged merchant/attacker can cause the app to process attacker-controlled webhook content under a victim shop's identity, i.e., cross-tenant access/attribution without needing the victim's credentials — matching the "shop authenticated versus the shop stored as a session key" analog explicitly called out in scope.

### Likelihood Explanation
Likelihood is high for any app that (a) installs the app on multiple shops (any multi-tenant SaaS app built on this gem inherently does), and (b) uses `WebhookMetadata#shop` from the callback to identify which merchant record to update — which is the documented intended usage pattern of this gem's webhook API. No special privileges beyond being an existing app installer are required to obtain a validly-signed body.

### Recommendation
Include the `shop` (and ideally `topic`) header value in the bytes that are HMAC-verified, or otherwise cryptographically bind the shop identity to the signed payload before it is trusted for tenant routing, e.g., extend `VerifiableQuery#to_signable_string` for webhook requests to include the normalized `shop-domain` header, or require callers to independently validate `request.shop` against the session/shop that is expected to receive that specific webhook_id.

### Proof of Concept
1. App is installed on `attacker.myshopify.com` and `victim.myshopify.com`.
2. Attacker triggers any webhook event (e.g., updates a product) in their own store, capturing the resulting POST: raw body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the identical body `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks `B` against `H` using the shared `api_secret_key` [3](#0-2) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com", body: <attacker-controlled parsed body>...)` [7](#0-6) , causing the host app to act on the victim's tenant record using attacker-supplied data.

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
