### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the shop identity (`request.shop`) is read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header. `Registry.process` validates only the body's HMAC and then hands `request.shop` straight to the app's webhook handler as the tenant identifier, with no binding between the signed bytes and the shop field.

### Finding Description
`Registry.process` verifies a webhook exclusively through `Utils::HmacValidator.validate(request)`, which in turn calls `verifiable_query.to_signable_string` for the bytes to authenticate: [1](#0-0) [2](#0-1) 

`Request#to_signable_string` returns `@raw_body` exclusively — it does not include the `shop`, `topic`, or `webhook_id` header values in the signed payload: [3](#0-2) 

Yet `Request#shop`, which is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header with no cryptographic binding to the HMAC, is trusted as the tenant identity and forwarded into the handler: [4](#0-3) [1](#0-0) 

This breaks the identity binding the report describes: the equality that should hold is `hmac_verified_bytes == identity_attributed_bytes`, but here `hmac_verified_bytes = raw_body` while `identity_attributed_bytes = shop_header`, which is disjoint from what is signed. Because Shopify's HMAC covers only the body, any request whose body happens to have a valid signature for the merchant's own webhooks can be replayed with an arbitrary `shop-domain` header value and the signature will still validate — the gem provides no server-side cross-check tying the header-derived shop to the signed content, nor any correlation against `webhook_id`/topic registration state per shop.

### Impact Explanation
An attacker who operates their own Shopify store and registers the app's webhook endpoint can capture a legitimately-signed webhook payload/HMAC pair generated for their own shop, then replay that exact payload to the same webhook endpoint while substituting a victim shop's domain in the `shopify-shop-domain` header. `Registry.process` will accept it as valid (HMAC over the body still checks out) and will invoke the app's handler with `data.shop` set to the victim's domain, `data.body` under attacker control. Any app logic keyed off `data.shop` (e.g., updating merchant-scoped records, triggering merchant-scoped side effects, using the shop to look up/derive session/access tokens) is fed attacker-controlled tenant attribution — a cross-tenant identity confusion.

### Likelihood Explanation
Requires only an unprivileged attacker capable of running their own Shopify shop with the target app installed and observing outbound webhook requests to their own endpoint (no `api_secret_key`, no privileged access, no TLS interception needed). This is a low-cost, self-service attack path fully reachable through the gem's own webhook-processing surface (`ShopifyAPI::Webhooks::Request` / `ShopifyAPI::Webhooks::Registry.process`), not dependent on any host application misuse.

### Recommendation
Include the tenant-identifying fields (at minimum `shop-domain`, and ideally `topic`/`webhook-id`) as part of the signable string used for HMAC verification, or otherwise cryptographically bind the shop attribution to the verified request content, so that no unsigned header can override the identity presented to the handler.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Attacker triggers/receives a real webhook delivery, capturing `raw_body` and the valid `x-shopify-hmac-sha256` value Shopify computed over that body.
3. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only (per `Request#to_signable_string`) — it matches, so `Registry.process` proceeds. [1](#0-0) 
5. The registered handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` returns `"victim.myshopify.com"` taken from the spoofed header. [4](#0-3) 
6. The app processes attacker-controlled webhook content believing it belongs to `victim.myshopify.com`.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
