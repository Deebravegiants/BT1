### Title
Webhook HMAC only signs the raw body, so `shop`, `topic`, `webhook_id`, and `api_version` are unauthenticated and can be forged for cross-tenant spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC computed by `Utils::HmacValidator.validate` never covers the `shop`, `topic`, `webhook_id`, or `api_version` values that are read from HTTP headers and then trusted and forwarded verbatim to the app's webhook handler.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `api_version`, and `webhook_id` from request headers: [1](#0-0) 

But the value that is actually HMAC-signed and verified is only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, passes the unauthenticated `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` straight into `WebhookMetadata`, which is handed to the app's handler as trusted, verified data: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` (the raw body) and compares it against the `hmac` header — it never binds the header-derived fields into the signed content: [4](#0-3) 

The documented contract of `WebhookMetadata.shop` is that it identifies "The shop domain of the webhook" and is meant to be a merchant identity to key sessions/data on: [5](#0-4) 

This breaks the intended identity binding: `shop-verified-by-HMAC == shop-acted-on-by-handler`. In reality, only `raw_body == raw_body` is verified; the `shop` (and other header fields) used by the handler is never bound to the signature at all.

### Impact Explanation
Any party who can obtain one genuine `(raw_body, hmac)` pair for the app (e.g., by installing the app on their own store and receiving a legitimate webhook, which requires no special privilege beyond installing the app) can replay that exact body+hmac combination to the app's webhook endpoint while substituting an arbitrary `shop-domain` (and `topic`/`webhook_id`/`api_version`) header. Because `HmacValidator.validate` only checks the raw body against the shared secret, the forged headers pass verification, and the handler receives `WebhookMetadata` claiming to be from a victim shop it was never sent for. Depending on how the host app uses `data.shop` (e.g. mandatory `shop/redact`, `customers/data_request`, inventory/order sync keyed by shop), this allows cross-tenant data confusion/corruption — e.g. triggering a data-redaction or session-scoped side effect against a shop the attacker doesn't control. This matches the Critical "cross-tenant access" category since the tenant boundary (`shop`) is not cryptographically bound to the verified message.

### Likelihood Explanation
Exploitation only requires the ability to send arbitrary HTTP headers to the app's own public webhook endpoint together with a body/HMAC pair obtainable from any store where the attacker can install the target app (a normal, unprivileged action) — no access token, `client_secret`, or privileged account is needed. The vulnerable code path (`Request#to_signable_string`, `HmacValidator.validate`, `Registry.process`) is exercised on every webhook processed by every app using this gem's built-in webhook handling as documented.

### Recommendation
Include the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the signed payload (e.g., re-derive/verify `shop` from a signed claim, or reject processing unless these headers match values independently established for the session/registration they claim to belong to). At minimum, document loudly that `WebhookMetadata.shop`/`topic`/etc. are NOT covered by the HMAC and must not be trusted as tenant identifiers without additional verification.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled store `attacker-shop.myshopify.com`; capture a legitimate webhook delivery, e.g. `raw_body = '{"id":1}'` with header `x-shopify-hmac-sha256: <valid hmac of raw_body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Replay the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally forge `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request object whose `to_signable_string` is unchanged (still `raw_body`), so `Utils::HmacValidator.validate(request)` succeeds: [6](#0-5) 
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, even though this webhook was never sent for `victim-shop`: [7](#0-6)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
