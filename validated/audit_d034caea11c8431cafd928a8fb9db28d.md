## Title
Webhook `shop` (and `topic`/`webhook-id`) fields are trusted without being covered by the HMAC, enabling cross‑tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by checking the HMAC over the raw request body only, then hands the caller‑supplied `shop-domain` (and `topic`/`webhook-id`) header values straight to the app's handler as trusted identity data. Because those headers are not part of the signed payload, any party who can obtain one legitimately‑signed `(body, hmac)` pair — e.g., a merchant who has installed the app and therefore receives genuine Shopify webhooks — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. The signature still validates, but the `shop` value delivered to the handler is attacker‑controlled.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are read directly from unauthenticated headers with no cryptographic binding to that body: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string`, i.e. the body, and never over the shop/topic headers: [3](#0-2) 

`Registry.process` accepts the request once that body‑only HMAC check passes, then constructs `WebhookMetadata` using `request.shop` — the unauthenticated header — and dispatches it to the app's handler as the identity of the tenant the event belongs to: [4](#0-3) 

The equality this breaks: `shop_authenticated_by_hmac == shop_delivered_to_handler` does not hold — the HMAC authenticates only the body bytes, while the `shop` binding used to key tenant-specific logic in the handler is taken from bytes (`shopify-shop-domain` header) that are never verified. Since Shopify signs webhooks with the app's single `api_secret_key` (shared across every installed shop, not shop-scoped), any shop that has installed the app can capture a legitimately-signed `(body, hmac)` pair for its own events and resend it to the app's public webhook endpoint with a forged `shop-domain` header naming a different, victim shop.

### Impact Explanation
This is a cross‑tenant identity-binding bypass: the receiving app is led to believe a webhook body originated from shop B when it was actually replayed by an attacker who controls shop A. Any handler logic that trusts `WebhookMetadata#shop` to select which tenant's data to read, mutate, or delete (a common pattern for webhook consumers) can be tricked into acting on/for the wrong shop using attacker-supplied content, meeting the "cross-tenant access" bar.

### Likelihood Explanation
Reaching this requires only that the attacker be a merchant who has installed the app (an unprivileged position relative to any other tenant) and can capture one webhook of their own — a routine capability, since apps commonly expose webhook endpoints publicly and log/inspect their own incoming requests. No secret material besides an ordinary webhook that Shopify sends the attacker's own shop is needed.

### Recommendation
Bind the shop (and topic) identity into the value being verified, not just the raw body — e.g. require callers of `Registry.process` to independently confirm `request.shop` corresponds to an app-known/installed shop session before trusting the metadata, or extend the HMAC-covered signable string / verification step to include the `shop-domain` header rather than relying on body-only HMAC plus an unauthenticated header for tenant attribution.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering Shopify to send a legitimate webhook: body `B`, headers include `x-shopify-hmac-sha256: H` (valid for `B` under the app's shared `api_secret_key`) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` → `Utils::HmacValidator.validate` recomputes the HMAC over `B` only [5](#0-4)  and it matches `H`, so validation passes.
4. `WebhookMetadata.new(shop: request.shop, ...)` is built with `shop = "victim-shop.myshopify.com"` [6](#0-5)  and dispatched to the handler, which now processes attacker-controlled body content under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
