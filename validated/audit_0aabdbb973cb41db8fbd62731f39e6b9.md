### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant-identity spoofing on otherwise-valid webhook deliveries - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , while `Request#shop` is read directly from the `X-Shopify-Shop-Domain` header [2](#0-1) . `Utils::HmacValidator.validate` only verifies `hmac` against `to_signable_string`, i.e. the body bytes [3](#0-2) . The shop-domain header is never included in the signed bytes, so a request whose body/HMAC pair is legitimate for shop A can be delivered with a forged `X-Shopify-Shop-Domain` header claiming to be shop B, and it will still pass HMAC validation.

### Finding Description
`Registry.process` gates dispatch solely on the body HMAC: `raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)` [4](#0-3) . Immediately after, it forwards `shop: request.shop` — the unauthenticated header value — into `WebhookMetadata` passed to the app's registered handler [5](#0-4) .

The binding that should hold is:
`shop-domain used by the handler for tenant scoping == shop-domain covered by the HMAC signature`

But the actual binding is:
`hmac validates only(raw_body) != shop header consumed by handler`

Since the `VerifiableQuery` interface only requires `hmac` and `to_signable_string` [6](#0-5) , and `Request` implements `to_signable_string` as `@raw_body` alone [1](#0-0) , nothing in this gem cryptographically ties the `shop` field to the signature. Any host app that relies on the gem's `Registry.process`/`request.shop` to determine which tenant a webhook body belongs to (a documented, intended usage per `docs/usage/webhooks.md` and `WebhookMetadata`) is exposed: an attacker who can capture or replay any single valid `(raw_body, hmac)` pair (e.g., from their own shop, from a public/test webhook, or from a leaked delivery log) can resubmit it with an arbitrary `X-Shopify-Shop-Domain` value and have it accepted as belonging to a different tenant.

### Impact Explanation
This is a cross-tenant identity-binding break: the merchant/tenant identifier consumed by the app (`request.shop` / `WebhookMetadata#shop`) is not authenticated by the signature that gates the request. Depending on how the host app uses `shop` from `WebhookMetadata` (e.g., to look up per-shop data, gate GDPR redaction requests such as `shop/redact`, or attribute webhook events to a store), this enables cross-tenant data confusion/injection using only a single previously-observed valid webhook payload — no access token, secret, or privileged account required, satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires the attacker to have obtained one legitimate `(raw_body, hmac)` pair for any shop (their own store's webhooks are sufficient, since the attacker controls their own tenant and can trigger arbitrary webhook events like `orders/create` on their own store), then forge the HTTP headers of a new request to the app's webhook endpoint. This is trivial for anyone who can operate their own Shopify development store or has visibility into any single delivered webhook, so likelihood is high for any host app whose webhook endpoint is internet-reachable — an unprivileged-internet-user analog.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically tie the `shop-domain` header to the payload before trusting it. Options:
- Extend `to_signable_string` to also validate shop domain against the source, e.g., include the shop-domain header in the value that is HMAC-verified (this would require Shopify's webhook signing to also cover the header — since it currently doesn't, the safer mitigation is a compensating control).
- Compensating control the gem should implement/document as mandatory: require callers to independently verify that `request.shop` corresponds to a shop that has confirmed_installed app registration/session in the app's own storage before trusting `WebhookMetadata#shop`, and make this explicit/enforced in `Registry.process` rather than leaving it entirely to host apps.
- At minimum, document in `docs/usage/webhooks.md` and in `WebhookMetadata` that `shop` is derived from an unauthenticated header and must not be trusted for authorization decisions without an independent session/shop lookup.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the raw POST body and the valid `X-Shopify-Hmac-Sha256` header Shopify computed for that body.
2. Attacker resends that exact body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`@raw_body`) only [1](#0-0)  — validation succeeds because the body was untouched.
4. `request.shop` returns `"victim-shop.myshopify.com"` from the forged header [2](#0-1) , which is passed straight into the app's handler via `WebhookMetadata` [5](#0-4) , causing the app to process attacker-controlled webhook content under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```

**File:** lib/shopify_api/utils/verifiable_query.rb (L6-16)
```ruby
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
```
