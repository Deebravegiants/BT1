### Title
Webhook shop/topic identity is not bound to the HMAC signature, enabling cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content from the raw body only, while the `shop`, `topic`, and `webhook_id` values used by the library to route and label a webhook are taken from unauthenticated HTTP headers that are never covered by the HMAC. Any party that possesses one valid `(raw_body, hmac)` pair signed with the app's secret (trivially obtainable by installing the app on an attacker-controlled development store) can resend that same body/HMAC to the app's webhook endpoint with a different `shopify-shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic for the spoofed shop.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are read directly from HTTP headers, independent of the signed body: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then dispatches using the header-derived `shop`/`topic` values without any cross-check that they were part of what was signed: [4](#0-3) 

This breaks the intended identity binding: `hmac-verified(body) == authenticated(shop, topic, webhook_id)` does not hold — the equality that should be enforced is `shop header ∈ signed material`, but in reality `shop header ∉ signed material`. Consequently, the "shop that the HMAC proves originated the payload" and the "shop the library trusts and hands to the app's webhook handler" (`WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`) are two different, unlinked values.

### Impact Explanation
An attacker who installs the target app on their own (attacker-owned) development/trial store can trigger any webhook topic they choose and legitimately receive a `(raw_body, hmac)` pair signed by the app's real `api_secret_key`. Because the shop header is not part of the signed material, the attacker can replay that exact body+HMAC to the app's public webhook endpoint while substituting the `shopify-shop-domain` header (and/or `shopify-topic`, `shopify-webhook-id`) with a victim shop's domain. `Registry.process` will treat the forged request as a valid, authentic webhook for the victim shop and invoke the host application's registered handler with attacker-controlled body content labeled as belonging to the victim tenant. Depending on how the host app's webhook handlers key their storage/actions by `shop` (a documented and expected usage pattern, e.g., `WebhookMetadata#shop` in `lib/shopify_api/webhooks/metadata.rb`), this enables cross-tenant data injection/confusion — data intended for one merchant is attributed to and processed under another merchant's identity.

### Likelihood Explanation
Medium-to-High: no privileged credentials, tokens, or TLS interception are required. The only prerequisite is the ability to install the app once on any store (including a free development store the attacker controls) to obtain one valid signed payload, after which the shop/topic/webhook-id headers can be freely substituted for arbitrary values while still passing `HmacValidator.validate`.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-verified signable content, or otherwise cryptographically bind them to the request (e.g., have `Request#to_signable_string` incorporate these header values alongside the raw body), so that the HMAC check in `Utils::HmacValidator.validate` proves authenticity of the shop/topic identifiers, not just the body bytes.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers/triggers a webhook (e.g., `orders/create`), capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` sent by Shopify (computed as `HMAC-SHA256(api_secret_key, B)`).
2. Attacker sends a new HTTP request to the same app's webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic`: any registered topic of the attacker's choosing
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (`lib/shopify_api/webhooks/request.rb:45-63`), and `Utils::HmacValidator.validate` succeeds because `to_signable_string` only checks `B` against `H`, which still match. [5](#0-4) 
4. `Registry.process` invokes the host app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B))`, causing the application to process attacker-supplied content under the victim shop's identity.

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
