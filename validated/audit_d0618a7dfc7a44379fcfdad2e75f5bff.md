This confirms the vulnerability. The `shop-domain` header is read directly from unauthenticated request headers and is never part of the HMAC-signed payload.### Title
Webhook Shop-Domain Spoofing via Unauthenticated Header Not Covered by HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value that is handed to app webhook handlers from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body (`to_signable_string` returns `@raw_body`). The shop-domain header is never included in the signed material, so an attacker who can obtain one validly-signed webhook body can replay it with an arbitrary `shop-domain` header and have it accepted as authentic for a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC to `@raw_body` only: [1](#0-0) 

`shop` is read straight from a header, entirely outside the signed data: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then trusts `request.shop` to build `WebhookMetadata`, which is passed directly to the app's handler for tenant-keyed processing (session lookup, data storage, etc.): [3](#0-2) 

Because the same `api_secret_key` is shared across all shops that install a given app, any valid `(raw_body, hmac)` pair obtained from a legitimate webhook delivery for one shop remains cryptographically valid no matter what `shop-domain` header value is attached when the request is replayed to the app's webhook endpoint. The binding the gem should enforce — "the shop the HMAC authenticates equals the shop the app attributes the payload to" — is broken: HMAC authenticates only the bytes of the body, while the identity/tenant field (`shop`) is parsed from unauthenticated bytes (headers).

### Impact Explanation
An attacker who controls a shop that has the vulnerable app installed (an "unprivileged internet user" relative to other merchants) can capture a legitimate webhook body+HMAC pair delivered to their own callback endpoint, then resend that exact body to the app with a forged `X-Shopify-Shop-Domain` (and `X-Shopify-Webhook-Id`/`X-Shopify-Api-Version`) header naming a different, victim shop. `Utils::HmacValidator.validate` will succeed because it only checks the body signature, and the app's `WebhookHandler#handle` will receive `WebhookMetadata` claiming the payload belongs to the victim shop. Any app that uses `data.shop` to key session/token lookups, database writes, or triggers actions against "that shop" will process/attribute attacker-supplied data as belonging to another merchant's tenant — a cross-tenant data injection/corruption primitive.

### Likelihood Explanation
Exploitation only requires: (1) the attacker's own store to have the app installed (self-service, no privileged access needed), and (2) knowledge of the app's public webhook endpoint (documented/predictable). No access token, refresh token, or `client_secret` is required — the attacker leverages a legitimately-issued webhook for their own shop and simply forges the accompanying header when replaying it, which is trivial with any HTTP client.

### Recommendation
Include the shop domain (and any other identity-relevant metadata such as topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` to the verified body before constructing `WebhookMetadata`. At minimum, document that `request.shop` is unauthenticated and must not be used by consuming apps as a trust anchor without independent verification (e.g., cross-checking against a known/expected shop for the delivery channel).

### Proof of Concept
1. App has `api_secret_key = S` shared by all installs.
2. Attacker installs the app on `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(S, B)`, `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker POSTs the same body `B` and the same valid HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` → `Utils::HmacValidator.validate(request)` succeeds (HMAC only covers `B`).
5. `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` is passed to the app's handler, which processes attacker-controlled data as though it came from `victim.myshopify.com`.

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
