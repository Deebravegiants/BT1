## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely via `Utils::HmacValidator.validate(request)`, but the HMAC signable string for a webhook `Request` is defined as only the raw request body. The `shop` field — read from the `shopify-shop-domain`/`x-shopify-shop-domain` header and passed straight into the handler as the tenant identity — is never part of the signed bytes. This breaks the identity binding `shop authenticated == shop acted upon`: the gem verifies the *body* bytes, but trusts the *shop* header unconditionally, exactly analogous to the `yield` bug where a value (`returned`) is used without validating it against anything authoritative.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived purely from an HTTP header that is not fed into the signable string at all: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` checks only this body-derived HMAC, then forwards the unauthenticated `request.shop` straight to the app's webhook handler as the tenant identity: [4](#0-3) 

Because the app's `client_secret` (hence HMAC key) is shared across all shops/tenants of the app, any party that legitimately receives a validly-signed webhook for their own shop (e.g., a merchant who installed the app) can capture that `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. The replayed request still passes `HmacValidator.validate` because the header is outside the signed scope, yet `Registry.process` and the resulting `WebhookMetadata#shop` will report the attacker-chosen shop instead of the shop that actually produced the signed body.

### Impact Explanation
This is a cross-tenant identity confusion: an app that keys any state, records, or actions off `WebhookMetadata#shop` (as the gem's own webhook contract instructs apps to do) can be made to process data under a victim shop's identity while the payload content actually originated from the attacker's own shop (or vice versa — attacker can inject their own webhook body as if it came from a victim shop). This matches the "cross-tenant access" Critical-impact category, since the trust boundary between tenants is broken purely through this gem's webhook verification API.

### Likelihood Explanation
Any merchant/developer who installs the app (an unprivileged, standard app-install action, not requiring `api_secret_key`, an access token, or social engineering) can capture a real webhook’s raw body + HMAC for their own shop and re-POST it to the app's public webhook endpoint with a modified `shop` header. No secret material or elevated privilege is needed beyond normal app installation, making this practically reachable.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise independently authenticate the shop header (e.g., cross-check it against the shop associated with the session/subscription that registered the webhook) before trusting it in `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted without additional verification.

### Proof of Concept
1. App installs webhook handler via `ShopifyAPI::Webhooks::Registry.add_registration` for topic `orders/create`, delivery `:http`.
2. Attacker owns `attacker-shop.myshopify.com`, which has the app installed; a genuine webhook arrives at the app endpoint with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body>`
   - body: `{"id": 1, ...}`
3. Attacker captures `raw_body` and `x-shopify-hmac-sha256` unchanged, then re-sends the same POST to the app's webhook endpoint but with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `victim-shop.myshopify.com`.
5. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` — still valid — and dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's order data>, ...)`.
6. The app now processes attacker-controlled data under the victim shop's tenant identity, or vice versa, depending on which direction the attacker chooses to spoof.

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
