This confirms the finding: `Request#shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers, while `to_signable_string` only returns `@raw_body` — the HMAC covers exclusively the body bytes, not the `shop-domain`, `topic`, or `webhook-id` headers.I have enough evidence to finalize the analysis.

### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted without HMAC coverage, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body [1](#0-0) . However, the identity fields that the gem hands to the app's `WebhookHandler` — `shop`, `topic`, and `webhook_id` — are parsed directly from HTTP headers and are never included in the signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `HmacValidator.validate` computes/compares the HMAC exclusively against that string [2](#0-1) [3](#0-2) . Meanwhile `Request#shop`, `Request#topic`, and `Request#webhook_id` are read straight from the `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers with no cryptographic binding to the signed body [4](#0-3) .

`Registry.process` passes these unauthenticated header values straight into `WebhookMetadata`, which the app's handler uses to decide which tenant/topic the event belongs to: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [1](#0-0) . `WebhookMetadata.shop` is a plain `String` field with no relation to the HMAC-verified bytes [5](#0-4) .

The broken identity binding, stated as an equality that should hold but doesn't:
`shop authenticated by HMAC` ≠ `shop delivered to the handler as WebhookMetadata#shop`

Because the gem's `Context.api_secret_key` is a single per-app client secret shared across every merchant install of the app (not a per-shop secret), any merchant who has legitimately installed the app can receive a validly-HMAC'd webhook body for their own store, then resend that same `raw_body` to the app's webhook endpoint while forging the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) headers to name a different, victim merchant's shop. `HmacValidator.validate` will still pass because it only checks the (unmodified) body bytes against the (unmodified, valid) HMAC — it never checks that the signature is tied to the claimed shop.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate app user for their own shop can cause the app's webhook handler to execute business logic (e.g., data sync, order/customer processing, mandatory GDPR `customers/redact`/`shop/redact` handlers) attributed to an arbitrary victim shop domain of their choosing, without ever needing the app's `client_secret`. Depending on the host application's handler implementation, this can lead to cross-tenant data corruption, injection of attacker-controlled data into another merchant's record, or triggering of tenant-scoped side effects (e.g., redaction/deletion) against a shop the attacker does not own — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is moderate to high for any app that installs on multiple shops (the standard SaaS model): every one of the app's own merchants is a valid, unprivileged source of a correctly signed body+HMAC pair, and no special credentials beyond a normal app install are needed to capture one and replay it with forged headers.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook-id` header values in the signable string used for HMAC validation (or otherwise cryptographically bind them to the signed payload) inside `Request#to_signable_string`, so that `HmacValidator.validate` fails if any of these identity fields are altered after signing.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com` and configures a webhook subscription (e.g. `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, and a valid `x-shopify-hmac-sha256` computed over the raw JSON body using the app's `client_secret`.
3. Attacker captures the exact `raw_body` and `x-shopify-hmac-sha256` value from this delivery.
4. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint again, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` — validation succeeds because the body/HMAC pair is unmodified [6](#0-5) .
6. The registered handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker's original body>, ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop [7](#0-6) .

### Citations

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
