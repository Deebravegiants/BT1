Confirmed. This is now sufficient to substantiate the finding.

### Title
Webhook `shop` (and `topic`/`webhook-id`) identity headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the shop identity (`shop-domain` header) that `Registry.process` trusts and forwards to app handlers is taken from an unauthenticated header that the HMAC never covers.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

so `to_signable_string` returns `@raw_body` only. `Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string: [2](#0-1) 

Meanwhile, `Request#shop` (and `#topic`, `#webhook_id`) are pulled straight from the `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header, which is never part of the signed bytes: [3](#0-2) 

`Registry.process` validates only the HMAC over the body, then trusts `request.shop` as the authenticated tenant identity and hands it to the app's handler: [4](#0-3) 

This produces the exact binding break the report describes by analogy: **bytes verified (`raw_body`) ≠ bytes/fields acted on (`shop`, `topic`, `webhook_id` headers)**. Because Shopify signs every webhook for every shop that has the app installed with the same app-level `client_secret`, the HMAC digest is shop-agnostic — it authenticates "this body byte-stream was produced with our secret," not "this body belongs to shop X." An unprivileged user who has the app installed on their own store (a normal, self-service action for any public app) receives genuinely-signed webhooks for their own shop. They can capture such a webhook and resend it to the app's registered webhook endpoint with only the `shop-domain` (and/or `topic`/`webhook-id`) header rewritten to name a different, victim shop. `HmacValidator.validate` still returns `true` because it only recomputes the digest over the unchanged raw body, and `Registry.process` forwards the attacker-controlled `shop` value into `WebhookMetadata#shop`: [5](#0-4) 

Any host application that follows the documented pattern of trusting `WebhookMetadata#shop`/`#topic` as the authenticated tenant/event identity (which is exactly what the gem's own API surface implies is safe, since `Registry.process` gates on `HmacValidator.validate` before dispatch) will process attacker-supplied data under another tenant's identity.

### Impact Explanation
This crosses a tenant boundary: an attacker who legitimately installs the app on their own store (no elevated privilege required) can make the gem accept and dispatch webhook payloads/topics as if they originated from an arbitrary victim shop, since the identity fields the gem exposes as "verified" (`shop`, `topic`, `webhook_id`) are not part of what the HMAC actually protects. This is a cross-tenant access primitive consistent with the "High" impact bucket (identity/tenant-binding check that answers permissively because the verified bytes and the acted-upon identity diverge).

### Likelihood Explanation
Exploitation only requires: (1) the ability to self-install the app on an attacker-controlled shop (available to any unprivileged merchant for public apps), (2) capturing one genuine webhook delivery for that shop, and (3) POSTing the identical body with a modified `shop-domain`/`topic` header to the app's public webhook endpoint. No knowledge of `client_secret` or any credential belonging to the victim is required, since the HMAC is validated over the same untouched body.

### Recommendation
Include the shop domain, topic, and webhook id in the signable string alongside the raw body in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind these header values before `Registry.process` treats them as authenticated tenant/event identity. At minimum, document clearly that `WebhookMetadata#shop`/`#topic` are not covered by `HmacValidator.validate` so host applications do not rely on them for tenant isolation.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a real webhook, e.g. `orders/create`, with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and a JSON body `B`.
2. Attacker resends the exact same body `B` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally the topic).
3. `ShopifyAPI::Webhooks::Request.new` parses the tampered headers; `Utils::HmacValidator.validate(request)` recomputes the HMAC only over `B` (unchanged) and returns `true`.
4. `Registry.process` proceeds, builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` and invokes the registered handler, which now processes attacker-controlled data attributed to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
