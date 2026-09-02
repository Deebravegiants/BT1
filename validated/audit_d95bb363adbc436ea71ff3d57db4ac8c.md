Confirmed: `Registry.process` at `lib/shopify_api/webhooks/registry.rb:189-190` validates HMAC via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` — and `Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`). Meanwhile `Request#shop`, `#topic`, and `#webhook_id` are read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) that are **not part of the signed bytes** (`lib/shopify_api/webhooks/request.rb:15-33`). These unauthenticated header values are then forwarded verbatim into `WebhookMetadata` and handed to the app's handler (`lib/shopify_api/webhooks/registry.rb:198-199`), which typically uses `data.shop` as the tenant key to look up/act on merchant data.

### Title
Webhook HMAC only covers the request body, not the shop-domain/topic headers, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by verifying the HMAC over the raw body. The `shop`, `topic`, and `webhook_id` values that the handler actually acts on come from HTTP headers that sit entirely outside the HMAC-signed bytes.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header. For `Webhooks::Request`, `to_signable_string` returns just `@raw_body` [1](#0-0) . The `shop`, `topic`, and `webhook_id` accessors, however, read from `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers [2](#0-1) , which are never included in the signable string. `Registry.process` checks only the body HMAC before dispatching [3](#0-2) , then constructs `WebhookMetadata` directly from those unauthenticated header fields and hands it to the app's registered handler.

Critically, the signing secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that has the app installed — it is not per-shop. This means: shop A (an authenticated equality) ≠ shop B (the value the handler stores/keys off of). A merchant who has legitimately installed the app receives real webhooks addressed to their own shop, each with a valid HMAC over the body. Because the HMAC only binds the body — not the shop-domain — that same (body, hmac) pair remains valid if replayed to the app's webhook endpoint with the `shopify-shop-domain` (and/or `shopify-topic`/`webhook-id`) header rewritten to name a different, victim shop. `HmacValidator.validate` will still pass, and the handler will process attacker-chosen body content under an arbitrary victim shop's identity.

### Impact Explanation
This breaks the identity binding "shop authenticated by HMAC" = "shop the handler trusts and acts on," letting one tenant (any merchant with the app installed) forge webhook events attributed to a different tenant. Since most apps use `data.shop` from `WebhookMetadata` as the tenant/lookup key for merchant records, this enables cross-tenant data injection/corruption (e.g., forging `shop/redact`, `app/uninstalled`, or order/customer webhooks against another merchant's account) — a Critical-class cross-tenant access issue.

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint and possession of one genuine (body, hmac) pair, which any shop that installs the app receives continuously and legitimately as part of normal Shopify webhook delivery. No access token, `client_secret`, or privileged account is required — only header manipulation on an otherwise-authentic request.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-signed material, or independently verify `request.shop` against the shop associated with the session/subscription that the handler expects, rather than trusting the header value implicitly once the body HMAC passes.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com`; capture a legitimate webhook POST, e.g. `orders/create`, with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, and body `B`.
2. Replay the identical body `B` and HMAC header to the same webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com` (and optionally the topic/webhook-id headers).
3. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-190`) calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — unchanged — so validation succeeds.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` and processes attacker-controlled data as if it originated from `victim.myshopify.com`.

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
