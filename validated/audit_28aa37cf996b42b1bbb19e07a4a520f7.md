### Title
Webhook `shop` field trusted for tenant identification without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, then passes the *unauthenticated* `x-shopify-shop-domain` header value straight into the `WebhookMetadata` struct that is handed to the host app's handler. The shop-domain field is never covered by the HMAC signature, so the binding "shop acted on == shop covered by HMAC" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, completely independent of the signed payload: [2](#0-1) 

`Registry.process` validates only the HMAC (which covers the body) and then immediately builds `WebhookMetadata` using `request.shop` taken from the header, with no cross-check that the shop is bound to the signed content: [3](#0-2) 

`HmacValidator.validate` computes the signature only from `verifiable_query.to_signable_string` (the raw body) and the app's single, shop-independent `api_secret_key`: [4](#0-3) 

Because the `api_secret_key` is identical for every shop that installs the app, and the HMAC is computed only over the body (not the shop domain), any two requests with the same body produce the same valid HMAC signature regardless of which shop they claim to originate from. An attacker who operates their own shop installation of the target app receives genuine webhooks (with a body/HMAC pair signed by the app's real secret). For webhook topics whose body is constant or attacker-influenceable (e.g. topics with an effectively empty/fixed JSON body, as shown in the test fixtures using `"{}"`), the attacker can capture that valid `(body, hmac)` pair and replay it against the same webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` will accept it (body/HMAC still match), and `Registry.process` will hand the host application a `WebhookMetadata` claiming the event happened for the victim shop.

This breaks the identity binding: `shop asserted to host app == shop cryptographically bound by HMAC`. The gem provides no mechanism to bind the header-derived tenant identity to the signature, and the host application has no documented way to get an authenticated shop value from this gem's webhook API — `request.shop` is the only value exposed.

### Impact Explanation
This allows cross-tenant confusion/spoofing: an app that keys off `WebhookMetadata#shop` (e.g., to delete a shop's data on `shop/redact` or `app/uninstalled`, or to update per-shop state) can be tricked into applying an event intended for the attacker's own shop to a different, victim shop, without the attacker possessing that shop's credentials. This matches the "Critical - cross-tenant access" category since it is a genuine crossing of the tenant boundary using only the attacker's own legitimate (non-privileged, non-secret) access to the shared app.

### Likelihood Explanation
Exploitability depends on: (1) the attacker having a working installation of the target app on their own shop (unprivileged — any merchant can install a public app), (2) a webhook topic existing whose signed body is constant/predictable across shops (demonstrated in this codebase's own tests, which sign the literal body `"{}"`), and (3) the host app trusting `WebhookMetadata#shop` for per-tenant actions, which is the gem's documented/intended usage pattern (see `docs`/tests passing `data.shop` straight from the request). No secret, TLS interception, or privileged access is required — only the ability to receive one's own genuine webhook and replay it with a different header.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed payload verification, or otherwise cryptographically bind the `shop` value to the validated body (e.g., verify the `shop` header against a known/expected shop for the given webhook subscription) before constructing `WebhookMetadata`. At minimum, document that `request.shop` is unauthenticated and must not be used as a tenant boundary unless corroborated by another authenticated source (e.g., a stored webhook-id-to-shop mapping obtained via authenticated GraphQL registration).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, which shares the same `api_secret_key` with every other install.
2. Attacker triggers a webhook topic whose payload body is constant/predictable (e.g. an empty-body-style event), and records the genuine `x-shopify-hmac-sha256` value Shopify sent along with that body — this HMAC was computed with the real secret, so it validates.
3. Attacker POSTs to the app's webhook endpoint with:
   - the same raw body,
   - the same (valid) `x-shopify-hmac-sha256`,
   - `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) succeeds because it only checks the body's signature.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and invokes the host handler, which performs whatever shop-scoped action the topic implies against the victim tenant.

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
