Confirmed: `WebhookMetadata` at [1](#0-0)  exposes `shop` to the host app's handler, and this `shop` value is derived exclusively from an unauthenticated header, never covered by the HMAC that is verified.

### Title
Webhook shop-domain identity spoofing due to HMAC covering only the raw body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [2](#0-1) , while `shop` (and `topic`) are read straight from the `shop-domain`/`topic` headers with no cryptographic binding [3](#0-2) . `Registry.process` validates only this body-only HMAC and then dispatches the handler using the unverified `shop` value [4](#0-3) .

### Finding Description
`HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field of the query object [5](#0-4) . For `Webhooks::Request`, `to_signable_string` is just `@raw_body` [2](#0-1) , so the signature authenticates *only* the JSON body bytes. The `shop`, `topic`, `api_version`, and `webhook_id` fields, however, are read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are never included in the signed content [6](#0-5) .

`Registry.process` trusts these unauthenticated header values once the body HMAC checks out, and forwards `request.shop` into `WebhookMetadata`, which is exactly the value host apps use to attribute the webhook to a tenant/store [4](#0-3) .

This breaks the intended identity binding: `hmac == HMAC(secret, shop ‖ topic ‖ body)` is what an app relying on this gem needs to trust tenant attribution, but the gem only enforces `hmac == HMAC(secret, body)`. Any unprivileged merchant who has installed the public app on their own store can capture a legitimately-signed webhook delivery for their own shop (client_secret is shared across all installs of the same app) and replay it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain — the HMAC still validates because the body is unmodified, but the shop identity presented to the handler is now attacker-controlled.

### Impact Explanation
This is a cross-tenant identity-binding bypass: an attacker-controlled `shop` value, purportedly authenticated by a passing HMAC check, is delivered to the app's webhook handler. If the host app uses `WebhookMetadata#shop` (as documented/intended by this gem) to select the tenant session or scope a write/side effect, an attacker can inject data or trigger actions attributed to a store they do not control, using no elevated privileges — only a merchant account with the app installed and their own webhook traffic. This satisfies the Critical "cross-tenant access" impact category since the shop that requested no cross tenant HMAC coverage is exactly the boundary being crossed.

### Likelihood Explanation
The prerequisite is trivial: install (or already have installed) the target app on any shop the attacker controls, capture one legitimate webhook delivery (body + valid HMAC for that body from Shopify to the app's shared `client_secret`), and replay it to the app's public webhook endpoint with an altered `shopify-shop-domain` header. No secrets, tokens, or elevated access are required — this is fully reachable by any unprivileged merchant/internet user who can install the app.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed content that `HmacValidator` verifies, e.g. by having `Webhooks::Request#to_signable_string` concatenate the shop-domain and topic headers with the raw body before HMAC comparison, or by independently verifying the `shop` header against a known/authorized install list before trusting `request.shop` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers any subscribed webhook topic (e.g., `orders/create`) on their own shop, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends — this HMAC is valid because it's computed by Shopify itself using the app's real `client_secret`.
3. Attacker resends this exact body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` returns `true` (body and HMAC match) [7](#0-6) ; `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` even though the payload never originated for that shop [8](#0-7) .

### Citations

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
