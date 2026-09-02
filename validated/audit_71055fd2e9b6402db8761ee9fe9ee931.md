Confirmed: the `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers that are never included in the HMAC-signed content [2](#0-1) . `Registry.process` validates only the HMAC over the body and then dispatches the handler using the unauthenticated `request.shop` value [3](#0-2) .

### Title
Webhook Shop-Domain Header Not Covered by HMAC Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the `shop`, `topic`, `webhook_id`, and `api_version` fields are taken verbatim from HTTP headers that are never part of the signed payload. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` to identify the tenant after validating only the body's HMAC, so the binding "HMAC-authenticated payload == payload the handler acts on" does not hold for the shop identity.

### Finding Description
`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string`, and for webhook requests `to_signable_string` simply returns `@raw_body` [1](#0-0) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from the `shopify-*`/`x-shopify-*` headers with no cryptographic binding to those header values [2](#0-1) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (body HMAC) before building `WebhookMetadata` from `request.shop`, `request.topic`, etc., and invoking the app-supplied handler with that metadata [3](#0-2) .

Since the HMAC covers only the body bytes and not the shop-domain header, any request whose body produces a valid HMAC (e.g., a genuine webhook payload originally delivered to the attacker's own shop, or any payload for which the attacker can obtain a validly-signed body) can be replayed to the app's webhook endpoint with the `shopify-shop-domain`/`x-shopify-shop-domain` header rewritten to a victim shop's domain. The signature still validates because the body is unchanged, but `Registry.process` reports the event as belonging to the attacker-controlled `shop` value, breaking the equality `shop authenticated by HMAC == shop used by the handler`.

### Impact Explanation
This is a cross-tenant integrity issue: an unprivileged internet user who controls one legitimate Shopify shop (and thus can generate genuinely-signed webhook deliveries for events under their control, e.g. `app/uninstalled`, `shop/update`, or any topic with attacker-controllable body content) can cause the host application to process that event as if it originated from a different, victim shop, because the shop identity is not authenticated by the HMAC. Depending on what the host app's webhook handler does with `WebhookMetadata#shop` (e.g., look up/mutate per-shop records, trigger data deletion, disable app for a shop, etc.), this can lead to cross-tenant state corruption in the host application, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to be able to trigger any webhook delivery whose body they can predict/control combined with a target topic accepted by the app (many topics like `app/uninstalled` have static or attacker-influenced bodies), and access to send arbitrary HTTP requests to the app's public webhook endpoint — both are available to any unprivileged internet user with their own Shopify store. No access token, `client_secret`, or privileged account is needed, since the HMAC is computed with the app's secret but the attacker doesn't need to know the secret — they only need Shopify to have already signed a body for their own delivery, which they replay with a modified shop header.

### Recommendation
Include the shop-domain (and ideally topic/webhook_id) header value in the HMAC-signable content, or otherwise cryptographically bind `shop` to the signed payload, so that `Registry.process` cannot dispatch events under an unauthenticated shop identity. At minimum, document that host applications must independently verify `WebhookMetadata#shop` against their own authorization state before acting on it.

### Proof of Concept
1. Attacker installs the app on their own Shopify store `attacker.myshopify.com` and triggers a webhook event (e.g., `app/uninstalled`) with a body they can predict, receiving a genuinely Shopify-signed `shopify-hmac-sha256` header for that body.
2. Attacker sends a POST request to the host app's webhook endpoint with the same raw body and `shopify-hmac-sha256` value, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header [4](#0-3) ; `Registry.process` validates the HMAC against the (unchanged, genuinely signed) body only [5](#0-4)  and passes, then calls the handler with `shop: "victim-shop.myshopify.com"`.
4. The host app's handler acts on `victim-shop.myshopify.com` even though the delivery was never authenticated for that shop.

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
