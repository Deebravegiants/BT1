### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable payload from the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used downstream by the app come from unauthenticated HTTP headers. This breaks the identity binding: *shop bytes verified by HMAC* ≠ *shop bytes trusted and acted upon by the handler*.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` only checks that the HMAC matches `to_signable_string` (the raw body) against `Context.api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`, `request.webhook_id`) verbatim, handing them to the app-supplied handler as authenticated metadata: [4](#0-3) 

`WebhookMetadata#shop` is a plain `String` field with no further validation: [5](#0-4) 

Because the HMAC only signs `raw_body`, a valid `(raw_body, hmac)` pair computed by Shopify for a real webhook delivered to shop A's app remains a **valid signature** for that same raw_body no matter which `x-shopify-shop-domain` header is presented alongside it. This is exactly the report's "missing checks to distinguish two pools of value" bug class, mapped onto: *shop-domain bytes verified* should equal *shop-domain bytes acted upon*, but the gem never establishes that equality — the header is trusted independent of the signature.

### Impact Explanation
An unprivileged internet user who can obtain (or replay) any single legitimate webhook payload+HMAC pair for the target app (e.g. via a public webhook payload leak, a shared body across shops for topics with identical/empty bodies such as `app/uninstalled`, or their own store's webhook if the body happens to match) can resend it with an arbitrary `x-shopify-shop-domain` header. `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` forwards the attacker-chosen `shop` value to the host application's handler as if it were authenticated. Any app logic that keys off `WebhookMetadata#shop` (e.g., looking up/deleting the merchant's stored session or data for that shop, per the documented API in `docs/`) can be triggered for a victim tenant using data unrelated to that tenant — this is cross-tenant access.

### Likelihood Explanation
Exploitability requires the attacker to already possess one valid `(raw_body, hmac)` pair for the app (their own installation's webhook, or a body-agnostic mandatory topic). Given the gem's documented flow explicitly instructs apps to rely on `WebhookMetadata#shop` as the authenticated tenant identifier, and no part of the library binds shop to the signed bytes, likelihood is moderate — it depends on the topic's body being attacker-controllable or predictable, but the underlying binding gap is unconditional.

### Recommendation
Include `shop-domain`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them to the HMAC), or require host apps to independently verify `request.shop` against the session/tenant they expect before trusting `WebhookMetadata`. At minimum, document and enforce that `to_signable_string` must cover all header fields consumed by `WebhookMetadata`.

### Proof of Concept
1. Attacker's own store `attacker.myshopify.com` receives a legitimate webhook delivery with `raw_body = B` and header `x-shopify-hmac-sha256 = H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker resends the same `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `B` — validation succeeds: [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"`, an unauthenticated value the app treats as the legitimate source tenant.

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
