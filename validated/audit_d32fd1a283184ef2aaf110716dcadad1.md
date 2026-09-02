### Title
Webhook `shop-domain` Header Not Covered by HMAC Allows Cross-Tenant Shop Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used by the registry to dispatch the webhook to a handler come from unauthenticated HTTP headers. This breaks the intended identity binding: `shop used by handler == shop that produced the signed body`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all read directly from the (attacker-controllable, unauthenticated) HTTP headers with no cryptographic binding to the body: [2](#0-1) .

`HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e., the raw body) against the HMAC header: [3](#0-2) .

`Registry.process` accepts the request once the body-only HMAC checks out, and then dispatches to the handler using the unverified `request.shop`, `request.topic`, and `request.webhook_id`: [4](#0-3) .

Because the app's `client_secret`/`api_secret_key` is shared across every shop installed on the app (it is not per-shop), any merchant that has installed the app receives genuine `(raw_body, hmac)` pairs signed with that same shared secret for their own shop's webhooks. Since `shop-domain`, `topic`, and `webhook_id` headers are never included in the signed bytes, a malicious merchant can capture one of their own genuine webhook deliveries and replay it to the app's webhook endpoint with the `shop-domain` header changed to a victim shop. The HMAC validation in `HmacValidator.validate` still passes (the raw body/HMAC pair is untouched and was legitimately signed by Shopify with the app secret), but `WebhookMetadata.shop` handed to the developer's handler will report the victim's shop domain paired with the attacker's captured body content. The app's own `Registry` and `Request` code, as documented and shipped in this gem, provide no protection against this because the signature-checked bytes (`raw_body`) and the value used for tenant attribution (`shop` header) are decoupled.

Equality that should hold but is broken:
`request.shop` (used to attribute data to a tenant in `WebhookMetadata`) == `shop that actually produced the HMAC-signed raw_body`.
This is exactly the "field acted on but not covered by the HMAC" analog: the tenant-identifying header is acted upon (passed to the handler for shop-scoped processing) without being part of the signed payload.

### Impact Explanation
This is a cross-tenant data confusion vector: an attacker-controlled merchant can cause the host app's webhook handler to process attacker-supplied webhook body data while it is labeled as belonging to a different (victim) shop, since `data.shop` — the field host apps rely on for shop-scoping (per the gem's own documented example: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` in `docs/usage/webhooks.md`) — is not authenticated. Depending on how the host app persists/keys data off `data.shop`, this enables cross-tenant data injection/confusion, matching the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker operate their own legitimate install of the target app (a normal unprivileged merchant), capture one real webhook delivery from Shopify for their own shop, and replay it to the app's public webhook endpoint with a modified `shop-domain`/`x-shopify-shop-domain` header. No access to `api_secret_key`, access tokens, or any privileged credential is needed — this is fully within the "unprivileged internet user" threat model, since webhook endpoints are public HTTP callback URLs and headers are attacker-controlled in the replayed request.

### Recommendation
Include the identity-relevant fields (`shop`, `topic`, `webhook_id`) in the HMAC-signed payload used for verification, or otherwise cryptographically bind them to the body (e.g., verify that `shop` corresponds to a shop with an active session/webhook registration matching this specific `webhook_id`/`topic` combination) before dispatching to the handler in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a genuine webhook, e.g. for `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of body B computed with app's api_secret_key>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - body `B` (attacker's own order data).
2. Attacker replays the exact same body `B` and the same valid `x-shopify-hmac-sha256` value to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` is constructed by the host app exactly as documented in `docs/usage/webhooks.md` lines 130-132.
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(B, api_secret_key)` [3](#0-2) .
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [5](#0-4) , causing attacker-controlled data `B` to be processed and attributed to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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
