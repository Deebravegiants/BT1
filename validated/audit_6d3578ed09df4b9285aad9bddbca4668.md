### Title
Webhook shop attribution is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the `hmac-sha256` header against the raw request body, then unconditionally trusts the separate `shop-domain` header to identify which merchant/tenant the payload belongs to. Because the shop identity is never part of the signed content, an attacker who can produce a validly-signed body (e.g., a real merchant replaying their own legitimate webhook payload) can attach an arbitrary `shop-domain` header and have the app process the request as if it originated from a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`hmac` is computed from the `hmac-sha256` header, and `to_signable_string` returns only `@raw_body`: [2](#0-1) 

`shop` is read from a completely separate, unsigned header: [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string` (the raw body) and compares it with the received signature: [4](#0-3) 

`Registry.process` validates only this body HMAC, then immediately forwards `request.shop` — the unauthenticated header — to the app's webhook handler as the tenant identity: [5](#0-4) 

The binding that should hold is: `shop-domain header == shop covered by hmac-sha256`. In reality the equality is broken — the HMAC only proves `raw_body` integrity; `shop` travels out-of-band and unauthenticated. Any request whose body produces a valid HMAC (using the app's single, shared `api_secret_key` across all installed shops) can carry any `shop-domain` value, and `Registry.process` will hand that spoofed shop identity to `WebhookHandler#handle` via `WebhookMetadata`.

### Impact Explanation
This breaks the shop/tenant binding a host application relies on to route webhook data (e.g., to decide which merchant's database record to update, which session/store to act on). An unprivileged actor — a merchant who has installed the app and thus legitimately receives webhooks signed with the app's shared secret for their own store — can capture one of their own valid webhook deliveries and resend it to the app's webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header changed to a victim shop's domain. Because HMAC validation only checks body integrity and never checks that the signature is scoped to the claimed shop, the app will process attacker-controlled data as though it came from the victim shop, resulting in cross-tenant data injection/corruption in webhook-driven business logic.

### Likelihood Explanation
The `api_secret_key` used for webhook HMACs in a public multi-tenant app is shared across all installations of the app (not per-shop), so any merchant who installs the app can generate/observe validly-signed webhook bodies for their own shop and simply swap the shop header before replaying it — no access to the app's `client_secret`, tokens, or the target shop's data is required. This requires no privileged access beyond that of any ordinary merchant installing the app.

### Recommendation
Bind the `shop` value into the material that is actually verified — either include it in the signable payload the app checks (e.g., verify that the resolved shop matches a shop the app has an active session/installation for before trusting `data.shop`), or otherwise cryptographically tie the shop header to the signed body so `Registry.process`/`WebhookHandler#handle` cannot be fed an unauthenticated shop identity.

### Proof of Concept
1. Install the app on shop A (unprivileged, self-service).
2. Receive a genuine webhook delivery from Shopify for shop A: raw body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: shop-a.myshopify.com`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Replay the exact same request to the app's webhook endpoint, but change only `x-shopify-shop-domain` to `shop-b.myshopify.com` (victim shop). `H` is still valid because `to_signable_string` (see `lib/shopify_api/webhooks/request.rb:35-38`) never includes the shop header.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) passes `Utils::HmacValidator.validate` and invokes the app's handler with `shop: "shop-b.myshopify.com"` and attacker-controlled body `B`, even though the request never touched shop B's data at Shopify.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
