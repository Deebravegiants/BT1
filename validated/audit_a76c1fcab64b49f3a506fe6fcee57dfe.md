### Title
Webhook HMAC only covers the raw request body, allowing shop-domain header spoofing for cross-tenant webhook injection - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, never the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. `Webhooks::Registry.process` validates the HMAC and then unconditionally trusts these unsigned headers—especially `shop`—to build the `WebhookMetadata` that is handed to the host application's webhook handler.

### Finding Description
The signable string used for HMAC verification is defined as: [1](#0-0) 

Meanwhile the `shop`, `topic`, and `webhook_id` accessors read straight from request headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC over the query object, then immediately trusts the unauthenticated header fields to construct the metadata delivered to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop field trusted by the app handler == shop field covered by the HMAC signature`. In this implementation that equality does not hold — the HMAC signs only `@raw_body`, so `shop`, `topic`, and `webhook_id` are outside the signed byte range while still being treated as authenticated tenant-identifying data by `Registry.process`.

The HMAC secret used here is `Context.api_secret_key`, i.e. the app's own `client_secret`, which is identical across every merchant shop that installs the same app. Any unprivileged user can install the app on their own (e.g., free/dev) shop, trigger a real webhook event, and receive from Shopify a validly-HMAC-signed `raw_body` + `X-Shopify-Hmac-Sha256` header pair addressed to the app's webhook endpoint. Because the header `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) is not part of the signed content, the attacker can replay the exact same body+HMAC to the same endpoint while substituting a victim shop's domain (or any other topic/webhook-id) in the headers. `Utils::HmacValidator.validate` will still succeed because it only re-derives the signature from `@raw_body`, and `Registry.process` will then dispatch the (attacker-controlled) payload to the handler tagged with the victim's `shop` value.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: the "shop" identity handed to the application's webhook handler is not the shop that actually produced/authenticated the signed bytes. Any host application that uses `WebhookMetadata#shop` to select which merchant's data store to write into (a common and expected pattern per the gem's own webhook handler contract) can be made to process attacker-supplied webhook payloads under another tenant's identity — i.e., cross-tenant data injection/confusion using only a legitimately-obtained webhook from the attacker's own shop.

### Likelihood Explanation
Requires the attacker to control any shop that has the target app installed (achievable for anyone able to install a free-tier or trial installation of the app — no special privilege, no leaked secret needed) and the ability to send a raw HTTP request to the app's public webhook endpoint with modified headers, which is straightforward.

### Recommendation
Include the tenant/topic identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used by `to_signable_string`, or otherwise cryptographically bind them to the HMAC (e.g., verify the `X-Shopify-Shop-Domain` header against a shop value embedded in `raw_body`/registration, or require the caller to additionally corroborate `shop` against a known/registered value before trusting it in `WebhookMetadata`). At minimum, document that consumers of `Webhooks::Registry` must not rely on `request.shop` for tenant selection without independent verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `orders/create`) on their store; Shopify sends a real, validly HMAC-signed POST to the app's webhook endpoint containing `raw_body` and header `X-Shopify-Hmac-Sha256: <valid-hmac>` plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures this request and replays it to the same endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256` unchanged, but rewriting `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely from `to_signable_string` (`@raw_body`) and succeeds since the body/HMAC pair is untouched ( [4](#0-3) ).
5. `handler.handle` is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` now returns `"victim.myshopify.com"` ( [5](#0-4) ), causing the application to process attacker-controlled webhook data as if it belonged to the victim's tenant.

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
