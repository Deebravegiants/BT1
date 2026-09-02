### Title
Webhook `shop` and `topic` fields are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body (`to_signable_string` returns `@raw_body`), but the `shop`, `topic`, `webhook_id`, and `api_version` fields — which are read from HTTP headers and then acted upon by `Registry.process` (used for handler routing and passed to the app as the tenant identifier) — are never included in the signed payload.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by comparing the HMAC over `to_signable_string` [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the HMAC [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` and `request.topic` to route to a handler and to build the `WebhookMetadata` passed to the app's handler as the tenant identifier: [4](#0-3)  The `WebhookMetadata` struct carries `shop` as a plain `String` with no further verification [5](#0-4) .

This breaks the intended identity binding: `HMAC-verified(body) == HMAC-verified(shop, topic)` is assumed by callers but never holds — the equality that should be enforced is `bytes_verified_by_hmac ⊇ bytes_acted_on`, yet `shop` and `topic` are acted on (used for routing and tenant attribution) without being covered by the HMAC. Since headers are attacker-controllable independently of the signed body, any party in possession of one valid `(body, hmac)` pair (e.g., an actual merchant who installed the app and can observe their own genuine webhook deliveries, or anyone able to replay/relay a captured webhook to the app's public endpoint) can resend the same body/hmac pair with an arbitrary `shopify-shop-domain` header. The HMAC check still passes because it only ever validated the body, and the app's handler receives a `WebhookMetadata` claiming to be from a different shop than the one that actually produced the payload.

### Impact Explanation
If a host application relies on `WebhookMetadata#shop` as the tenant key (the documented/expected usage pattern, since it's the only shop identifier supplied to `handler.handle`), an attacker can force cross-tenant processing: content or side effects (e.g., data deletion for GDPR `customers/redact`/`shop/redact` mandatory topics, or any app-specific business logic keyed by shop) can be triggered against a shop that never sent that payload. This satisfies the Critical "cross-tenant access" impact category, since the binding between the authenticated payload and the shop it is attributed to is not enforced by this gem.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one legitimate `(body, hmac)` pair — obtainable by anyone who runs the app on their own store and can observe/capture the webhook their own shop legitimately receives from Shopify — and the ability to POST to the app's public webhook endpoint with modified headers, which is a normal unauthenticated HTTP request (no `client_secret`, access token, or privileged access needed). This is a realistic, low-effort scenario for any unprivileged internet user/merchant.

### Recommendation
Bind the `shop` (and `topic`) claim into the material verified by the HMAC, or otherwise cryptographically/structurally tie the header-derived `shop` value to the signed body (e.g., require the shop domain to also appear inside the signed JSON payload and cross-check it against the header before trusting it in `WebhookMetadata`). At minimum, document that `WebhookMetadata#shop`/`#topic` are unauthenticated header values and must not be used as a sole tenant-authorization signal by host applications.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and captures a legitimate webhook POST that Shopify sends to the app's endpoint, containing `raw_body = B` and header `x-shopify-hmac-sha256 = H` (valid HMAC of `B` under the app's `client_secret`), plus `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same `raw_body = B` and `x-shopify-hmac-sha256 = H` to the app's public webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only, which still matches `H`, so `Registry.process` proceeds [6](#0-5) .
4. The app's `handler.handle` receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and performs its business logic (e.g., data mutation/deletion) attributed to `victim-shop.myshopify.com`, even though that shop never sent or authorized this webhook.

### Citations

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
