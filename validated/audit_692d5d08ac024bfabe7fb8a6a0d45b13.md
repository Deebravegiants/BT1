### Title
Webhook `shop` identity is not bound by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (tenant) attribute is read directly from an unauthenticated header and handed to the app's webhook handler as if it had been verified together with the signature.

### Finding Description
`Webhooks::Registry.process` verifies webhook authenticity by calling `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` and compares it to the `hmac-sha256` header value: [1](#0-0) 

`Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers that are **not** part of the signed content: [3](#0-2) 

After `HmacValidator.validate` succeeds, `process` builds `WebhookMetadata` using `request.shop` and passes it straight to the app's handler, trusting it as the authenticated tenant identity: [4](#0-3) 

This is the same defect class as the double-transfer bug in the report: the code validates one artifact (the body, via HMAC) but then *acts on* a second, unbound artifact (the `shop` header) as though the validation covered it. The equality the gem implicitly assumes is:

```
verified(body, hmac) == authenticated(shop-domain header)
```

but the actual binding enforced is only `verified(body, hmac)`; `shop-domain` is never included in the signable string, so the two are never actually tied together.

Because the app's `client_secret` (and therefore the webhook HMAC secret) is shared across every shop that installs the app rather than being per-shop, any party who can obtain one genuinely-signed `(raw_body, hmac)` pair for their own shop (e.g., by installing the app on a development/partner store they control and observing traffic they receive on infrastructure they control) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary victim `shop-domain` header. The signature still validates because the header is outside the signed content, and the handler receives `WebhookMetadata` attributing the (attacker-controlled) body to a shop it was never actually delivered for.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as documented and demonstrated by this gem) to key persisted data, trigger tenant-scoped side effects, or make decisions about a specific merchant (e.g., processing `app/uninstalled`, `shop/redact`, or order/customer events under an assumed shop), an attacker can cause the app to process attacker-controlled webhook content under a **different tenant's identity**, i.e., cross-tenant data injection/corruption without holding any credential for the victim shop. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to first obtain one legitimately HMAC-signed `(body, hmac)` pair, which is only practical if they can observe a webhook delivery sent to infrastructure they control (e.g., their own dev store pointed at a proxy/logging endpoint they operate) and then relay it to the target app's public webhook URL with a modified `shop-domain` header — no interception of the target's traffic, no access to the app's `client_secret`, and no privileged account on the victim shop are needed. This keeps likelihood moderate: it depends on the app exposing a stable/known webhook URL and the attacker being able to register/receive a webhook for a shop they control, both of which are realistic for any public commodity app.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed content, or otherwise cryptographically bind the authenticated shop to the request — for example by including the `shop-domain` header value in `to_signable_string`, or by cross-checking `request.shop` against a shop already bound to the session/registration that this webhook was registered for, before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own (attacker-controlled) Shopify development store and registers/receives a webhook subscription, capturing a genuine `raw_body` and its `shopify-hmac-sha256` value delivered to infrastructure they control.
2. Attacker sends this exact `raw_body` and `hmac` to the app's public webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `raw_body` against the secret, per `Webhooks::Request#to_signable_string` [2](#0-1) .
4. `Registry.process` passes `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` to the app's handler [1](#0-0) , which processes attacker-controlled data as though it originated from the victim shop.

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
