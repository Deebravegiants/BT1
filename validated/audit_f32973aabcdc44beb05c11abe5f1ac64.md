### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The gem's webhook signature validation only authenticates the raw request body. The `shop` field that downstream handlers use to attribute a webhook to a specific merchant/tenant is read from a separate HTTP header that is never included in the HMAC-signed content, so it can be swapped without invalidating the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop` by reading the `shopify-shop-domain` / `x-shopify-shop-domain` header directly, independent of the HMAC: [1](#0-0) 

The value actually covered by the signature is only the raw body, via `to_signable_string`: [2](#0-1) 

`HmacValidator.validate` computes/verifies the signature strictly over `verifiable_query.to_signable_string` (the body), never the shop header: [3](#0-2) 

`Registry.process` trusts the HMAC check as proof of authenticity for the whole request, then forwards `request.shop` (the unauthenticated header) straight to the app's handler as the tenant identifier: [4](#0-3) 

The intended binding should be:
`shop header value == shop cryptographically bound inside the HMAC-signed payload`

What is actually enforced is:
`HMAC(raw_body, secret) == received_signature`, with `shop` excluded entirely from `raw_body`'s coverage as far as the validator is concerned (the body only carries the shop implicitly if the payload's JSON happens to include a shop id, which the gem never checks against the header).

Because every shop installed for a given app shares the same `api_secret_key`, any tenant that has legitimately installed the app can obtain a validly-signed webhook (body + HMAC) for their own store, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for an arbitrary victim shop domain. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` calls the handler with `shop: <attacker-chosen victim shop>`.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to guarantee: an attacker who legitimately holds one shop's valid webhook material can inject data attributed to any other shop into the host application's webhook handler, without ever holding a token or secret belonging to the victim tenant. This is a cross-tenant identity-binding bypass — the app's business logic (order processing, inventory sync, data deletion callbacks, GDPR/mandatory webhooks, etc.) may execute against the wrong tenant's records because it trusts the unauthenticated `shop` field passed through from `ShopifyAPI::Webhooks::Request#shop`.

### Likelihood Explanation
Any unprivileged internet user can install the app on their own (attacker-controlled) shop through normal OAuth, causing Shopify to deliver a genuinely signed webhook to the app's public endpoint. Capturing that raw body + `hmac-sha256` header pair requires no special access, and replaying it with a modified shop-domain header is a simple HTTP request — no TLS interception, leaked secrets, or privileged account is required.

### Recommendation
Bind the shop identity to the signed payload before trusting it: either (a) require the app's own handler/registry to compare the header-derived `shop` against a shop value embedded in the signed JSON body (rejecting mismatches), or (b) change `to_signable_string` in `lib/shopify_api/webhooks/request.rb` to include the `shop`, `topic`, and `webhook-id` headers in the HMAC-covered content so any tampering of those headers invalidates the signature, matching how `Auth::Oauth::AuthQuery#to_signable_string` already binds `shop` into its OAuth HMAC.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` (normal OAuth flow, no special privilege).
2. Shopify sends a legitimately-signed webhook (e.g. `orders/create`) to the app's webhook endpoint: body `B`, header `X-Shopify-Hmac-Sha256: H = HMAC(B, api_secret_key)`, header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same `B` and `H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC(B, api_secret_key)`, which equals `H` — validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:26-31`), since only `B` is checked.
5. `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker's own body data (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host application to process attacker-supplied data under the victim tenant's identity.

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
