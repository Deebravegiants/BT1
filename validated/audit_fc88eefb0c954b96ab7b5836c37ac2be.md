This confirms the finding. The gem's own documentation explicitly tells developers to key their business logic (`shop_domain`, tenant identification) off `data.shop` from `WebhookMetadata`, but that field is never covered by the HMAC.

### Title
Webhook `shop`, `topic`, `api_version`, and `webhook_id` Metadata Are Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity by calling `Utils::HmacValidator.validate(request)`, which computes an HMAC over `request.to_signable_string`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw request body [1](#0-0) . However, `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` are all read directly from unauthenticated HTTP headers [2](#0-1)  and are then passed straight into `WebhookMetadata` and handed to the host application's handler after only the body-HMAC check succeeds [3](#0-2) . This is the same bug class as the reported overflow analog: a value that is *acted on* (here, the `shop` field used for tenant identification) is not *covered* by the integrity check that is supposed to bind the whole message together (the HMAC).

### Finding Description
`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it via `OpenSSL.secure_compare` against the `hmac` header [4](#0-3) . For webhook requests, `to_signable_string` is defined as simply `@raw_body` [1](#0-0) , meaning the HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) are entirely excluded from what is authenticated. The intended binding should be: `shop header == shop that produced this HMAC-signed body`. Instead, the gem verifies "body bytes == body bytes Shopify signed" while independently trusting "shop header == whatever the request claims," breaking the equality between the shop the payload was cryptographically bound to and the shop actually used by the application. Because Shopify signs webhook bodies per-shop with the app's shared `client_secret`, and the gem's own documentation instructs developers to key tenant-specific logic off `data.shop` [5](#0-4) , any attacker who can obtain one valid (body, hmac) pair sent by Shopify to the app's webhook endpoint (e.g., from their own store subscribing the app, or from any webhook their tenant naturally triggers) can replay the exact same body/HMAC pair while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to point at a different, victim shop. `HmacValidator.validate` still returns `true` because only the body is checked, and `Registry.process` proceeds to invoke the handler with attacker-chosen `WebhookMetadata#shop` [3](#0-2) .

### Impact Explanation
This is a cross-tenant confusion vector at the identity-binding layer of the gem: the application layer built on top of `shopify_api` (following the gem's documented pattern) will process webhook events attributed to a shop other than the one that actually produced the signed payload. Depending on how the host app uses `data.shop` (e.g., to look up a stored session/access token for a tenant, to route job processing, or to write into per-tenant state), this can result in tenant B's stored data being updated/corrupted based on tenant A's webhook content, or actions being taken against tenant B's session using data that was never actually sent by Shopify for tenant B. This matches the Critical impact class of cross-tenant access, since the binding between the authenticated payload and the shop identifier is broken entirely within this gem's verification logic.

### Likelihood Explanation
Exploitation requires only network access to the app's public webhook endpoint plus possession of one legitimately Shopify-signed `(raw_body, hmac)` pair — which any unprivileged merchant/developer installing the app obtains automatically the first time any subscribed webhook topic fires for their own shop. No access to `api_secret_key`, session tokens, or victim credentials is required; the attacker only replays intercepted/observed bytes with a modified header.

### Recommendation
Include the `shop`, `topic`, `webhook_id`, and `api_version` header values in the signable string used for HMAC computation (or otherwise cryptographically bind them, e.g., by including the shop domain that Shopify associates with the webhook subscription and verifying it against the session/store the app expects), so that any tampering with these headers invalidates the HMAC. At minimum, the gem should document/enforce that the `shop` header must be independently corroborated against a known, previously-established tenant record before being trusted for identity-sensitive operations.

### Proof of Concept
1. App developer installs the app on Shop A and subscribes to a webhook topic (e.g., `orders/create`). Shopify sends `POST /callback` with body `B` and header `x-shopify-hmac-sha256: H`, computed as `HMAC-SHA256(client_secret, B)`, plus `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker (who is Shop A's own merchant/dev, or has otherwise observed this request, e.g. via logs, a proxy, or replay from their own store) captures `(B, H)`.
3. Attacker resends `POST /callback` with the identical body `B` and identical `x-shopify-hmac-sha256: H`, but changes `x-shopify-shop-domain` to `shop-b.myshopify.com` (a different tenant of the same app).
4. `HmacValidator.validate` recomputes the HMAC over `B` only [1](#0-0)  — it still matches `H`, so validation passes.
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied `shop-b.myshopify.com` [6](#0-5)  and invokes the host app's handler as if this data legitimately came from Shop B.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
