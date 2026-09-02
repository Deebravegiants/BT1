## Finding

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` value that gets passed to the app's webhook handler is read from an unauthenticated header. Anyone who possesses one genuine `(body, hmac)` pair — e.g. a malicious merchant who has installed the app and received a real webhook for their own store — can replay that exact body/HMAC pair to the app's webhook endpoint with a forged `shopify-shop-domain` header, and the library will accept it as valid and hand the forged shop identity to the handler.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC by comparing the computed signature of `verifiable_query.to_signable_string` against the received signature: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw request body — it does not include the `shop`, `topic`, or `webhook-id` headers: [2](#0-1) 

Meanwhile, `shop` (and `topic`, `webhook_id`) are read straight from HTTP headers that are never mixed into the signed material: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then forwards the unauthenticated `request.shop` header value directly into `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The identity binding the library implicitly claims is: *"if the HMAC over this payload is valid, then `shop` (and `topic`/`webhook_id`) in this `Request` genuinely describe who the event is for."* In reality the equality that holds is only `hmac == HMAC(secret, body)`; there is no cryptographic link between the verified bytes and the `shop` header value the handler will trust. Because Shopify signs all webhooks for an app-installation with the same shared `client_secret` (not a per-shop secret), any shop that has installed the app can obtain a valid `(body, hmac)` pair from its own legitimate webhook traffic and replay that pair directly against the app's public webhook endpoint while substituting a different `shopify-shop-domain` header. `Utils::HmacValidator.validate` will report the signature as valid (it never looked at the shop header), and `Registry.process` will invoke the handler with an attacker-chosen `shop` value in `WebhookMetadata`, even though the event body was never generated for that shop.

### Impact Explanation
Any app whose webhook handler uses `WebhookMetadata#shop` to key merchant-scoped operations (which is the documented usage pattern — `handler.handle(data: WebhookMetadata.new(topic: ..., shop: request.shop, body: ..., ...))`) can be tricked into performing data mutations or reads attributed to the wrong tenant. This is a cross-tenant identity confusion rooted entirely in this gem's `Webhooks::Request`/`Utils::HmacValidator` design, not a misuse of a documented API by the host app — the gem itself hands out an unauthenticated `shop` value alongside an authenticated body and calls the pair "verified."

### Likelihood Explanation
Requires only an internet-reachable webhook endpoint (default for any Shopify app) and a merchant/attacker who has installed the target app on any shop (unprivileged relative to the target shop) so they can harvest one genuine `(body, hmac)` pair from their own store's webhook traffic and resend it with a spoofed `shopify-shop-domain` header.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable string, or otherwise fail closed if the header-derived `shop` cannot be cryptographically tied to the verified body — e.g. incorporate the headers into `to_signable_string` in `lib/shopify_api/webhooks/request.rb`, matching how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` into its signed payload.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; attacker triggers or waits for a real webhook and captures the raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(client_secret, B)`).
2. Attacker sends a POST to the app's webhook endpoint with body `B`, `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)` and it matches `H` (only the body was checked): [5](#0-4) 
4. `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` even though the payload `B` was generated for `attacker-shop.myshopify.com`. [6](#0-5)

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
