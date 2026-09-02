## Title
Webhook shop/topic identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — which are used to dispatch business logic and identify the tenant — come from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: ` [1](#0-0) `. The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all derived from HTTP headers that are never mixed into the signature: ` [2](#0-1) `.

`Registry.process` validates the HMAC over the request (which only proves the body was signed by Shopify with the app's secret) and then dispatches the handler using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` header values: ` [3](#0-2) `. The `HmacValidator` itself only checks `verifiable_query.hmac` against `verifiable_query.to_signable_string`: ` [4](#0-3) `.

This breaks the identity binding: `signed_body_HMAC == HMAC(shop_header, body)` is assumed by callers of `Registry.process`, but the actual check only proves `signed_body_HMAC == HMAC(body)`. The `shop-domain` (and `topic`/`webhook_id`) header is never bound to the signature, so `shop_that_signed_body != shop_header_used_for_dispatch` can be forced by the caller.

### Impact Explanation
An unprivileged internet user can install the target app on their own shop (a shop they legitimately control) to legitimately receive a genuine, correctly-HMAC-signed webhook body from Shopify for their own tenant. They can then replay that exact body/HMAC pair to the app's public webhook endpoint while spoofing the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a different, victim shop. Because `Utils::HmacValidator.validate` only verifies the body bytes and never the shop/topic headers, `Registry.process` will accept the forged request and invoke the registered handler with `WebhookMetadata` claiming the victim shop, topic, and webhook id ` [5](#0-4) `. Any app logic keyed on `data.shop` (e.g., updating that shop's stored state, marking uninstalled, deleting/altering per-shop records, or processing GDPR-style customer data requests) executes attributing the attacker-controlled payload to a shop the attacker does not control — a cross-tenant identity confusion introduced entirely inside this gem's webhook processing path.

### Likelihood Explanation
The only prerequisite is that the attacker can install the app on any shop (a normal, unprivileged action) to obtain one legitimately signed webhook body, and can then send an HTTP request to the app's public webhook endpoint with a spoofed header — no `api_secret_key`, access token, or privileged account is required. This is a straightforward, repeatable exploit reachable by any internet user targeting an app built on this gem.

### Recommendation
Include the tenant-identifying and action-relevant headers (`shop-domain`, `topic`, `webhook_id`, `api-version`) in the HMAC-signed payload — or otherwise cryptographically bind them to the raw body — so that `HmacValidator.validate` fails whenever any of these header values have been altered relative to what Shopify actually signed for that specific webhook delivery.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering Shopify to send a legitimate webhook (e.g. `orders/create`) with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(B)`.
2. Attacker replays a POST to the app's webhook endpoint with the same body `B` and same valid `X-Shopify-Hmac-Sha256`, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and/or the topic/webhook-id headers).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` and succeeds ` [6](#0-5) `.
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` reporting `victim-shop.myshopify.com` as the shop, even though Shopify never signed anything for that shop ` [7](#0-6) `.

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
