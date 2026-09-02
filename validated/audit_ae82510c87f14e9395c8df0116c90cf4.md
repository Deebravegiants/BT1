### Title
Webhook `shop` (tenant) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and exposes an HMAC-validated webhook, but the signature only covers the raw request body. The `shop` (tenant identifier) that the gem hands to the app's webhook handler is read from a separate, unsigned HTTP header, so a valid HMAC does not bind the request to the shop it claims to be from.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac` header value — it never incorporates the shop header into the signed material: [3](#0-2) 

`Webhooks::Registry.process` trusts this unauthenticated `shop` value once the (body-only) HMAC check passes, and forwards it as the tenant identity to the app's handler: [4](#0-3) 

**Broken binding**: the gem implicitly claims `hmac_valid(body) == request_is_authentically_from(shop)`, but the actual invariant enforced is only `hmac_valid(body)`; `shop` is never part of the signed bytes. Since the app's `api_secret_key` is shared across every shop that installs the app, any attacker who can install the app on their own store receives genuine, validly-signed webhook deliveries. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` passes `request.shop` (now the victim's domain) straight to the handler as if Shopify itself vouched for that tenant.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged user who merely installs the app on their own shop (no `api_secret_key`, no stolen credentials, no privileged account) can cause the host application's webhook handler to process attacker-controlled webhook bodies under an arbitrary victim shop's identity. Depending on how the host app uses `WebhookMetadata#shop` (e.g., looking up the victim's session/access token, writing to the victim's records, or triggering shop-scoped side effects), this can lead to cross-tenant data corruption or cross-tenant actions being taken against a shop the attacker doesn't control.

### Likelihood Explanation
Likelihood is high for any attacker willing to install the app (a normal, unprivileged flow for any public/embedded app) — they obtain real, validly HMAC-signed webhook bodies for their own store without needing the app's secret, and can freely manipulate the shop header on replay since it sits entirely outside the signed material.

### Recommendation
Bind the shop identity into the verified material, e.g., include the `shop` header value in the HMAC signable string (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop`), or otherwise cryptographically bind the `shop-domain` header to the payload before trusting `Request#shop` in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a genuine webhook: body `{"foo":"bar"}`, header `x-shopify-hmac-sha256: <valid-hmac-of-body>`, header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged header; `Utils::HmacValidator.validate` recomputes the HMAC over the body only and it matches — validation passes.
4. `Webhooks::Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to treat attacker-controlled data as an authentic webhook from the victim shop.

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
