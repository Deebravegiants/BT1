### Title
Webhook HMAC signs only the raw body, not the `shop-domain`/`topic`/`webhook-id` headers, enabling cross-tenant shop impersonation - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` returns only the raw request body, while `shop`, `topic`, and `webhook_id` are read directly from HTTP headers that are never included in the signed content. `Registry.process` trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the host app's handler, after validating only the body's HMAC. This breaks the intended binding: `shop_header == shop_that_produced_the_signed_body`.

### Finding Description
`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` value: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

But `shop`, `topic`, and `webhook_id` are pulled straight from headers, which are not part of the signed string: [3](#0-2) 

`Registry.process` validates the HMAC of the body, then unconditionally trusts `request.shop`/`request.topic` to build the metadata object handed to the app's webhook handler: [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that installs the app (it is not a per-shop secret), any merchant who installs the app receives legitimately HMAC-signed webhook deliveries for their own shop. That merchant can capture one such `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for an arbitrary victim shop domain. `Utils::HmacValidator.validate` will still return `true`, because it only re-derives the HMAC from `@raw_body`, which the attacker has left untouched. The equality the code implicitly assumes — "the header `shop-domain` I acted on" == "the shop whose secret produced this HMAC" — does not hold, because the header is never covered by the signature at all.

### Impact Explanation
This lets an unprivileged internet user (any merchant who has installed the app, or anyone who has captured a single legitimate webhook delivery) forge webhook events that host applications will process as belonging to an arbitrary other shop/tenant. Downstream apps typically use `WebhookMetadata#shop` to look up the tenant's session/access token or to route billing/inventory/order data — an attacker can attribute their own controlled payload to a victim shop, resulting in cross-tenant data confusion inside the host app. This matches the "cross-tenant access" Critical-impact category, since the identity binding (shop ↔ signed content) that the gem is supposed to guarantee is broken at the library level.

### Likelihood Explanation
Any merchant that installs the app already receives correctly-signed webhooks for their own shop by design, giving them a trivially obtainable `(body, hmac)` pair. The webhook endpoint is by definition public/unauthenticated (Shopify calls it over the internet), so replaying the same body with a substituted `shop-domain` header requires no special access, no leaked credentials, and no privileged account — only a basic HTTP client.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable content used for webhook HMAC verification, or otherwise cryptographically bind the shop/topic to the signature (e.g., verify that the attacker-observed values match a signature computed over `headers + body`), so that tampering with any of these headers invalidates the HMAC.

### Proof of Concept
1. App has shop A and shop B both installed, sharing the same `api_secret_key`.
2. Shop A performs some action (e.g., updates an order), causing Shopify to send a legitimately-signed webhook to the app's endpoint with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid-for-body>`.
3. The owner of shop A intercepts/logs this request (trivial, since it is delivered to their own configured endpoint or can be observed via any request logging they control).
4. The attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `shop-b.myshopify.com` (a victim shop they do not own).
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` and matches the untouched signature — validation succeeds.
6. `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)` is passed to the app's handler, which will process attacker-supplied data as if it originated from shop B.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
