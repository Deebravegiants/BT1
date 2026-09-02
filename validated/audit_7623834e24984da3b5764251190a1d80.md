### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` headers are unauthenticated and unbound from the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then trusts `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` — all taken from unauthenticated HTTP headers — and hands them, unbound to that HMAC, to the merchant's webhook handler as `WebhookMetadata`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate(request)`, and then immediately trusts the header-derived `shop` value to build `WebhookMetadata`, which the host app's handler uses to attribute the event to a specific merchant/tenant: [3](#0-2) [4](#0-3) 

The identity binding that should hold is: `HMAC(body, secret) == received_hmac` **and** `shop header == the tenant the body actually belongs to`. Because `to_signable_string` only covers the body, this second equality is never enforced by the library. Any observer who has ever seen one valid `(body, hmac)` pair for the app (e.g. because they also run an install of the same app, or captured one webhook over an insecure channel) can resend that same body/hmac pair with an arbitrary `x-shopify-shop-domain` header. The `HmacValidator.validate` call in `lib/shopify_api/utils/hmac_validator.rb` (lines 26-31) will still pass, because `verifiable_query.to_signable_string` never includes `shop`: [5](#0-4) 

The library then reports this forged request as authenticated and passes the attacker-controlled `shop` value straight into the handler, letting the attacker impersonate a different merchant/tenant's webhook.

### Impact Explanation
This breaks the cross-tenant boundary: an app instance that legitimately receives webhooks for shop A can also inject events labelled as coming from shop B, because the shop identity is never part of what's verified. Depending on how the host application uses `data.shop` (as is documented/expected — see `docs/usage/webhooks.md`), this can cause cross-tenant data writes, incorrect app/uninstalled state transitions, or GDPR/data-erasure actions being triggered for the wrong shop — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one valid `(raw_body, hmac)` pair produced with the app's `api_secret_key` for any shop — realistic for a multi-tenant app since every installed shop is signed with the same app-level secret, and webhook bodies/topics are often predictable or replayable (e.g., `app/uninstalled` with an empty `{}` body, as used in this library's own test fixtures). No knowledge of `api_secret_key` itself is required, only observation of one legitimate webhook delivery, so likelihood is moderate rather than purely theoretical.

### Recommendation
Include the header-derived identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signable representation of the webhook request, or otherwise cryptographically bind the shop domain to the payload before trusting it, so that swapping the `shop`/`topic` headers on a previously valid `(body, hmac)` pair invalidates the signature.

### Proof of Concept
1. App is installed on both `shop-a.myshopify.com` and `shop-b.myshopify.com` (or attacker captures one webhook delivery for `shop-a`).
2. Attacker captures a legitimate webhook: `raw_body = "{}"`, headers include `x-shopify-hmac-sha256: <valid-hmac-of-{}>`, `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: app/uninstalled`.
3. Attacker replays the same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request whose `to_signable_string` is still `"{}"`; `Utils::HmacValidator.validate` succeeds because the hmac was computed only over the body.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: "app/uninstalled", shop: "shop-b.myshopify.com", ...)`, causing the host app to process an uninstall (or any other topic's) event for `shop-b` that Shopify never actually sent.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
