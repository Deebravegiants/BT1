### Title
Webhook shop/topic/webhook-id headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity solely via `Utils::HmacValidator.validate(request)`, but the `Request#to_signable_string` used for that check only returns the raw HTTP body — none of the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers are part of the signed material. Those exact headers are, however, the values that are trusted and acted upon (`request.shop`, `request.topic`, `request.webhook_id`) when dispatching the webhook to the app's handler.

### Finding Description
`Webhooks::Request` mixes in `Utils::VerifiableQuery` and defines: [1](#0-0) 

so the HMAC is computed and checked only over `@raw_body`: [2](#0-1) 

Meanwhile the `shop`, `topic`, and `webhook_id` accessors read directly from unauthenticated headers: [3](#0-2) 

`Registry.process` validates only the HMAC and then hands the (unauthenticated) header-derived `shop`, `topic`, and `webhook_id` straight to the app's handler: [4](#0-3) 

The identity binding that is broken is: `hmac_valid(raw_body) == authentic(shop, topic, webhook_id, raw_body)`. In reality `hmac_valid(raw_body)` only proves the body was produced (at some point) by someone possessing `api_secret_key` — it says nothing about which shop, topic, or webhook the body was originally emitted for. Any bytes verified by HMAC (the body) are disjoint from the bytes actually parsed for tenant attribution (the headers).

### Impact Explanation
A merchant who has legitimately installed the app on their own store (an unprivileged party with no access to `api_secret_key`, access tokens, or any privileged account) will receive genuine, correctly HMAC'd webhook deliveries from Shopify for their own shop. Because the signature never covers the headers, that merchant can capture one such delivery (body + valid `hmac-sha256` header) and replay it to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header with a victim shop's domain / a different topic. `HmacValidator.validate` still succeeds (it only re-hashes `@raw_body`), and `Registry.process` dispatches the request to the handler with `WebhookMetadata` claiming it originated from the victim shop. This is a cross-tenant integrity violation: the app processes attacker-supplied data/events under a victim tenant's identity, satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Medium-High: any app installer can obtain one legitimately-signed webhook for their own store (no secrets required) and craft an HTTP request with modified headers using nothing more than a standard HTTP client. No credentials beyond a normal store installation are needed.

### Recommendation
1. Include the identity-critical headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body (e.g., HMAC over a canonical concatenation of header values + body), so `to_signable_string` cannot be satisfied by replaying a body signed for a different shop/topic.
2. As a defense-in-depth measure, require callers of `Registry.process` to pass the expected/registered shop (from their own session store) and assert it matches `request.shop` before dispatch, rather than trusting the header value implicitly.
3. Add regression tests asserting that changing `shop-domain`/`topic`/`webhook-id` headers while keeping body and HMAC constant causes verification to fail.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook (e.g. `orders/create`) to the app's endpoint:
   - Headers: `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: orders/create`, `shopify-hmac-sha256: <valid HMAC over raw body>`
   - Body: attacker-controlled JSON (attacker created the order on their own store, so they control the body content).
3. Attacker replays this exact body and HMAC header to the app's webhook endpoint, but changes `shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over `@raw_body` only — it matches, since the body is unchanged.
5. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-controlled data under the victim tenant's identity.

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
