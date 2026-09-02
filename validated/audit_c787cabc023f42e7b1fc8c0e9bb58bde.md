I found a concrete analog in the webhooks HMAC validation logic. Let me verify how `shop` is used downstream and confirm the signing scope.### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its `to_signable_string` using only the raw HTTP body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers and are never included in the HMAC computation. `ShopifyAPI::Utils::HmacValidator.validate` only proves that the *body* was produced by an entity possessing the app's `client_secret`; it proves nothing about which shop the request is claimed to originate from.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled straight from request headers with no cryptographic binding: [2](#0-1) 

`Registry.process` only verifies the HMAC over that signable string (the body) before dispatching to the app's handler using `request.shop` as the tenant identifier: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` compute the HMAC solely over `verifiable_query.to_signable_string` (the body), using the single, app-wide `Context.api_secret_key`: [4](#0-3) 

The handler then receives the `shop` field as the trusted tenant key, with no independent verification: [5](#0-4) 

This is exactly the "field acted on but not covered by the HMAC" bug class: the equality that should hold is `shop_bound_by_hmac == shop_used_for_tenant_dispatch`, but instead `shop_used_for_tenant_dispatch` comes from a bare header that is disjoint from the HMAC-covered bytes (`raw_body` only). Since the same `client_secret` is shared across every shop that installs a given app, any merchant who has installed the app on their own store can capture a legitimate `(raw_body, hmac)` pair from their own webhook deliveries (which they legitimately receive and can trivially trigger, e.g. by editing an order) and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain. `HmacValidator.validate` will pass because the body/HMAC pair is valid for the shared secret, and the host application's handler will process the payload as belonging to the victim tenant.

### Impact Explanation
This breaks the shop-to-signature identity binding and allows cross-tenant data injection/spoofing: an attacker (a legitimate but low-privilege user of the app in one shop) can make the app process attacker-controlled webhook data under a different, victim shop's identity. Depending on how the host application's `WebhookHandler#handle` implementation uses `data.shop` (e.g., looking up records, updating order/customer state, or authorizing further actions), this can lead to cross-tenant access or data corruption — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires the attacker to have installed (or have access to) the app on at least one shop that shares the same `client_secret` as the intended victim shop — a common scenario for public apps with many installs. No access to the app's secret or the victim's credentials is needed; only the ability to capture one's own legitimate webhook delivery and replay it with a modified header, which is straightforward for any authenticated merchant/admin of a shop that has installed the app.

### Recommendation
Bind the tenant/shop identity cryptographically to the HMAC-covered material, e.g., include the `shop`, `topic`, and `webhook_id` values as part of the signable string (or verify them against a value independently obtained via the offline session/token associated with that shop) rather than trusting the `X-Shopify-Shop-Domain` header outright. At minimum, cross-check `request.shop` against the shop associated with the session/store used to register the webhook before dispatching to the handler.

### Proof of Concept
1. Install the app on Shop A (attacker-controlled) and Shop B (target tenant), both apps share the same `client_secret` (standard for a single published app).
2. Trigger any webhook event on Shop A (e.g., update an order) and capture the raw request: `raw_body`, and header `X-Shopify-Hmac-Sha256`.
3. Replay this exact `raw_body` + `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC — it never checks `shop`.
5. `Registry.process` dispatches to the handler with `WebhookMetadata.shop == "shop-b.myshopify.com"`, even though the payload actually originated from Shop A, achieving cross-tenant confusion. [6](#0-5)

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
