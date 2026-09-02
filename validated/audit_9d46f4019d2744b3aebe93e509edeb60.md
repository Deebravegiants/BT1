### Title
Webhook shop/topic identity is not covered by the HMAC signature, allowing cross-tenant webhook impersonation - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body only, then dispatches the app's handler using these unverified header values as if they were authenticated, breaking the intended equality `hmac-verified byte range == identity fields the handler trusts`.

### Finding Description
`Request#to_signable_string` is defined to return `@raw_body` exclusively: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed directly from the `x-shopify-*`/`shopify-*` headers, none of which participate in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then hands the header-derived `topic`/`shop`/`webhook_id`/`api_version` to the registered handler as trusted metadata: [3](#0-2) 

The library's own `HmacValidator.validate` only recomputes and compares against `verifiable_query.to_signable_string`, i.e. the body — it never incorporates the headers into the signature check: [4](#0-3) 

This is exactly the reported bug class applied to an identity binding instead of a price: "bytes verified versus bytes parsed." The bytes cryptographically verified (the body) are not the same bytes the handler uses to decide *whose* data this is (`shop`) or *what kind* of event it is (`topic`). Any unprivileged internet user who can obtain one genuine webhook delivery with a valid HMAC — for example by installing the target app on their own store and receiving webhooks for it — can capture that `(body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `shopify-shop-domain` and/or `shopify-topic` headers. Because those headers are not covered by the signature, `HmacValidator.validate` still returns `true`, and `Registry.process` will invoke the handler believing the event legitimately belongs to the victim shop/topic.

### Impact Explanation
This breaks the identity binding `shop authenticated by HMAC == shop the app attributes data to`, which is a cross-tenant boundary violation. An app's webhook handler typically uses `WebhookMetadata#shop` to select the merchant's session/access token and to scope writes (e.g., upserting order/product records keyed by shop). By forging the `shop` header on a replayed, still-HMAC-valid payload, an attacker can cause the app to process fabricated events under another merchant's identity — potentially triggering side effects (database writes, outbound API calls using the victim's stored access token) attributed to a shop the attacker does not control. This matches the Critical-tier "cross-tenant access" impact category.

### Likelihood Explanation
The attacker only needs to be able to reach the app's public webhook HTTP endpoint and to have obtained at least one legitimately-signed `(body, hmac)` pair — trivially achievable by installing the app on their own development/test store, which any unprivileged internet user can do for public apps. No access token, `api_secret_key`, or privileged account is required; only header manipulation on a replayed request, which is fully within reach of a normal HTTP client.

### Recommendation
Bind the identity fields into the signed payload before trusting them: either include `shop`, `topic`, and `webhook_id` in the HMAC-covered signable string (matching how the field is actually consumed downstream), or have `Registry.process` independently corroborate the header-derived `shop`/`topic` against data embedded in the verified body before constructing `WebhookMetadata`. At minimum, document that header values on `Webhooks::Request` are unauthenticated and must not be used for tenant-scoping decisions without additional verification by the host application.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a genuine webhook, e.g. for `orders/create`, with headers:
   - `x-shopify-topic: orders/create`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid-hmac-of-body>`
   - body: `{"id": 1, ...}`
2. Attacker replays the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the HMAC against `request.to_signable_string` (the unchanged body) — validation succeeds: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: {...}, ...)`, causing the app to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

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
