### Title
Webhook `shop` (and `topic`/`webhook_id`) are trusted from unauthenticated headers, not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC that `ShopifyAPI::Utils::HmacValidator.validate` checks binds nothing but the body bytes. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from HTTP headers and handed to the application's webhook handler without ever being covered by the signature that is supposed to authenticate the message.

### Finding Description
`Registry.process` only calls `Utils::HmacValidator.validate(request)` before dispatching to the registered handler: [1](#0-0) 

`HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` header: [2](#0-1) 

But `Request#to_signable_string` is defined to be just the raw body: [3](#0-2) 

Meanwhile `shop`, `topic`, and `webhook_id` are all pulled from unauthenticated headers and passed to the handler as trusted identity fields: [4](#0-3) [5](#0-4) 

This is exactly the "field acted on but not covered by the HMAC" pattern from the report: the equality the code implicitly assumes is `hmac_verified(body) == hmac_verified(body, shop, topic, webhook_id)`, but only the left side is actually checked. Since the HMAC secret (`Context.api_secret_key`) is shared across every shop that installs the same app — it is per-app, not per-tenant — any legitimate installer of the app can obtain a validly-signed webhook for their own shop, then resend the identical `body`+`hmac` pair while substituting the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header for a victim shop. `HmacValidator.validate` still passes because the signable string never included those headers, and `Registry.process` will invoke the handler with `shop: <victim>` for attacker-controlled body content.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate (even free/trial) installer of the host app can cause the app's webhook handler to process attacker-chosen payloads under another merchant's `shop` identity. Depending on how the host app's `WebhookMetadata` handler uses `shop` (e.g., to look up sessions, update per-shop data, or trigger per-shop side effects), this enables cross-tenant data corruption or confusion — matching the "cross-tenant access" High/Critical bucket.

### Likelihood Explanation
Exploitation only requires the attacker to be able to install the app on a shop they control (no special privilege, no leaked secret, no TLS interception) in order to receive one validly-signed webhook, and then to be able to send an arbitrary HTTP request to the app's webhook endpoint with a modified shop header — both are within reach of an unprivileged internet user interacting with the gem's documented webhook-processing API (`Registry.process`).

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body before dispatching to handlers, so a replayed/re-headered webhook cannot be revalidated for a different shop or topic.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook with body `B`, headers including `x-shopify-shop-domain: attacker-shop.myshopify.com`, and `x-shopify-hmac-sha256: H` where `H = HMAC(secret, B)`.
2. Attacker replays the request to the same endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes `HMAC(secret, B)` — still equals `H` — and passes.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., the app processes attacker-controlled data under the victim shop's identity, confirmed via: [1](#0-0)

### Citations

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
