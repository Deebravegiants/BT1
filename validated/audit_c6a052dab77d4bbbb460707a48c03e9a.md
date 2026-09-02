## Title
Webhook shop identity not bound by HMAC, allowing cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor sourced from the unauthenticated `X-Shopify-Shop-Domain` HTTP header, while the HMAC signature that `Utils::HmacValidator` verifies covers only the raw request body. `Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler. Because the shop identity is never covered by the signature, an attacker can replay any body+HMAC pair they legitimately possess (e.g., from their own shop's genuine webhook delivery) against the app's public webhook endpoint while substituting an arbitrary `shop-domain` header, and the HMAC check will still pass.

### Finding Description
The signable content for a webhook request is defined as: [1](#0-0) 

which returns only `@raw_body`, not the `shop`, `topic`, or `api-version` headers: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` and compares it against the `hmac` header value: [3](#0-2) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` (the raw header) to construct the metadata delivered to the app's handler: [4](#0-3) 

**Binding broken (equality that should hold but doesn't):**
`bytes covered by HMAC (raw_body)` ≠ `bytes used to establish tenant identity (shop-domain header)`

Before the attack: a genuine Shopify-delivered webhook has `hmac == HMAC(api_secret_key, raw_body)` and `shop-domain` header set correctly by Shopify's infrastructure for that same tenant, so the two happen to agree in the legitimate flow.

After the attacker's request: the attacker (who operates their own store with the app installed) captures a valid `(raw_body, hmac)` pair from a legitimate webhook sent to their own endpoint. They then send a POST directly to the app's public webhook endpoint (there is no other authentication on that endpoint besides this HMAC check) reusing the same `raw_body`/`hmac`, but with the `X-Shopify-Shop-Domain` header set to a victim shop's domain. `Utils::HmacValidator.validate(request)` still returns `true` because it only checks the body bytes, and `Registry.process` passes `shop: request.shop` (now the victim's domain) into the handler.

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler processes attacker-controlled body content while believing it is associated with an arbitrary shop of the attacker's choosing (any shop domain string, not limited to shops the attacker owns). Any handler logic that keys persistence, authorization, or side effects off `WebhookMetadata#shop` (e.g., updating that shop's cached data, revoking access, processing GDPR redaction data, invalidating sessions) can be triggered against a shop the attacker does not own and has no legitimate relationship with, since the "proof" of the sender's identity (the shop header) carries no cryptographic binding to the payload it accompanies.

### Likelihood Explanation
Any internet user can create a free/dev shop, install an app that uses this gem's webhook receiver, and legitimately receive a valid `(raw_body, hmac)` pair for at least one subscribed topic. They can then directly POST to the app's public webhook endpoint (no additional transport-level authentication is provided by this gem) with a forged `shop-domain` header. No merchant credential, access token, or `client_secret` is required — only the ability to receive one genuine webhook for their own installation, which is an unprivileged action.

### Recommendation
Bind the tenant/shop identity into the material that is cryptographically verified before it is trusted, e.g. include `shop`, `topic`, and `api_version` header values in `to_signable_string` (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`, `state`, and other fields into the HMAC-covered string), or otherwise independently authenticate the shop domain (e.g., by cross-checking it against a known/registered shop record) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers any subscribed webhook topic, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent for that delivery.
2. Attacker sends a POST request directly to the app's webhook endpoint (same path the app configured for `ShopifyAPI::Webhooks::Registry`) with:
   - Body: the captured `raw_body` (unmodified)
   - Header `X-Shopify-Hmac-Sha256`: the captured HMAC (unmodified)
   - Header `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic`: the original topic
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` [5](#0-4) , which succeeds because it only checks `raw_body` against the shared secret.
4. `handler.handle` is invoked with `shop: request.shop` equal to `victim-shop.myshopify.com`, even though the payload and signature originated entirely from the attacker's own store [6](#0-5) .

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
