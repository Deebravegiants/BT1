## Analysis

Investigated the webhook processing pipeline in `lib/shopify_api/webhooks/`. Found a binding gap consistent with the requested bug class: the shop-identity field consumed by the webhook handler is not covered by the HMAC signature that `Registry.process` verifies.

### Title
Webhook `shop` identity used by handlers is not covered by the HMAC signature that `Registry.process` verifies, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking `Utils::HmacValidator.validate(request)`, and that HMAC is computed only over the raw request body [1](#0-0) . The `shop`, `topic`, and `webhook_id` values that get forwarded to the app's handler are pulled from unauthenticated HTTP headers, not from the signed payload [2](#0-1) .

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`; none of the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers participate in the signable string [3](#0-2) . `HmacValidator.validate` computes the HMAC over exactly that signable string and compares it to the `hmac` header [4](#0-3) . `Registry.process` treats a passing HMAC check as proof the whole request is legitimate and immediately hands `request.shop` — sourced from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header — to the app's handler as the tenant identifier: [1](#0-0) [5](#0-4) .

The documented usage pattern instructs apps to call `Registry.process` on the constructed `Request` to "verify the request did indeed come from Shopify" and then trust `data.shop` as "the shop domain of the webhook":

```
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
)
```

This is exactly the documented integration pattern; no misuse of the API is required to reach this gap.

**Binding broken (as an equality):**
`shop authenticated-by-signature` ≠ `shop delivered-to-handler`

- Before: the app assumes `HMAC-verified-body` ⇒ `header-shop-domain-is-trustworthy`.
- After an attacker request: an attacker who can capture one genuine, HMAC-signed webhook body/HMAC pair for shop A (e.g. from their own dev/trial store that legitimately installed the app and can trigger a webhook with content of their choosing) can replay that exact `raw_body` + `hmac` header while substituting the `shopify-shop-domain` header to any victim shop B. `HmacValidator.validate` still returns `true` (it never looked at the shop header), and `Registry.process` forwards `WebhookMetadata.new(shop: "shop-B...", body: <attacker-controlled-body-from-shop-A>, ...)` to the handler [6](#0-5) .

### Impact Explanation
Any handler that uses `data.shop` as the tenant key to look up sessions, write per-shop records, or branch business logic (exactly as shown in the gem's own documentation example, `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) will process attacker-supplied webhook content under a victim tenant's identity. This is cross-tenant data injection/confusion — an unprivileged user with their own store installation can inject fabricated events attributed to a different merchant, without ever needing the app's `client_secret`, an access token, or any privileged account.

### Likelihood Explanation
Moderate: requires the attacker to (a) control an app installation capable of receiving genuine webhooks (any merchant/dev who installs a public app can do this) and (b) be able to reach the app's public webhook endpoint directly with a replayed/edited HTTP request (trivial, since webhook endpoints are internet-facing by design). No secrets or elevated privileges are required.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` headers in the signable string used for HMAC verification, or otherwise cryptographically bind the shop-domain claim to the verified payload (e.g., cross-check the header shop domain against a shop identifier embedded inside the verified JSON body) before constructing `WebhookMetadata` in `Registry.process`.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker-shop.myshopify.com`, triggering a genuine webhook (e.g. `orders/create`) with attacker-chosen order content.
2. Attacker captures the raw POST body and the `X-Shopify-Hmac-SHA256` header from that genuine delivery (both are legitimately signed by Shopify for `attacker-shop`).
3. Attacker sends a new HTTP POST to the app's webhook endpoint, reusing the exact same body and `X-Shopify-Hmac-SHA256` value, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because only the (unmodified) body is signed [7](#0-6) .
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's order data>, ...)` and processes it as if it were a legitimate event from `victim-shop`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
