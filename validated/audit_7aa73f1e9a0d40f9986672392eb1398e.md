Based on my investigation, I found a concrete analog vulnerability in the webhook processing path.

### Title
Webhook `shop` (and `topic`/`webhook-id`) identity headers are trusted but not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` extracts the tenant-identifying `shop` (and `topic`, `webhook-id`, `api-version`) from HTTP headers, but the HMAC signature that `Registry.process` validates is computed **only over the raw request body**. The `shop` field that host applications rely on to identify which merchant a webhook belongs to is never cryptographically bound to the signature, breaking the equality: `shop authenticated by HMAC == shop used to attribute the webhook`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, ignoring all headers: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string`, i.e., only the body: [2](#0-1) 

`Registry.process` validates this body-only HMAC, then immediately trusts `request.shop` (parsed straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header, with no cross-check against the signed content) to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`Request#shop` simply reads the unauthenticated header value: [4](#0-3) 

Because the same `api_secret_key` is shared across all shops installed on a multi-tenant app, any merchant that has the app installed on their own store can capture a legitimately-signed `(raw_body, hmac)` pair from their own webhook deliveries (e.g., by proxying/inspecting their own endpoint traffic) and replay that exact body+HMAC to the app's shared webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. The HMAC check still passes because it only verifies the body was signed with the correct secret — it says nothing about which shop the body belongs to.

### Impact Explanation
This is a cross-tenant confusion: a webhook handler that uses `WebhookMetadata#shop` to look up the target merchant's session/access token or to perform per-tenant side effects (the exact intended usage pattern, per the gem's docs) can be tricked into executing shop A's webhook payload under shop B's identity. This satisfies the "cross-tenant access" Critical impact category, since it lets an unprivileged app-installing merchant forge webhook events attributed to another merchant's shop.

### Likelihood Explanation
Likelihood is realistic but requires an attacker to (a) have the app installed on their own store to obtain a validly-signed `(body, hmac)` pair, and (b) be able to send arbitrary HTTP requests directly to the app's public webhook endpoint with custom headers. Both conditions are satisfiable by any unprivileged internet user / self-service merchant, since Shopify webhook endpoints are plain public HTTP endpoints and header values are attacker-controlled in a raw request.

### Recommendation
Bind the identity headers into the signed material, or otherwise cryptographically tie `shop`/`topic`/`webhook-id` to the HMAC — e.g., include the headers in `to_signable_string`, or require host apps to independently verify that the `shop-domain` header matches a store known to have generated the specific `webhook-id`/payload (via a stored idempotency/session check) before trusting `WebhookMetadata#shop` for tenant-sensitive operations. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be used as the sole tenant-identity source.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and lets Shopify deliver a real webhook to the app's shared endpoint; attacker captures the raw JSON body and the `x-shopify-hmac-sha256` value from that request (e.g., via a logging reverse proxy they control in front of their own callback URL, or from app logs if exposed).
2. Attacker crafts a new HTTP POST to the same shared webhook endpoint, keeping the exact `raw_body` and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic` to a topic the app handles.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body against the secret: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, causing the app to process/act as if the victim shop sent this data.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
