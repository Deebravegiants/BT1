### Title
Webhook shop-domain (and topic/api-version/webhook-id) headers are trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then uses the `shop`, `topic`, `api_version`, and `webhook_id` values taken from unauthenticated HTTP headers to route and process the webhook, including passing `shop` to the app's handler as the tenant identifier.

### Finding Description
`Webhooks::Registry.process` validates a webhook with: [1](#0-0) 

The only thing checked against `Utils::HmacValidator.validate(request)` is `request.hmac` compared against a signature computed over `request.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns only the raw body: [2](#0-1) 

Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` — the values used to decide *which tenant/topic* the webhook belongs to — are read directly from HTTP headers that are never included in the HMAC computation: [3](#0-2) 

This breaks the intended identity binding: `HMAC-verified content == body_bytes_only`, while the app trusts `request.shop == header["shopify-shop-domain"]` as the authenticated tenant, even though `header["shopify-shop-domain"] ⊄ HMAC-covered bytes`. Concretely, `equality that should hold` is `authenticated_shop == request.shop`, but the code only proves `HMAC(secret, raw_body) == received_hmac`; it never proves `HMAC(secret, raw_body ‖ shop_header) == received_hmac`.

Because the app's `client_secret`/webhook secret is shared across every shop that installs the app (it is not per-shop), any actor who can install the app on their own store (an unprivileged, ordinary merchant) will receive a legitimately HMAC-signed webhook whose signature is valid for that app regardless of which shop it names in the header. That attacker can replay the same signed body while substituting the `shopify-shop-domain` header (and/or `shopify-topic`) for a victim shop, and `Registry.process` will accept it, because header values are outside the scope the HMAC actually authenticates: [4](#0-3) 

### Impact Explanation
This allows cross-tenant impersonation: an attacker with a valid (but unmodified-body) HMAC signature from their own shop's webhook traffic can cause the handler to process the webhook attributing it to an arbitrary victim `shop` domain, since `WebhookMetadata.shop` is derived from the unauthenticated header, not from data covered by the signature. Any host application logic that keys per-tenant state (session lookup, data writes, side effects) off `WebhookMetadata#shop` is exposed to cross-tenant data corruption/confusion, which matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The precondition is only that the attacker can install/operate their own Shopify store using the same app (a normal unprivileged flow — no leaked secrets or elevated access required), and can intercept/replay their own legitimately-delivered webhook HTTP request while modifying the `shopify-shop-domain` header before forwarding to the app's public webhook endpoint. No knowledge of `api_secret_key` is needed.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them to the signed body), so that any header tampering invalidates the signature. At minimum, `to_signable_string` for `Webhooks::Request` should incorporate these header values rather than the raw body alone.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, receiving a real webhook POST with a valid `shopify-hmac-sha256` for the raw body `B` and header `shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the same body `B` and same `shopify-hmac-sha256` value to the app's public webhook endpoint, but changes the header to `shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` only checks `HMAC(secret, B)`, which still matches, so `Registry.process` proceeds and invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`. [4](#0-3)

### Citations

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
