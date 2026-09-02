## Finding: Webhook shop/topic/webhook-id identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing

### Title
Webhook `shop-domain`/`topic`/`webhook-id` headers are unauthenticated and can be swapped on a validly-signed payload, enabling cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers that are never covered by the signature. `Registry.process` trusts these header-derived values to route and label the webhook after verifying only that the *body* HMAC is valid. Anyone who receives a real, validly-signed webhook for one shop (e.g., because they installed the app on a shop they control) can resend the same body/HMAC pair to the app's webhook endpoint with different `shop-domain`/`topic`/`webhook-id` header values, and the HMAC check will still pass.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that are not part of that signable string: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts the header-derived `topic`/`shop`/`webhook_id`/`api_version` to route and label the event for the handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` (the raw body) and the shared `api_secret_key`: [4](#0-3) 

The identity binding that should hold is: `hmac == HMAC(secret, body || shop || topic || webhook_id)`. Instead, the gem only enforces `hmac == HMAC(secret, body)`, leaving `shop`, `topic`, and `webhook_id` completely unauthenticated. Since the webhook signing secret (`api_secret_key`/client secret) is shared across **every shop** that has installed the app, any party who legitimately receives one signed webhook (by installing the app on a shop they control, which is not a privileged action) possesses a `(body, hmac)` pair that remains valid for the app's client secret regardless of which shop or topic header accompanies it.

### Impact Explanation
An attacker who installs the target app on a shop they control (an ordinary, unprivileged action available to anyone) receives real, correctly-signed webhooks. They can then replay the same `raw_body`/`hmac-sha256` pair to the app's webhook endpoint while substituting the `shop-domain`, `topic`, and `webhook-id` headers. `Registry.process` will accept it (HMAC still matches) and dispatch `handler.handle` with `shop: <victim-shop>`/`topic: <arbitrary registered topic>`/`webhook_id: <arbitrary>`. This breaks the tenant isolation the host application relies on: the app's business logic (which typically keys off `shop` to decide which merchant record/session to act on) will process attacker-supplied data under another shop's identity, and/or under a different topic than what was actually sent (e.g., turning a `products/update` payload into a purported `app/uninstalled` or `shop/redact` event for a different shop). This is a cross-tenant identity confusion in the gem's own webhook trust boundary, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Likelihood is high in any deployment that lets outside parties install the app (which is the normal Shopify app distribution model): no privileged access, leaked secret, or credential is required — only the ability to install the app once on an attacker-owned store to harvest one legitimately signed webhook, and the ability to send arbitrary HTTP requests to the app's public webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id`/`api_version` in the HMAC-signable string (or otherwise cryptographically bind them to the body), so that `Utils::HmacValidator.validate` fails if any of these header-derived identity fields are altered relative to what was actually signed by Shopify. At minimum, the gem should document/verify that consuming applications cannot rely on `request.shop`/`request.topic` being authenticated by the HMAC check, and ideally should refuse to trust these fields unless bound into the signature.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` (unprivileged, self-service).
2. Receive a real webhook delivery, e.g. `orders/create`, with headers `shopify-topic: orders/create`, `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-hmac-sha256: <valid HMAC over raw_body>`, and some `raw_body`.
3. Replay to the app's webhook endpoint with the same `raw_body` and same `shopify-hmac-sha256`, but change `shopify-shop-domain` to `victim-shop.myshopify.com` (and/or change `shopify-topic`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — this passes because it only checks `raw_body` against the shared secret — and then calls the handler with `shop: "victim-shop.myshopify.com"`, causing the host application to process attacker-controlled data under the victim shop's identity. [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-38)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
