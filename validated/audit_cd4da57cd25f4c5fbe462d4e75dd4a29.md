## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw HTTP body with HMAC-SHA256, while the `shop` (and `topic`/`webhook_id`) values used for tenant identification are read straight from unauthenticated HTTP headers. `Registry.process` validates the HMAC against the body only, then hands the *unverified* header-derived `shop` value to the handler as the tenant identity. Any caller who possesses one genuinely-signed webhook (body + HMAC) — trivially obtainable by installing the app on their own shop — can splice the same body/HMAC pair with an arbitrary `X-Shopify-Shop-Domain` header and have the app process it as belonging to a different, victim shop.

### Finding Description
The identity binding that should hold is:

`shop authenticated by HMAC == shop the handler acts on`

In `lib/shopify_api/webhooks/request.rb`: [1](#0-0) 
`hmac` is derived from the `hmac-sha256` header, and `shop` is derived independently from the `shop-domain` header — neither is bound to the other.

The signable string used for verification is the raw body only: [2](#0-1) 

`Registry.process` verifies only that string against the HMAC, then forwards the unauthenticated `request.shop` to the handler as the trusted tenant identifier: [3](#0-2) 

Because the `shop-domain` header is outside the signed payload, the equality the app relies on (`hmac_valid(body) → shop_header is trustworthy`) does not hold. A user who legitimately installs the app on their own shop will receive real, correctly-signed webhook deliveries for that shop. They can capture one such request and resend it to the app's webhook endpoint with the `shop-domain` header changed to a victim shop, keeping body and HMAC untouched — `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` still passes because it only checks `verifiable_query.to_signable_string` (the body) against the secret: [4](#0-3) 

This is the same root-cause pattern as the external report: an action (crediting/burning collateral in the DYAD report; here, attributing a webhook event to a tenant) proceeds on data that is not actually covered by the verification step that is supposed to authorize it.

### Impact Explanation
Any host application that uses `WebhookMetadata.shop` (built directly from `request.shop`) to decide which merchant's records to update — the documented, intended usage pattern of this gem — can be made to apply another shop's webhook side effects to a victim tenant, or vice versa. This is a cross-tenant boundary break, satisfying the Critical impact class ("cross-tenant access").

### Likelihood Explanation
Requires only an attacker who can install the app on their own shop (unprivileged internet user) and replay/modify an HTTP header on a request to the app's public webhook endpoint — no `api_secret_key`, access token, or other privileged credential is needed. This is fully within the unprivileged-caller threat model.

### Recommendation
Bind the `shop` (and `topic`/`webhook_id`) values into the HMAC-verified payload, e.g. include them in the signable string (as `AuthQuery` does for OAuth, see `lib/shopify_api/auth/oauth/auth_query.rb` lines 33-43) or otherwise cryptographically bind headers to body before trusting `request.shop` for tenant routing, and document that consuming apps must not treat header-derived `shop` as authenticated unless bound to the signature.

### Proof of Concept
1. Install the app on `attacker.myshopify.com`; trigger any webhook event so Shopify delivers a genuinely HMAC-signed request: headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid>`, body `B`.
2. Capture this request, change only `x-shopify-shop-domain` to `victim.myshopify.com`, leave body `B` and the HMAC header untouched.
3. Replay to the app's webhook endpoint. `Registry.process` → `HmacValidator.validate` recomputes HMAC over `B` only and it matches, so the request is accepted: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and processes the event as if it originated from the victim's store.

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
