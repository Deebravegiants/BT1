### Title
Webhook Shop/Topic/Webhook-ID Headers Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — are trusted and forwarded to the application's webhook handler without being part of the HMAC-protected data. This breaks the intended binding "HMAC-authenticated bytes == the shop this webhook is attributed to."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from caller-supplied headers with no cryptographic tie to the signature: [2](#0-1) .

`Registry.process` validates the HMAC of only the body and then immediately trusts the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` to build the `WebhookMetadata` passed to the application-supplied handler: [3](#0-2) .

This means the identity binding actually enforced is:
`HMAC(secret, raw_body) == received_hmac`

but the binding that matters for tenant attribution —
`shop_header == shop_that_shopify_actually_sent_this_webhook_for`

— is never checked. Any attacker who can obtain **one** genuine `(raw_body, hmac)` pair signed with the developer's `api_secret_key` (trivially available to them if they install the app on their own store, since they receive real webhooks for their own shop) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header pointing at a victim shop. `HmacValidator.validate` still succeeds because it only hashes `raw_body`: [4](#0-3) .

### Impact Explanation
Because the forged headers are handed unchanged to the host application's handler as the authoritative shop/topic/webhook-id, an attacker fully controlling their own installed instance can trigger tenant-scoped business logic (e.g., `app/uninstalled`, GDPR redact/request, order/customer create handlers) attributed to a different, victim shop. Any downstream logic that keys off `WebhookMetadata#shop` to select or mutate per-tenant state is exposed to cross-tenant interference — this satisfies the "cross-tenant access" High-severity bar.

### Likelihood Explanation
Exploitation requires only: (1) the attacker installs the app themselves (or otherwise observes one legitimate webhook delivery) to obtain a valid `(body, hmac)` pair, and (2) they send a forged HTTP request to the app's public webhook endpoint with a substituted shop-domain header and the captured body/HMAC. No access token, `client_secret`, or privileged credentials are needed — only unprivileged internet access to the merchant's public webhook URL, matching the "unprivileged-internet-user" analog class this scan targets.

### Recommendation
Include the shop domain, topic, and webhook id in the signed/verified material (or otherwise cryptographically bind them, e.g. verify `shop` against a known-installed-shop allowlist prior to trusting it), rather than passing header-derived values straight through to `WebhookMetadata` once only the body's HMAC has been checked.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a real webhook delivery, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's real `api_secret_key`).
2. Replay to the app's webhook endpoint:
```
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
X-Shopify-Webhook-Id: <any>

B
```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds: [5](#0-4) .
4. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., webhook_id: ..., api_version: ...)` — attributed to a shop the attacker does not own: [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
