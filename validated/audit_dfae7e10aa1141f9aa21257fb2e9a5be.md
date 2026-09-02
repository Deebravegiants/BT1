### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw HTTP body via HMAC, while the `shop` (tenant) value used by the application is read from the `X-Shopify-Shop-Domain` header, which is never included in the signed content. An unprivileged user who can obtain one legitimately-signed webhook delivery (e.g., by installing the app on their own store) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, and the gem will accept it as valid and hand the attacker-chosen shop identity to the host app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only the raw request body: [1](#0-0) 

`Request#shop`, which becomes the tenant identity forwarded to the app, is read directly from an HTTP header that is not part of the signed content: [2](#0-1) 

`Registry.process` verifies the request solely via `Utils::HmacValidator.validate(request)`, which — per `HmacValidator#validate_signature` — computes/compares the HMAC over `verifiable_query.to_signable_string` (i.e. body only), then immediately trusts `request.shop` and forwards it to the registered handler: [3](#0-2) [4](#0-3) 

The binding the gem is supposed to enforce is:
`shop identity trusted by handler == shop identity authenticated by HMAC`

Because the HMAC only covers `@raw_body`, this equality does not hold — the `shop-domain` header can be swapped for any value without invalidating the signature, breaking the binding between "bytes verified" and "identity acted on."

### Impact Explanation
This is a cross-tenant identity confusion issue: a webhook payload cryptographically proven to originate from Shopify (for *some* shop) can be relabeled as originating from a *different, victim* shop. Any host application logic that keys off `WebhookMetadata#shop` (e.g., tenant-scoped session lookup, data deletion via mandatory `shop/redact` topic, per-shop caching/state updates) can be triggered under the wrong tenant's identity, meeting the "cross-tenant access" criterion for High impact.

### Likelihood Explanation
The attacker only needs the ability to install the target app on a store they control (a normal, unprivileged action available to any merchant/developer), capture one legitimate webhook delivery (body + `X-Shopify-Hmac-Sha256` header) sent to their own endpoint, and replay it to the app's webhook endpoint with a modified `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header. No access token, `client_secret`, or privileged credentials of the victim are required.

### Recommendation
Bind the `shop` value to the signed content rather than trusting an unauthenticated header:
- Prefer deriving tenant identity from data inside the verified body (most Shopify webhook payloads and topics carry shop-scoped data/IDs) instead of, or in addition to, the header, and cross-check it against the header.
- Alternatively, include the shop domain (and other trust-sensitive headers such as `webhook-id`, `api-version`, `topic`) in the HMAC signable string construction if using a custom verification scheme, or verify webhook uniqueness/replay via `webhook_id` tracking combined with a signed shop claim.
- At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant-scoping key by host applications, and provide a verified alternative.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`).
2. Shopify sends the app's webhook endpoint a request with body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC over `B` using the app's `api_secret_key`), and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this request (they control the receiving endpoint or a proxy in front of it) and replays it to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but setting `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only — validation succeeds because `B` and `H` are unchanged.
5. `request.shop` returns `"victim-shop.myshopify.com"`, and the handler in `Registry.process` receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-supplied data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
