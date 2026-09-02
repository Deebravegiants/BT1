Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC signature (verified in `Registry.process` via `Utils::HmacValidator.validate(request)`) authenticates only the request body — it does not cover the `shopify-shop-domain` header that is exposed as `request.shop` and passed into `WebhookMetadata.new(... shop: request.shop ...)`. [1](#0-0) [2](#0-1) 

### Title
Webhook shop identity spoofing via unsigned `shopify-shop-domain` header enables cross-tenant webhook injection - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the shop identity delivered to the application's webhook handler comes from a separate, unsigned HTTP header. Since the same `client_secret`/`api_secret_key` is shared across all merchants installing an app, any holder of one valid `(raw_body, hmac)` pair from any shop can replay it to the app's webhook endpoint with an arbitrary `shopify-shop-domain` (or `x-shopify-shop-domain`) header value, and `Registry.process` will accept it as authentic for that spoofed shop.

### Finding Description
`Webhooks::Request` includes `Utils::VerifiableQuery` and defines: [3](#0-2) 

so `to_signable_string` returns only `@raw_body`. `shop` is read straight from a header that is not part of the signed content: [4](#0-3) 

`Registry.process` verifies the HMAC of the request and, on success, immediately forwards `request.shop` (the unauthenticated header) to the app's handler: [5](#0-4) 

This breaks the intended identity binding `hmac_valid(body) == authentic(shop, body)`. In reality, `hmac_valid(body)` only proves the body was produced (or replayed) under the app's shared `api_secret_key`; it says nothing about which shop the payload belongs to. Because `api_secret_key` is shared by all shops that install the same app (it's not per-tenant), an unprivileged user who operates or controls their own shop installation can:

1. Trigger any webhook topic on their own shop, capturing the exact `raw_body` + `shopify-hmac-sha256` header Shopify sends (both attacker-observable, since it's their own store's webhook delivery).
2. Replay that identical `(raw_body, hmac)` pair to the target app's public webhook endpoint, but substitute the `shopify-shop-domain` header with a victim shop's domain.
3. `HmacValidator.validate` recomputes the HMAC over `raw_body` only and it matches (same secret, same body) — validation succeeds.
4. The handler receives `WebhookMetadata` with `shop: <victim shop>` and the attacker's chosen `body`, `topic`, and `webhook_id`, believing this event genuinely originated from the victim's store.

### Impact Explanation
This is a cross-tenant confusion vulnerability: an attacker who is merely an installer of the same app on their own store can make the app process fabricated events "as if" they came from any other merchant using the app, without needing that merchant's credentials, access token, or `client_secret`. Depending on how the host application's webhook handlers act on `data.shop` (e.g., updating shop-scoped records, triggering redactions, provisioning/deprovisioning resources, sending notifications, or writing to the victim shop's stored state), this enables cross-tenant data corruption or unauthorized actions attributed to a shop the attacker does not own — matching the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Likelihood is high for any app builder relying solely on `ShopifyAPI::Webhooks::Registry.process`/`Request` for webhook trust decisions, since nothing in the gem's own validation path ties the accepted `shop` value to the signed bytes. Exploitation only requires the attacker to install the target app on a shop they control (a standard, unprivileged action) and issue a normal HTTP POST with modified headers to the app's existing public webhook route — no secrets, tokens, or elevated privileges are needed.

### Recommendation
Bind the shop identity into the signed content verification path, e.g., have `Webhooks::Request#to_signable_string` (or a separate verification step in `Registry.process`) incorporate the shop domain header (or require the caller to independently authenticate/authorize `request.shop` against a known/expected value per installation) before trusting it, so `hmac_valid` cannot be satisfied while the shop header is substituted.

### Proof of Concept
1. App is installed on attacker's own shop `attacker.myshopify.com`, which shares the app's single `api_secret_key` with every other install.
2. Attacker triggers a webhook (e.g. `orders/create`) on their own shop and captures the raw POST body and its `shopify-hmac-sha256` header from Shopify's delivery.
3. Attacker sends this identical body + hmac header to the app's webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only — matches, so validation passes: [6](#0-5) 
5. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, so the app treats attacker-supplied data as if it were the victim's authentic webhook event.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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
