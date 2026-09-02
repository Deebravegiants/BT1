## Title
Webhook `shop-domain` header is not covered by HMAC verification, enabling cross-tenant webhook shop-spoofing — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content solely from the raw HTTP body, while the `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read directly from unauthenticated HTTP headers. `Registry.process` verifies the HMAC over the body only, then forwards the header-derived `shop` value to the app's webhook handler as the authoritative tenant identifier. Because the HMAC never binds the `shop-domain` header to the signed payload, any request bearing a previously-valid `(body, hmac)` pair can be replayed with an arbitrary `shop-domain` header and will pass HMAC validation, causing the receiving application to process the webhook under an attacker-chosen shop.

### Finding Description
The equality that should hold is:
`shop value cryptographically bound by HMAC == shop value delivered to the handler`

In `lib/shopify_api/webhooks/request.rb`: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body` — the `shop`, `topic`, `webhook_id`, and `api_version` accessors read straight from HTTP headers that are never included in the signed content.

`HmacValidator.validate` computes/compares the HMAC strictly over `to_signable_string`: [3](#0-2) 

`Registry.process` verifies only this body HMAC, then constructs `WebhookMetadata` using the unauthenticated `request.shop` header value and dispatches it to the app's handler as the tenant identity: [4](#0-3) 

Since the `shop-domain` header sits entirely outside the HMAC-covered bytes, the two sides of the binding — "bytes verified" vs. "bytes/headers acted on" — diverge: the gem verifies only the body, but acts on (and hands to the app) a header value that carries zero cryptographic guarantee of authenticity or of belonging to that particular body.

### Impact Explanation
Any actor who has legitimately received one authentic webhook (e.g., by installing the app on their own development/trial store, which is available to any unprivileged internet user under normal app-install flows) obtains a valid `(raw_body, hmac)` pair signed with the app's `client_secret`. They can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header (e.g., a targeted victim merchant's domain). `Registry.process` will accept the HMAC as valid and invoke the merchant's webhook handler with `shop` set to the victim's domain and attacker-controlled body content, achieving cross-tenant data injection/confusion in any host application that trusts `WebhookMetadata#shop` (returned by this gem) as the authoritative tenant key — which is the gem's documented usage pattern for webhook processing.

### Likelihood Explanation
Likelihood is meaningful but not universal: it requires the attacker to first obtain one valid signed webhook body (trivial via app installation on any shop they control, since Shopify signs webhooks with the app's single shared `client_secret` regardless of shop) and to be able to deliver an HTTP request directly to the app's webhook endpoint with custom headers (feasible since Shopify webhook endpoints are plain public HTTP(S) endpoints, not restricted to Shopify's IP ranges by this gem). No access token, session, or knowledge of `client_secret` is required.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) header into the value that is HMAC-verified, or independently authenticate the shop before trusting it — e.g., require the caller to look up an existing offline session/access token for `request.shop` before processing, and reject webhooks for shops with no established session. At minimum, document prominently that `WebhookMetadata#shop` is not cryptographically authenticated by `HmacValidator.validate` and must not be used as a sole tenant-identity check by consuming applications.

### Proof of Concept
1. Install the target app (or use a trial/dev store) so Shopify delivers one legitimate webhook to the app's callback URL, e.g.:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: ...
   Body: {"id": 1, "note": "hello"}
   ```
2. Capture `Body` and `x-shopify-hmac-sha256` unchanged.
3. Replay the same request but change `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` still succeeds because it only hashes `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`).
5. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) dispatches `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` to the app's handler, which processes attacker-supplied data under the victim's tenant identity.

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
