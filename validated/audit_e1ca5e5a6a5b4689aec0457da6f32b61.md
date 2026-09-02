This confirms the vulnerability. The webhook `Registry.process` method (`lib/shopify_api/webhooks/registry.rb:188-200`) validates only `Utils::HmacValidator.validate(request)`, and `Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) returns only `@raw_body` — none of the header-derived fields (`shop`, `topic`, `api_version`, `webhook_id`) are included in the HMAC-signed string. Yet `Registry.process` passes `request.shop` directly into `WebhookMetadata` (`lib/shopify_api/webhooks/registry.rb:198-199`, struct defined in `lib/shopify_api/webhooks/webhook_handler.rb:6-12`), which the host app's `WebhookHandler#handle` implementation uses to attribute the event/body to a specific tenant.

### Title
Webhook `shop` (and other Shopify headers) are not covered by HMAC verification, enabling cross-tenant webhook impersonation - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the HMAC signature. `Registry.process` trusts `Utils::HmacValidator.validate(request)` as proof of authenticity for the whole request, then forwards the unauthenticated `request.shop` value to the app's handler via `WebhookMetadata`.

### Finding Description
The equality the gem should guarantee is: `shop attributed to the webhook == shop that the HMAC-signed bytes originated from`. Instead, the HMAC only certifies the body bytes: [1](#0-0) 
while `shop`, `topic`, `webhook_id`, and `api_version` come from headers that are never part of the signable string: [2](#0-1) 

`Registry.process` performs a single check — `Utils::HmacValidator.validate(request)` — and, on success, unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) [4](#0-3) 

Because the app's single `api_secret_key` is shared across all shops (it is not per-tenant), any merchant who has installed the app is a valid, unprivileged source of *legitimately signed* webhook bodies for their own shop. Such a merchant can capture one of their own real webhook deliveries (raw body + valid `x-shopify-hmac-sha256`) and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header rewritten to a victim shop's domain. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:26-31` recomputes the HMAC over `to_signable_string`, which is unaffected by the header change, so validation still passes. The gem then reports this forged event to the app as originating from the victim shop.

### Impact Explanation
This breaks the tenant-authentication boundary this gem is trusted to enforce for webhook consumers: apps built on top of `ShopifyAPI::Webhooks::Registry.process` reasonably assume `WebhookMetadata#shop` is authenticated by the HMAC check that just occurred. An attacker-controlled shop can cause a host application to process arbitrary attacker-chosen (body, topic) pairs while impersonating a different shop, enabling cross-tenant data confusion/corruption in any app whose webhook handler keys off `data.shop` (e.g. to look up or update per-shop state, uninstall/redact flows, order/customer processing, etc.). This matches the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
High. The only prerequisite is that the attacker is a legitimate (even free/unprivileged) installer of the app — no special scope, no access token, and no knowledge of `api_secret_key` are required, since the attacker reuses an HMAC that Shopify itself already computed and delivered to them for their own shop. Replaying it with modified headers is trivial (a single HTTP request).

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the value verified by the HMAC — e.g. Shopify's own docs specify the HMAC is computed only over the body per-shop-secret-less design, so instead the fix should be at the trust boundary: `Registry.process` (or `Request`) must not treat a body-only HMAC pass as authenticating the header-derived `shop`/`topic`. Practically, this means documenting/enforcing that `request.shop` cannot be trusted as tenant-authenticated by `HmacValidator.validate` alone, or requiring callers to independently correlate the shop against a known, previously-registered webhook/shop pairing (e.g., validating that a session/subscription exists for that shop+webhook_id combination) before dispatching to `WebhookHandler#handle`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (unprivileged, ordinary merchant).
2. Shopify delivers a legitimate webhook to the app: body `{"id":1}"`, headers include `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over the body>`.
3. Attacker replays this exact body and HMAC to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` builds the request from these headers; `Utils::HmacValidator.validate(request)` succeeds because it only checks the raw body:
   `lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`.
5. `Registry.process` calls the app's `WebhookHandler#handle` with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though nothing about `victim-shop.myshopify.com` was ever verified by the HMAC — the app now processes attacker-controlled data as if it came from the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
