### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` reads the `shop` (and `topic`) attribute from an unauthenticated HTTP header, while `Utils::HmacValidator` only verifies the raw request body against the app's shared `client_secret`. Because the shared secret is identical for every merchant using the app, an attacker who legitimately receives one valid, signed webhook (e.g., by installing the app on their own store) can replay that exact body to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. The signature still validates (it only covers the body), but `ShopifyAPI::Webhooks::Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `#topic` are pulled straight from attacker-controlled HTTP headers, entirely outside the signed bytes: [2](#0-1) 

`HmacValidator.validate` computes `HMAC(client_secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — it never incorporates `shop` or `topic`: [3](#0-2) 

`Registry.process` trusts the HMAC-validated request and forwards the unauthenticated `request.shop`/`request.topic` straight into `WebhookMetadata`, which is passed to the app's handler as the tenant identity for the event: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `HMAC-verified bytes == the full attested payload including shop/topic`. Instead the gem verifies `HMAC-verified bytes == raw_body only`, while `shop`/`topic` are asserted, not authenticated. Because `Context.api_secret_key` is the app's single `client_secret` shared across all installing shops (not a per-shop key — see `HmacValidator.validate`/`Context.api_secret_key` usage), a valid `(raw_body, hmac)` pair captured from any one shop's genuine webhook remains valid when replayed with a different `shop-domain` header value.

### Impact Explanation
This is a cross-tenant identity confusion: an app running for multiple merchants relies on `WebhookMetadata#shop` (and `#topic`) to route/authorize per-tenant processing (e.g., "delete data for this shop," "mark order paid for this shop," GDPR `customers/redact`/`shop/redact` handling). Since `shop` is not covered by the signature, a malicious merchant who has installed the app can generate a genuinely signed webhook with a chosen body (many webhook types, e.g. `app/uninstalled`, carry sparse/predictable JSON bodies), capture the valid `hmac`, and resend it with the `shop-domain` header (and `topic` header) set to any other value. `Registry.process` accepts it as authentic and invokes the handler believing the event is for the victim shop, potentially causing the attacker to trigger app-level state changes (uninstall handling, data deletion, order/webhook logic) attributed to a shop they do not own — a cross-tenant access/manipulation vector.

### Likelihood Explanation
Requires only an unprivileged internet user who can install the app on any store (satisfying "no privileged credentials" in the sense that no leaked secrets, tokens, or the app's actual `client_secret` are needed — only a legitimately obtainable webhook they were the intended recipient of) and can send arbitrary HTTP requests to the app's public webhook endpoint. No TLS interception, social engineering, or privileged account is required; it only depends on the host app calling `ShopifyAPI::Webhooks::Registry.process`/`Request.new` as documented, which is exactly the gem's intended usage.

### Recommendation
Bind `shop` (and `topic`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop/topic to the signed body (e.g., include them in `to_signable_string`, or require the host app to independently confirm `shop` against a known/registered shop before trusting `WebhookMetadata#shop`). At minimum, document that `shop`/`topic` in `WebhookMetadata` are unauthenticated and must be cross-checked by the caller against their own tenant registry before use.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com`, receiving a legitimate webhook (e.g., `app/uninstalled`) with body `{}` and headers `x-shopify-hmac-sha256: <valid_hmac_for_{}>`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the same raw body `{}` and same `hmac` header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` (and/or `x-shopify-topic` to another mandatory topic like `customers/redact`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, "{}")` — identical to the captured value — and passes: [6](#0-5) 
4. The handler receives `WebhookMetadata.new(topic: "customers/redact", shop: "victim.myshopify.com", body: {}, ...)` and performs the corresponding action against `victim.myshopify.com`'s data, even though the victim never sent or authorized this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
