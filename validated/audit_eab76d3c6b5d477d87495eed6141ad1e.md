### Title
Webhook shop, topic, and webhook-id fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop`, `topic`, and `webhook_id` values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook are taken from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, and `webhook_id` are all read directly from HTTP headers, independent of the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC of the request (i.e., of `raw_body`), then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to dispatch and label the payload to the registered handler: [3](#0-2) 

Because the `shop-domain` header is not part of `to_signable_string`, the equality the code implicitly relies on — `shop-domain header == shop bound by the HMAC` — does not hold. An HMAC that is valid for a given `raw_body` under the app's `client_secret` remains valid no matter what `shop-domain`/`topic`/`webhook-id` headers accompany that body, since those fields are never mixed into the signable string. This is the same bug class as the report's `increaseAmount()` gap: a field that is acted upon (`shop`, used for tenant attribution) is not covered by the binding check (HMAC) that governs the other trusted fields (`raw_body`).

### Impact Explanation
An unprivileged actor who can obtain one genuine `(raw_body, hmac)` pair delivered by Shopify to the app's shared webhook endpoint (e.g., by triggering a webhook on their own store, since webhook endpoints for multi-tenant apps are shared across merchants) can replay that exact body/HMAC pair while substituting a different `shopify-shop-domain` (and/or `shopify-topic`, `shopify-webhook-id`) header. `HmacValidator.validate` will still return `true` because the signed string is unaffected, and `Registry.process` will hand the attacker-chosen `shop` value to the host application's webhook handler as if Shopify itself asserted it. If the host application uses `WebhookMetadata#shop` to key data writes, cache invalidation, or session/tenant lookups (the intended and documented use per `webhook_id:`/`shop:` fields on `WebhookMetadata`), this allows cross-tenant data confusion/injection — data legitimately generated for shop A can be attributed to shop B purely by header manipulation, without ever possessing shop B's credentials.

### Likelihood Explanation
Exploitability requires the attacker to have access to one legitimately signed webhook body for any shop (trivial for an app installer/merchant on their own store) and the ability to send an HTTP POST to the app's public webhook endpoint with modified headers (trivial, since it's a public internet endpoint by design). No secret key, session, or elevated privilege is needed to perform the spoof — it only requires observing the gem's own HMAC/verification boundary (body-only) versus the tenant-attribution boundary (header-only) diverging.

### Recommendation
Bind the tenant-identifying headers into the HMAC-signed payload the same way Shopify does at delivery time, or explicitly document/enforce that `shop`, `topic`, and `webhook_id` must not be trusted for authorization decisions unless independently re-validated (e.g., cross-checked against an active, previously-established session/shop record). At minimum, `VerifiableQuery#to_signable_string` for `Webhooks::Request` should incorporate `shop`, `topic`, and `webhook_id`, or `Registry.process` should re-derive/validate `shop` from a source that is covered by the signature before dispatching to handlers.

### Proof of Concept
1. Register a webhook handler for topic `orders/create` in a multi-tenant app.
2. As merchant of Shop A (unprivileged, self-service), trigger `orders/create`, capturing the POST body `B` and header `X-Shopify-Hmac-Sha256: H` sent to the app's shared webhook endpoint.
3. Send a new POST to the same webhook endpoint with body `B` (unchanged) and header `X-Shopify-Hmac-Sha256: H` (unchanged), but with `X-Shopify-Shop-Domain: shop-b.myshopify.com` substituted for Shop A's domain.
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)` which passes (only `raw_body` is checked), and the handler receives `WebhookMetadata.new(shop: "shop-b.myshopify.com", ...)` bound to Shop A's actual order payload — demonstrating the shop attribution is forgeable independent of the HMAC. [4](#0-3)

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
