### Title
Webhook HMAC only signs the request body, allowing shop/topic header spoofing for cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, and `webhook_id` entirely from HTTP headers, while the HMAC signature that `Utils::HmacValidator` verifies covers only the raw request body. An attacker who can obtain one genuine, validly-signed webhook (e.g., by installing the target app on their own store) can replay that exact body+HMAC pair to the app's webhook endpoint while freely rewriting the `shopify-shop-domain` and `shopify-topic` headers to any value, since those fields are never part of the signed data.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are read straight from attacker-controlled HTTP headers with no binding to the signature: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` — i.e., that the body matches the app's secret — before dispatching the handler for `request.topic` and passing `request.shop` straight through to the app's business logic: [3](#0-2) 

`HmacValidator.validate_signature` confirms only that the HMAC of the body matches the shared `api_secret_key` (or `old_api_secret_key`); it does not incorporate `shop`, `topic`, or `webhook_id` into the signed value at all: [4](#0-3) 

The identity binding broken is: `HMAC-verified bytes (raw_body) != identity fields actually acted upon (shop, topic, webhook_id)`. Since the app's `api_secret_key` is shared across every shop that installs the app, any legitimate (even free/unprivileged) installer can capture a validly-signed webhook delivered to their own store and replay it to the same endpoint with the `shopify-shop-domain` header swapped to a victim shop already known to be an installer of the same app, and/or the `shopify-topic` header swapped to a different registered topic. The signature still validates because it only checks the body bytes against the secret, so `Registry.process` will invoke the handler believing the event originates from, and pertains to, the victim shop/topic pair.

### Impact Explanation
This directly breaks the tenant isolation the whole webhook-processing model depends on. If the host app trusts `WebhookMetadata#shop` (as intended and documented for building per-shop side effects — e.g. billing, order sync, uninstall cleanup) it can be made to process attacker-supplied body content attributed to a different, victim shop, or to misroute an event to the wrong handler by spoofing `topic`. This is a cross-tenant data integrity/authenticity issue for any application relying on this gem's webhook signature verification to establish which shop and topic a webhook is trusted to represent.

### Likelihood Explanation
Exploitation requires only the ability to install the target app on any store (including a free development store) to legitimately receive one correctly-signed webhook, then replaying that exact body over HTTP with edited headers to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or privileged accounts is required — this is reachable by any unprivileged internet user who can install the app once.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the body before dispatch, so that `Registry.process` can guarantee the `shop`/`topic` values it hands to `WebhookMetadata` are authentic and match the request whose body was verified — not independently attacker-controlled header values.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, receiving a genuine webhook, e.g. `orders/create`, with body `B` and header `shopify-hmac-sha256: H` (valid for the app's `api_secret_key`).
2. Attacker replays `POST /webhooks` with the identical body `B` and `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim.myshopify.com` (a real installer of the app) and/or `shopify-topic: app/uninstalled`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` using the shared secret.
4. The handler registered for the spoofed topic is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: <spoofed>, body: <attacker's own body>, ...)`, causing the app to act on data purportedly from the victim shop.

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
