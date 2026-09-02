### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop/tenant spoofing on replayed webhook payloads - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate`, using `Request#to_signable_string`, which returns only `@raw_body`. [1](#0-0) [2](#0-1)  The `shop`, `topic`, `webhook_id`, and `api_version` values used afterward to build `WebhookMetadata` (and dispatched to the host app's handler) are pulled directly from unauthenticated HTTP headers, never included in the HMAC-signed bytes. [3](#0-2) 

### Finding Description
The equality that should hold for a webhook to be trusted is:

`bytes_verified_by_HMAC == bytes_the_app_acts_on`

Here that equality is broken: `bytes_verified_by_HMAC = raw_body` only, while `bytes_the_app_acts_on` includes `shop` (and `topic`, `webhook_id`) taken from `shopify-shop-domain` / `x-shopify-shop-domain` headers, which are never mixed into the HMAC computation. [4](#0-3) [1](#0-0) 

`Registry.process` raises `InvalidWebhookError` only if the body-only HMAC fails, then immediately constructs `WebhookMetadata` using `request.shop`, `request.topic`, `request.parsed_body`, `request.api_version`, and `request.webhook_id`, and hands it to the app's registered handler: [2](#0-1) 

Because a valid HMAC only proves the *body bytes* were signed with the app's `client_secret` — it says nothing about which shop that body was originally sent for — any party that can obtain one legitimately-signed webhook body (e.g., by having their own store install the app and receive a real webhook) can resend that exact body to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. The HMAC check still passes (body unchanged), but `WebhookMetadata#shop` now reports a different shop than the one whose secret-derived signature was actually validated. Any host application that uses `data.shop` to select which tenant's DB/records to update (the documented, expected usage pattern shown in `docs/usage/webhooks.md`) will process/attribute this replayed payload to the attacker-chosen shop.

### Impact Explanation
This breaks the shop-identity binding at the point the library hands verified data to the app, enabling cross-tenant data injection/spoofing: an attacker-controlled shop can cause a webhook event to be attributed to a victim shop's domain. This matches the Critical "cross-tenant access" category — the library's own construct (`WebhookMetadata.shop`) that host applications are documented to trust for tenant identification is not actually bound to the cryptographic proof that authenticated the request.

### Likelihood Explanation
Requires only an unprivileged actor who can install the target app on any store they control (common for public apps) and can craft/replay a raw HTTP POST to the app's public webhook endpoint — no access to `api_secret_key`, tokens, or the victim's credentials is needed. Exploitability depends on the host application trusting `data.shop` from `WebhookMetadata` without independently cross-checking it against known/installed shop sessions, which is exactly what this gem's `WebhookMetadata` is intended to convey to consumers.

### Recommendation
Bind the shop domain (and ideally topic/webhook id) into the value verified by HMAC, or require the host app to cross-validate `shop` against a known/installed session store. Concretely, extend `Request#to_signable_string` (or add an additional verification step in `Registry.process`) so that the `shop-domain` header is authenticated together with the body — e.g., only trust `request.shop` after confirming a session/install record exists for that shop domain and topic, or document explicitly and enforce that consumers must not rely on `WebhookMetadata#shop` as an authenticated identity binding without a secondary lookup.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, triggering Shopify to send a legitimate webhook (e.g. `orders/create`) with a real HMAC computed over the JSON body using the app's `client_secret`.
2. Attacker captures the raw request: headers `x-shopify-topic`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and the JSON body.
3. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (unchanged). [5](#0-4) 
5. `WebhookMetadata.new(topic:, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` and passed to the app's handler, which — following this gem's documented pattern — processes/store the order data as belonging to the victim shop. [6](#0-5)

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
