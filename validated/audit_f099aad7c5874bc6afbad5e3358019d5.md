### Title
Webhook `shop`, `topic`, `api_version`, and `webhook_id` headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the `shop`, `topic`, `api_version`, and `webhook_id` values used to dispatch and attribute the webhook are taken from unauthenticated HTTP headers that are never included in the signed content.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-api-version`, `shopify-webhook-id`) with no cryptographic binding to those headers: [2](#0-1) 

`Registry.process` verifies only the body HMAC via `Utils::HmacValidator.validate(request)`, then dispatches the handler using the unauthenticated `request.shop` and `request.topic`: [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the raw body only) using `Context.api_secret_key`: [4](#0-3) 

The identity binding that should hold is: `shop_header == shop_covered_by_hmac`. Because the signature only covers the body bytes, this equality never holds — the header `shop` is fully attacker-controllable independent of the signature. An unprivileged internet user who is a merchant using the app (and therefore legitimately receives valid, HMAC-signed webhook bodies for their own shop from Shopify) can capture one such valid `(body, hmac)` pair and replay it to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop). `Registry.process` will still consider the HMAC valid (since the body bytes are unchanged) and will hand the handler a `WebhookMetadata` object whose `shop` field is the attacker-chosen value, alongside the original signed body content. This lets a single legitimate webhook payload be replayed and falsely attributed to any other tenant shop known to the app.

### Impact Explanation
This crosses a tenant boundary: application code that trusts `WebhookMetadata#shop` (returned by `Registry.process`/`WebhookHandler#handle`) to select or mutate per-shop data will act on data belonging to shop A as if it belonged to shop B, since the shop identity is not authenticated. Depending on how the host application uses the webhook payload (e.g., writing order/customer data keyed by `shop`, triggering redact/mandatory-compliance actions, or driving business logic), this can result in cross-tenant data corruption or disclosure. This aligns with the "cross-tenant access" impact category.

### Likelihood Explanation
Medium-to-High: any merchant who has installed the app and has visibility into their own valid webhook deliveries (a normal, unprivileged capability) can capture a body+HMAC pair and freely re-send it with a forged `shop`, `topic`, `api_version`, or `webhook_id` header, since none of these are covered by the signature. No secret material or privileged access is required beyond being a legitimate, if untrusted, webhook recipient.

### Recommendation
Include `shop`, `topic`, and any other header value used for dispatch/attribution in the signed content that is HMAC-verified, or independently authenticate these headers (e.g., cross-check `shop` against a known/onboarded shop list bound to the session/access token, and require the header hash to match a signature computed over headers+body). At minimum, document that `Request#shop`/`#topic`/`#webhook_id`/`#api_version` are unauthenticated and must not be trusted by host applications for tenant attribution without additional verification.

### Proof of Concept
1. As a merchant who has installed the app, capture a legitimate webhook delivery HTTP request sent by Shopify to the app's configured endpoint — record the raw body and the `x-shopify-hmac-sha256` header value.
2. Re-send this exact `(raw_body, hmac header)` pair to the app's webhook endpoint, but replace `x-shopify-shop-domain` with a different shop's domain (e.g., `victim-shop.myshopify.com`).
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers, and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (only `@raw_body`) — this matches the captured HMAC because the body is unchanged: [5](#0-4) [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` where `shop` is the attacker-supplied "victim-shop.myshopify.com" value, despite the payload actually belonging to the attacker's own shop: [7](#0-6)

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
