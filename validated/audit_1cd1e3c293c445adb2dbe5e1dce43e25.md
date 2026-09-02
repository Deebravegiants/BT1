### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates the webhook HMAC over the raw request body only, but the `shop` (tenant identifier) that is handed to the app's webhook handler comes from an HTTP header that is *not* included in the signed payload. Any user who can get the app installed on their own store (an ordinary, unprivileged action) can capture a validly-HMAC-signed webhook body from their own shop and replay it to the app's webhook endpoint with the `shop-domain` header changed to a victim shop, and the HMAC check will still pass.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` verifies a request by recomputing an HMAC over `to_signable_string` and comparing it to the `hmac` value [1](#0-0) .

For webhook requests, `Request#to_signable_string` returns **only the raw body** (`@raw_body`), while `Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, and `Request#hmac` is read from the `shopify-hmac-sha256` header [2](#0-1) . Neither the shop domain header nor the topic/webhook-id headers are part of the signed string — only the body bytes are covered by the HMAC.

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the application's handler:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no further verification [4](#0-3) .

The identity binding that should hold is:
`shop_header == shop_bound_by_HMAC`

but in this implementation:
`shop_header != any field covered by to_signable_string`

Since Shopify signs webhooks per-app using the app's shared `client_secret` (the same secret is used for every shop that installs the app), a body captured from a legitimate webhook delivered to *shop A* carries a valid HMAC for that exact body regardless of which shop header accompanies it. Because the header is excluded from the signed data, an attacker who owns shop A (an ordinary, unprivileged merchant able to install the app) can:
1. Trigger a real event on their own shop A and capture the resulting webhook body + valid `x-shopify-hmac-sha256` value.
2. Replay the identical body/HMAC pair to the app's public webhook endpoint, substituting `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` passes (it only checks the body), and `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"`, causing the host application to process/act on data under the wrong tenant's identity.

### Impact Explanation
This breaks the tenant isolation the HMAC is supposed to guarantee: any host application built on this gem that trusts `WebhookMetadata#shop` (as the documented usage pattern implies, since it's the only shop identifier provided by the library for webhook processing) can be made to attribute attacker-controlled webhook bodies to an arbitrary victim shop. Depending on how the host app uses this shop value (looking up sessions/access tokens, updating per-shop records, driving billing/state logic keyed by shop), this enables cross-tenant data confusion/access — matching the Critical "cross-tenant access" impact category. No `api_secret_key`, access token, or privileged account is required; the attacker only needs their own (unprivileged) shop install.

### Likelihood Explanation
Likelihood is moderate-to-high: obtaining a shop install of a target app is trivial for any internet user (this is the ordinary app-installation flow), capturing outbound webhook bodies/HMACs sent to the app's own endpoint requires only observing normal traffic to one's own webhook receiver (or a MITM-free capture via browser/dev tools proxy of one's own webhook consumer), and replaying an HTTP POST with a modified header is trivial. The gem provides no protection against this because the shop identity is architecturally excluded from the signed payload.

### Recommendation
Bind the shop identity to the signature verification, e.g. include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signable string used for webhook HMAC validation, or require the host application to cross-check `request.shop` against the specific shop session/webhook subscription expected for that endpoint before trusting it. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key without additional verification (e.g. matching it against the store's registered webhook subscription obtained via the Admin API for that specific session).

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com` (unprivileged action available to any user).
2. Trigger any subscribed event (e.g., `orders/create`) so Shopify sends a webhook to the app's endpoint. Capture the exact `raw_body`, and the `x-shopify-hmac-sha256` header value sent along with it.
3. Replay an HTTP POST to the same webhook endpoint with:
   - identical `raw_body`
   - identical `x-shopify-hmac-sha256` header
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (any shop, including one the attacker doesn't control)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `@raw_body` against the HMAC — the swapped shop header is never validated.
5. The registered handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, so any host-app logic keyed off `data.shop` operates as though this event legitimately originated from the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
