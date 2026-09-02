### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are not covered by the HMAC signature, allowing cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery` but its `to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly and unauthenticated from HTTP headers and then handed to the app's webhook handler as if they were verified.

### Finding Description
`Webhooks::Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` and compares it to the `hmac` header. [1](#0-0) 

`Request#to_signable_string` is defined as just `@raw_body`: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers, none of which participate in the signed string: [3](#0-2) 

These header-derived, unauthenticated fields are then forwarded directly into the metadata passed to the host application's handler: [1](#0-0) 

The broken identity binding is: `HMAC_valid(raw_body) == true` is treated as if it implies `request.shop == authenticated_shop`, `request.topic == authenticated_topic`, and `request.webhook_id == authenticated_webhook_id`. In reality the HMAC only proves the app's secret was used to sign `raw_body`; it says nothing about which shop, topic, or webhook ID that body is attributed to. Anyone who can obtain one validly-signed `(raw_body, hmac)` pair — trivially achievable by installing the app on their own store and triggering any webhook event, since Shopify signs and delivers the webhook to the app's public endpoint — can resend that exact body/HMAC pair to the app's endpoint while substituting arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, and `x-shopify-api-version` headers. `HmacValidator.validate` will still return `true` because it never inspects those headers, and `Registry.process` will invoke the handler believing the event legitimately originated from the spoofed shop/topic/webhook.

### Impact Explanation
This is a cross-tenant identity-binding break at the exact bug class called out in the analog rules: a field ("shop"/"topic"/"webhook_id") acted upon by the application logic but not covered by the HMAC. A multi-tenant app that keys any business logic (e.g., attributing order/customer data, triggering `app/uninstalled` cleanup, GDPR data-request/erasure flows) off `WebhookMetadata#shop` or `#topic` can be made to process attacker-supplied body content under a victim shop's identity, or process a victim's genuine webhook data under the wrong topic — a cross-tenant confusion inside this gem's own webhook trust boundary, not merely a host-application misuse of a documented API, since the gem itself claims to have "validated" the whole request via `Utils::HmacValidator.validate(request)` while silently leaving `shop`/`topic`/`webhook_id` unauthenticated.

### Likelihood Explanation
Likelihood is high for any attacker who can install the target app on a shop they control (a normal, unprivileged onboarding flow for any public/multi-merchant app) and capture one legitimately Shopify-signed webhook delivery to the app's public endpoint. No access to `api_secret_key`, tokens, or privileged accounts is required — only the ability to trigger a webhook on one's own installation and resend it with different headers.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (in addition to the raw body) in the value that is HMAC-verified, or otherwise require the host application to separately assert that these header-derived values match the tenant context expected for the corresponding installed session before acting on them. At minimum, document prominently that only `raw_body` is authenticated by `HmacValidator`, so host apps do not implicitly trust `shop`/`topic`/`webhook_id` from `WebhookMetadata` as verified.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (self-service, no privileges needed).
2. Attacker triggers a webhook event (e.g., `orders/create`) on their own shop; Shopify POSTs to the app's public webhook endpoint with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Attacker captures `(B, HMAC(secret,B))` (e.g., via their own reverse proxy/logging in front of their self-hosted instance of the app, or any environment they control that fronts the webhook endpoint).
4. Attacker resends the exact same `B` and `hmac` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`, and/or a different `x-shopify-topic` / `x-shopify-webhook-id`.
5. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `B` against the secret; `Registry.process` invokes the topic handler with `WebhookMetadata.new(topic: "attacker-chosen", shop: "victim-shop.myshopify.com", body: parsed(B), webhook_id: "attacker-chosen", ...)`. [1](#0-0) 
6. The host app processes attacker-controlled body content attributed to the victim shop/topic, breaking tenant isolation.

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
