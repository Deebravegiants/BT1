Found it. This is the strongest analog to the M-23 "field used but not covered by the binding" bug class.

### Title
Webhook `shop` (and `topic`) identity used by handlers is taken from an HTTP header not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , but `Registry.process` treats the `shop` (and `topic`) header values as authenticated tenant identity and forwards them straight to the app's webhook handler [2](#0-1) .

### Finding Description
`Webhooks::Registry.process` validates the webhook using `Utils::HmacValidator.validate(request)` [3](#0-2) . `HmacValidator` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field of the same object [4](#0-3) . For `Webhooks::Request`, `to_signable_string` is defined as just `@raw_body` [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` values, however, are pulled from HTTP headers (`X-Shopify-Shop-Domain`, `X-Shopify-Topic`, etc.) via `shopify_header` [5](#0-4) [6](#0-5)  — none of which are part of the signed bytes. The HMAC only proves "this body was produced by Shopify using our secret"; it says nothing about which shop or topic the request claims to be for. Yet `Registry.process` passes `request.shop` and `request.topic` on to `WebhookMetadata` and the app's registered handler as if they were verified [7](#0-6) .

This is the exact bug class described in the report: a field (`shop`) is acted upon (used to route/tag the webhook payload to a tenant) but is not covered by the cryptographic binding (`HMAC` over the signable string), so "bytes verified" ≠ "bytes parsed/acted on."

### Impact Explanation
Because `shop` is not bound to the HMAC, if the host application relies on `WebhookMetadata#shop` to determine which merchant/tenant the payload belongs to (a documented and expected usage pattern in Shopify apps — e.g., looking up the session/access token for that shop and writing incoming data into that tenant's records), an attacker who can replay or forge headers on a request whose *body* signature matches for shop A can spoof the `shop` header to point at shop B. Since anyone with a Postman client can hit an app's public webhook endpoint, and only the `raw_body` is authenticated, an attacker controlling the header (e.g., a malicious/compromised proxy, or replaying a captured payload with a modified `shop-domain` header) can make the app process/store data under an incorrect tenant identity — a cross-tenant data integrity issue matching the "Critical - cross-tenant access" impact category, since the shop identity used for tenant-scoped processing is unauthenticated attacker-controlled input.

### Likelihood Explanation
Any unprivileged internet user who can send an HTTP request to the app's public webhook receiver endpoint can supply arbitrary headers, since headers are not covered by any cryptographic check — only the body is. No secrets, tokens, or privileged access are required; this fits squarely within the "unauthenticated internet user" threat model.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the signable payload (or otherwise cryptographically bind them, e.g., by re-deriving/validating them from Shopify's registered webhook metadata rather than trusting client-supplied headers), so `HmacValidator.validate` actually authenticates every field that `Registry.process` and downstream handlers rely on.

### Proof of Concept
1. Capture a legitimate webhook delivery for `shop-a.myshopify.com` with topic `orders/create`, including its valid `X-Shopify-Hmac-Sha256` header (computed over the raw body only).
2. Replay the exact same request to the app's webhook endpoint, but change the `X-Shopify-Shop-Domain` header to `shop-b.myshopify.com` (leave the body and HMAC header untouched).
3. `Utils::HmacValidator.validate(request)` in `Registry.process` still returns `true`, because `to_signable_string` only ever considered `@raw_body` [1](#0-0) .
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with the attacker-controlled `shop-b.myshopify.com` [8](#0-7) , and the app's handler processes the order payload as if it belonged to `shop-b`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
