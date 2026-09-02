Found a solid analog. In `lib/shopify_api/webhooks/request.rb`, the HMAC signature only covers the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — all used downstream by webhook handlers to determine tenant identity — are read directly from unauthenticated HTTP headers that are never included in the HMAC computation.### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted for tenant identity but are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook using `Utils::HmacValidator.validate(request)`, which only verifies the raw request body against the HMAC. The `shop`, `topic`, `webhook_id`, and `api_version` values passed to the handler as `WebhookMetadata` are read straight from HTTP headers that are never part of the signed payload, breaking the binding between "bytes verified" and "identity acted on."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes and compares the signature purely over `verifiable_query.to_signable_string`, i.e. the raw body only: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all derived from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are outside the HMAC's coverage: [3](#0-2) 

`Registry.process` only checks the HMAC before dispatching to the handler, and forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` header values as the trusted tenant/topic identity in `WebhookMetadata`: [4](#0-3) [5](#0-4) 

The equality that should hold is: `bytes_verified_by_HMAC == bytes_the_handler_trusts_for_tenant/topic_identity`. In this implementation, `bytes_verified_by_HMAC = raw_body` while `bytes_trusted_for_identity = shopify-shop-domain / shopify-topic / shopify-webhook-id headers`. These are disjoint, so the HMAC check gives no cryptographic assurance that the `shop` (or `topic`/`webhook_id`) attributed to a given verified body is the one Shopify actually intended.

Because the same app `client_secret`/HMAC key is shared across every shop that installs the app, any party who can obtain one genuine `(raw_body, hmac)` pair signed by that shared secret — for example by installing the app on their own shop and capturing/replaying webhook deliveries they legitimately receive — can resend that unmodified body with the same valid HMAC while swapping only the `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header to reference a different, victim shop. `HmacValidator.validate` still passes because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim shop/topic/id, causing the application to process attacker-supplied data under another tenant's identity.

### Impact Explanation
This breaks the tenant identity binding that webhook consumers rely on: the cryptographic guarantee (valid HMAC) is decoupled from the value (`shop`) the host application uses to route/attribute the webhook to a specific merchant record. An attacker who has legitimate access to their own shop's webhook stream (an "unprivileged" position relative to any other tenant) can forge cross-tenant webhook deliveries that pass this gem's own validation, tricking downstream application logic (e.g., `shop/redact`, `customers/redact`, order/product update handlers) into acting on attacker-controlled data as if it originated from a different, victim shop. This matches the "cross-tenant access" High-impact category in scope.

### Likelihood Explanation
Likelihood requires the attacker to have first obtained at least one valid `(raw_body, hmac)` pair signed with the app's shared secret — achievable simply by being a legitimate (if unprivileged) merchant/installer of the same app receiving its own webhooks — and then be able to reach the same app's webhook endpoint with a modified `shop-domain` header. Both preconditions are realistic for any public app with self-serve installation, so likelihood is moderate to high wherever a host application trusts `WebhookMetadata#shop`/`#topic`/`#webhook_id` for authorization or record lookup without independent verification.

### Recommendation
Include the header values that establish identity (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed payload used for verification — e.g., verify against a canonical string that binds headers to body, or additionally cross-check `shop` against a known/allow-listed set of installed shops before dispatch — rather than validating the body alone and blindly trusting header-derived identity fields in `Registry.process` and `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and configures a webhook subscription (or waits for one triggered by their own store activity).
2. Shopify delivers a webhook to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body>` and a JSON body.
3. Attacker captures this raw body and its valid HMAC (both are visible to them as the receiving party, or replayable via a proxy they control in front of their own endpoint).
4. Attacker resends the exact same raw body and HMAC header to the app's public webhook endpoint, but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/webhooks/hmac_validator.rb`/`request.rb` returns `true` because it only checks `raw_body` against the shared app secret, which is unchanged.
6. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", ...)` to the app's handler, causing it to process attacker-supplied order data attributed to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
