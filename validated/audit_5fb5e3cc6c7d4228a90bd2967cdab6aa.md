### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unauthenticated headers while the HMAC signature only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, excluding the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id`, and `X-Shopify-Api-Version` headers from the bytes that are HMAC-verified, yet `Registry.process` dispatches to the app's handler using exactly those unauthenticated header values as the trusted tenant/event identity.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the HMAC solely over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic linkage to that body: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` and `request.topic` (both unauthenticated) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

This breaks the identity binding `shop authenticated by HMAC == shop delivered to handler`: the HMAC only proves "this body was produced with the app's `api_secret_key`" — it says nothing about which shop or which topic that body belongs to. Because the same shared `api_secret_key` is used for every shop that installs the app, an attacker who controls (or has installed the app on) any shop can capture one legitimate, validly-signed `(raw_body, hmac)` pair delivered to their own endpoint from their own shop, then replay that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) headers to name a victim shop. `Utils::HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` forwards the attacker-chosen shop/topic straight to the handler as if Shopify itself vouched for it.

### Impact Explanation
Any app handler logic that keys persistence, authorization, or side effects off `WebhookMetadata#shop` or `#topic` (exactly what the documented API is designed for) can be made to act on/against a shop the attacker does not own, because that identity is asserted by an unauthenticated header rather than by the HMAC-covered payload. This is a cross-tenant identity confusion: data intended to be scoped to the attacker's own shop can be injected/attributed to a victim shop's tenant context, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the target app on a shop the attacker controls (normal onboarding, not a privileged action), (2) capturing one raw webhook delivery HTTP request from Shopify to the app (visible to the receiving endpoint, or replayable from the attacker's own logs), and (3) sending a crafted HTTP request with the identical body/HMAC but altered `shop`/`topic` headers to the same public webhook endpoint. No `api_secret_key`, access token, or leaked credential is needed — the whole point is that the existing signature (obtained legitimately for the attacker's own tenant) remains valid after tampering with fields outside the signed scope.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) as part of the HMAC-signable bytes for webhook requests, or otherwise cryptographically bind the header-derived identity to the signed body before it is handed to `WebhookMetadata`/application handlers, so that `Utils::HmacValidator.validate` fails whenever any of these values is altered from what was originally signed by Shopify.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the delivered request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's shared `client_secret`).
2. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [4](#0-3) .
4. The app's registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes it as an authentic event for that shop, even though Shopify never sent anything for that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
