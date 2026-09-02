### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted from unauthenticated HTTP headers while the HMAC signature only covers the raw body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying fields `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers, but `to_signable_string` (the bytes that are actually HMAC-verified) is only the raw request body. This breaks the binding "the shop covered by the HMAC == the shop the gem treats the webhook as coming from."

### Finding Description
`Webhooks::Registry.process` verifies a webhook using `Utils::HmacValidator.validate(request)`, which computes an HMAC over `request.to_signable_string` and compares it to the value returned by `request.hmac`: [1](#0-0) 

`to_signable_string` for a webhook `Request` is defined as `@raw_body` only: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` — the fields used to route and attribute the webhook to a specific merchant/tenant — are read straight from HTTP headers, which are **not** part of the signed bytes at all: [3](#0-2) 

After HMAC validation passes, `process` builds a `WebhookMetadata` object using these unauthenticated header values and hands it to the app's handler as the trusted tenant/topic identity: [4](#0-3) 

Because the signature only binds to the body bytes, any request carrying a `(raw_body, hmac)` pair that is valid for *some* shop's webhook can be replayed with a different `shopify-shop-domain` (or `shopify-topic` / `shopify-webhook-id`) header and will still pass `HmacValidator.validate`, since the HMAC check never inspects those headers. The equality that should hold — `shop authenticated by HMAC == shop attributed to the webhook by the gem` — is not enforced; only `raw_body authenticated by HMAC == raw_body received` is enforced, and `shop` is orthogonal to that check.

### Impact Explanation
An attacker who can obtain one legitimate `(raw_body, hmac)` pair (e.g., from a webhook delivered to a shop they control, or one leaked/logged/proxied through infrastructure they observe) can replay that exact body with a forged `shopify-shop-domain` header pointing at a victim shop. `HmacValidator.validate` still returns `true` because it only recomputes/compares the HMAC of the unchanged body. The app's registered handler then receives `WebhookMetadata` claiming the payload is for the victim shop, causing the host application to process and attribute attacker-supplied data to a different tenant — a cross-tenant identity/data-attribution bypass reachable by an unprivileged party with no access token, `client_secret`, or privileged account.

### Likelihood Explanation
Exploitation only requires capturing one valid webhook delivery for any shop (including the attacker's own installed app instance, which they legitimately receive) and replaying it with modified headers against the same publicly reachable webhook endpoint. No secret material, TLS interception, or privileged access is needed beyond normal use of the app as an installed merchant.

### Recommendation
Bind the identity fields used for tenant attribution into the signed material, or otherwise independently verify that the `shop` header value corresponds to a shop with a known/active session before trusting it for routing/processing — do not rely solely on HMAC-of-body to authenticate header-derived shop/topic/webhook_id values.

### Proof of Concept
1. App instance is installed on `attacker-shop.myshopify.com`; attacker triggers a benign event and captures the webhook HTTP request Shopify sends, including headers (`shopify-hmac-sha256: H`, `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: orders/create`) and raw body `B`.
2. Attacker resends the identical body `B` and `shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds.
4. `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` is passed to the app's handler as if it were an authentic webhook for `victim-shop.myshopify.com`, even though nothing about that shop identity was ever verified. [4](#0-3)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
