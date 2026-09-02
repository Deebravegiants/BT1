This confirms the vulnerability: the HMAC in `ShopifyAPI::Webhooks::Request` (`lib/shopify_api/webhooks/request.rb`) signs only the raw body via `to_signable_string`, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no HMAC coverage, and `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) dispatches and attributes the event using those unverified header values.

### Title
Webhook `shop`/`topic` identity headers are not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-checking only the raw request body, but the `shop-domain`, `topic`, `webhook-id`, and `api-version` values that the `Registry` uses to route and attribute the event are read directly from unauthenticated headers.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from the request headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates only the body HMAC, then uses the unverified `request.topic` to select the handler and the unverified `request.shop` to build the metadata passed to that handler: [3](#0-2) 

This breaks the intended identity binding: `shop header == shop that authored/authorized the signed body`. In practice, the same `client_secret` is used to sign webhooks for every shop that has installed the app (it is not per-shop). Since installing an app is unprivileged (anyone can install it on their own store), an attacker can:
1. Install the target app on their own (attacker-controlled) shop.
2. Trigger a webhook event on their own shop with attacker-influenced body content (e.g. `orders/create`, `customers/create` fields that are largely attacker-controlled), causing Shopify to deliver it to the app's endpoint with a genuine `x-shopify-hmac-sha256` computed over that body using the app's real `client_secret`.
3. Replay that same body + valid HMAC to the same endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) to reference a victim shop/topic.

Because `HmacValidator.validate` only re-derives the signature from the body, this forged request passes verification, and `Registry.process` will hand the handler a `WebhookMetadata` claiming to be from the victim shop/topic with attacker-chosen body content.

### Impact Explanation
This is a cross-tenant identity spoofing vector: a host application that keys its webhook processing (order creation, GDPR redaction, data updates, etc.) off `WebhookMetadata#shop`/`#topic` as supplied by this gem will process attacker-controlled data attributed to another merchant's shop, without any way to detect the mismatch since the gem does not expose or enforce that the header-derived shop/topic were part of the signed material.

### Likelihood Explanation
Moderate-to-high for a multi-tenant SaaS app: exploitation only requires the attacker to be a legitimate (free/unprivileged) installer of the target app on their own store — no leaked credentials, `api_secret_key`, or access token is needed, since Shopify itself computes and delivers the valid HMAC for the attacker's own shop.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable material verified against the HMAC (or otherwise cryptographically bind them, e.g. by requiring the host app to independently confirm `shop` against a known/authorized shop list before dispatch), rather than trusting these identity-bearing headers as unauthenticated input alongside a body-only HMAC.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) with a body they mostly control.
2. Shopify delivers: headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, plus the raw JSON body.
3. Attacker resends the identical body and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, changing `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and/or `x-shopify-topic` to another registered topic).
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (body unchanged), `Registry.process` dispatches to the handler registered for the (possibly attacker-chosen) topic, and the handler receives `WebhookMetadata.shop == "victim-shop.myshopify.com"` with attacker-controlled body content — despite that shop never having sent this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
