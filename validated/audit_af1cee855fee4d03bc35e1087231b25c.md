### Title
Webhook `shop`, `topic`, and `webhook_id` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content as only the raw request body, while the shop-identifying metadata (`shop`, `topic`, `webhook_id`, `api_version`) is read directly from unauthenticated HTTP headers and passed to the handler unverified.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the HMAC solely against that signable string using `Context.api_secret_key` [2](#0-1) . Meanwhile, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers with no cryptographic binding to the signed body [3](#0-2) .

`Registry.process` validates only the HMAC-over-body, then constructs `WebhookMetadata` directly from these unauthenticated header values and dispatches it to the app's handler: [4](#0-3)  (see `raise ... unless Utils::HmacValidator.validate(request)` followed by `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))`).

The equality this breaks: `shop header authenticated by HMAC` should equal `shop the raw_body/HMAC pair was actually generated for`, but the HMAC only proves "this body was signed with our secret at some point" — it says nothing about which shop or topic that signature was originally issued for.

### Impact Explanation
Because HMAC-SHA256 is deterministic (`OpenSSL::HMAC.hexdigest(secret, raw_body)`), any `{raw_body, hmac}` pair remains valid regardless of what `shop-domain`, `topic`, or `webhook-id` header accompanies it. An unprivileged internet user who installs the target app on their own (attacker-controlled) shop will receive genuine Shopify-signed webhook deliveries for their own store — i.e., legitimate `{raw_body, hmac}` pairs signed with the real `api_secret_key`. The attacker can then replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to name a victim shop. `HmacValidator.validate` will still pass (only the body is checked), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the spoofed victim shop/topic. Any app logic that trusts `data.shop`/`data.topic` to key privileged, tenant-scoped operations (e.g., writing data under the victim's stored session/access token, triggering redaction actions, updating per-shop state) is exposed to cross-tenant confusion — satisfying the "cross-tenant access" Critical impact category, without needing the app's `client_secret`, any access token, or privileged account access.

### Likelihood Explanation
Likelihood is meaningful but constrained: the attacker needs at least one legitimate `{raw_body, hmac}` pair, which any developer can trivially obtain by installing the app on a free/dev shop of their own and capturing a real webhook delivery (no special access required — this is normal, unprivileged app installation). Constructing a useful attack additionally requires either finding a topic/body combination that is shop-agnostic in its effect, or where the handler logic keys solely off the `shop` field for a body whose content the attacker also controls to some degree (e.g., via triggering actions on their own store that produce attacker-influenced webhook bodies). This makes the finding a genuine gap in the gem's binding guarantees, though full exploitability depends on how a given host application's webhook handler consumes `data.shop`/`data.topic`.

### Recommendation
Bind the shop/topic/webhook identity to the signed payload rather than trusting raw headers:
- Compute the HMAC over a canonical representation that includes `shop`, `topic`, and `webhook_id` in addition to the raw body, or
- Require callers to independently verify `request.shop` against the shop associated with the session/registration that was expected to receive the webhook before acting on it, and document this requirement clearly in `Registry.process`/`WebhookMetadata`, and
- Consider rejecting cross-topic/cross-shop replay by tracking `webhook_id` uniqueness (idempotency) in addition to shop verification.

### Proof of Concept
1. Attacker installs the target public Shopify app on their own shop `attacker-shop.myshopify.com`, subscribing to a topic that the app handles (e.g. `orders/create`).
2. Attacker triggers the real webhook delivery (e.g., creates an order on their own store) and captures the raw POST body and the `x-shopify-hmac-sha256` header — both legitimately signed by Shopify using the real `api_secret_key` for `attacker-shop.myshopify.com`.
3. Attacker resends this exact body and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and/or changes `x-shopify-webhook-id`).
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` accepts the forged headers (`Request#shop`/`#topic` just echo header values) [5](#0-4) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [6](#0-5) .
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload was never actually generated for that shop, and performs whatever tenant-scoped action the app implements keyed on that `shop` value.

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
