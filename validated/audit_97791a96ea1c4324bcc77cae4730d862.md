### Title
Webhook HMAC only covers the raw body, allowing shop/topic header spoofing for cross-tenant impersonation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC over the raw request body only. The `shop`, `topic`, `webhook_id`, and `api_version` values — all of which are trusted downstream by the host application to identify the tenant and route processing — are read from unauthenticated HTTP headers that are never part of the signed content.

### Finding Description
`Webhooks::Registry.process` validates a webhook purely via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` for the bytes that get HMAC-verified: [1](#0-0) 

The `to_signable_string` implementation returns only the raw body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which are covered by that signable string: [3](#0-2) 

After HMAC validation succeeds, `Registry.process` looks up the handler by `request.topic` and hands the handler a `WebhookMetadata` built directly from the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id`: [4](#0-3) 

The identity binding that should hold is: `shop/topic authenticated by HMAC == shop/topic acted upon by the handler`. Because the signature only covers the body bytes, this equality is broken — the `hmac-sha256` header cryptographically proves nothing about which shop or topic the payload is scoped to; it only proves the body wasn't tampered with.

### Impact Explanation
The app's `api_secret_key` is shared across all shops that installed the app; it is not shop-specific. An attacker who controls (or trials-installs) the app on their own shop can capture one legitimate webhook delivery (body + valid `x-shopify-hmac-sha256`), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic` header) for a victim shop or a more sensitive topic (e.g. `app/uninstalled`, `shop/redact`). `HmacValidator.validate` still succeeds because it never inspects the headers, so the forged shop/topic values are passed to the host application's handler as if authentic. If the host app uses `data.shop` to key a tenant record (as the gem's own docs/tests assume, e.g. loading a session/tenant by `data.shop`), this is a cross-tenant confused-deputy: content genuinely signed for the attacker's own shop is processed as if it belonged to another merchant, or a body meant for one topic is now dispatched to a different topic's handler. This crosses the tenant boundary using only the app's globally-shared secret, without needing an access token, matching the "cross-tenant access" Critical-tier impact category.

### Likelihood Explanation
Exploitation requires only: (1) the attacker holds any legitimate app installation (attacker's own dev/test store) to obtain one valid `(body, hmac)` pair, and (2) the ability to send arbitrary HTTP requests to the app's public webhook endpoint with attacker-chosen headers — both trivially available to any unprivileged internet user / app installer. No secret, token, or privileged account is required beyond what any merchant installing the app already has.

### Recommendation
Bind the shop, topic, and webhook id into the verified signature material, or otherwise cryptographically tie the header values to the HMAC before trusting them. Since Shopify's webhook `hmac-sha256` header is computed only over the raw body on Shopify's side as well, `Registry`/`Request` should not expose `shop`/`topic`/`webhook_id` as trusted output of `process` without documenting that these headers are unauthenticated and must be cross-checked (e.g. against a shop known to have installed the app and registered that specific topic/webhook id) before being used to key any tenant-scoped operation. At minimum, update documentation/guidance to explicitly warn integrators that `WebhookMetadata#shop`/`#topic` are unauthenticated and must not be used as the sole tenant selector.

### Proof of Concept
1. Install/trial the app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook topic registered by the app (e.g. `orders/create`) to capture a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's `api_secret_key`.
2. Replay this exact body and HMAC header to the app's webhook receiving endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` (and optionally `x-shopify-topic` to a different registered topic name).
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks presence, not authenticity) and `Utils::HmacValidator.validate` succeeds because it only recomputes the HMAC over `@raw_body`, per [5](#0-4) .
4. `Registry.process` dispatches to the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the forged, unauthenticated values, per [6](#0-5) , causing the host application to act on `victim.myshopify.com`'s data using attacker-controlled webhook content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
