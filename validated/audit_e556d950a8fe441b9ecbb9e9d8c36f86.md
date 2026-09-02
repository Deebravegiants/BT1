## Finding [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` (and `topic`) header is trusted for tenant attribution without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `HmacValidator.validate` only proves that the body bytes were signed with `api_secret_key`. The `shop` (and `topic`) values, read from `x-shopify-shop-domain`/`shopify-shop-domain` headers, are never included in the signed material, yet `Registry.process` forwards `request.shop` directly to the merchant-facing webhook handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as `@raw_body` only: [1](#0-0) 

`Request#shop` is read straight from an unauthenticated header with no cryptographic binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` computes the signature only over `to_signable_string` (the body) and compares against the `hmac` header: [4](#0-3) 

`Registry.process` accepts any request whose body+secret produce a matching HMAC, then dispatches the handler using the unauthenticated `shop` header value as the tenant identity for the payload: [3](#0-2) 

The equality the gem should enforce is: `shop bound in HMAC == shop used for tenant attribution`. Instead the gem enforces only `HMAC(body, secret) == received_hmac`, leaving `shop` (and `topic`) completely unbound. Any unprivileged internet user who legitimately installs the target app on their own store receives genuinely-signed webhook deliveries (valid `body` + `hmac` pair, signed with the app's real `api_secret_key`) for their own shop. Because the `shop` header is not part of the signed material, that same `(body, hmac)` pair remains valid when replayed to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain — `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the body belongs to the victim shop.

### Impact Explanation
This breaks the tenant/shop identity binding that webhook consumers rely on to route and persist per-merchant data (see `WebhookMetadata` and `shop:` usage), matching the "Critical – cross-tenant access" category: an attacker-controlled payload (from the attacker's own, legitimately signed webhook) can be attributed to a different merchant's shop, letting the attacker inject or spoof data/events into another tenant's processing pipeline.

### Likelihood Explanation
Any unprivileged internet user can self-install the target Shopify app (no special credentials, tokens, or `api_secret_key` knowledge required) to obtain a genuinely signed webhook body/HMAC pair for their own shop, then send an HTTP POST to the app's public webhook endpoint with that same body/HMAC but an attacker-chosen `x-shopify-shop-domain` header. No TLS interception, credential leakage, or privileged access is required — only the ability to send arbitrary HTTP requests to the app's public webhook URL, which is inherent to how the gem's `Registry.process`/`Request` model validates webhooks.

### Recommendation
Bind the `shop` (and `topic`) values into the material verified by the HMAC, or otherwise re-derive/cross-check the acting shop from a source under the app's control (e.g., match `request.shop` against the shop of the session/registration under which the webhook was registered) before dispatching to handlers, rather than trusting the raw header value for tenant attribution.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-serve, no privileges needed) and lets it trigger any subscribed webhook topic (e.g., `orders/create`), capturing the raw POST body and the `x-shopify-hmac-sha256` value Shopify sends — a valid `(body, hmac)` pair signed with the app's real `api_secret_key`.
2. Attacker resends the identical HTTP POST to the app's webhook endpoint, keeping `body` and `x-shopify-hmac-sha256` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `request.to_signable_string` (`@raw_body`) — validation passes because the body/secret pair is unchanged.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, where `request.shop == "victim-shop.myshopify.com"`, even though the payload actually originated from and describes the attacker's own shop — achieving cross-tenant data confusion.

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
