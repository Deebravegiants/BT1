### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string solely from the raw HTTP body, while the shop identity (`shop-domain` header) is read directly from request headers and forwarded to the handler as an authenticated fact, without ever being covered by the HMAC signature.

### Finding Description
`Registry.process` validates the HMAC before dispatching to the handler: [1](#0-0) 

The HMAC check only proves that `@raw_body` was signed with `Context.api_secret_key`: [2](#0-1) [3](#0-2) 

`shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of `to_signable_string` and therefore not bound by the HMAC: [4](#0-3) 

This unauthenticated `shop` value is then passed straight into `WebhookMetadata` and handed to the app's handler as the trusted tenant identifier: [5](#0-4) 

The equality that should hold is: `shop_bound_by_hmac == shop_used_for_tenant_routing`. In this implementation, `shop_bound_by_hmac` is undefined (not signed at all), while `shop_used_for_tenant_routing = request.shop` (raw header). This is exactly the "field acted on but not covered by the HMAC" pattern described in the analog report: bull/bear utilization was split from what the price formula actually charged; here, the header used to route/attribute webhook data is split from what the signature actually covers.

Because `Registry.process` raises `InvalidWebhookError` only if the HMAC over the body fails, a request with a valid, previously-observed `(raw_body, hmac)` pair but an attacker-modified `shop-domain` header will still pass validation and be dispatched with the forged `shop` value.

### Impact Explanation
Any party capable of producing one legitimately HMAC-signed webhook body (e.g., an app's own installed shop, which naturally receives real webhooks with valid signatures from Shopify) can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. The handler in the host app receives `WebhookMetadata` with `shop` set to the attacker-chosen victim shop, and typically uses this field as the per-tenant key to persist/update data (order records, inventory, mandatory GDPR actions, etc.). This crosses the tenant boundary: data delivered by one shop's HMAC ends up attributed and processed under a different shop identity, i.e., cross-tenant data confusion caused purely by this gem's failure to bind `shop` inside the verified message.

### Likelihood Explanation
Likelihood is high for a real installed merchant/attacker (no leaked credentials, tokens, or TLS interception required): they only need to capture a genuine webhook payload+signature that Shopify delivered for their own shop (trivial, since it is sent to their own endpoint), then resend it with a modified shop header. This satisfies the "unprivileged internet user" bar — no access token, refresh token, or `client_secret` is needed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-covered signable string, or independently verify that `request.shop` matches an application-known/registered shop before trusting it, rather than relying on an unauthenticated header for tenant attribution. At minimum, document that consumers of `WebhookMetadata#shop` must not treat it as cryptographically authenticated and must cross-check it against their own shop registry keyed by a value that is actually bound to the signature.

### Proof of Concept
1. App installed on `shop-a.myshopify.com`; Shopify sends a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's `api_secret_key`), header `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Attacker (who controls `shop-a`, e.g., a malicious merchant) captures this `(B, H)` pair.
3. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and same `H`, but header `x-shopify-shop-domain: shop-victim.myshopify.com`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-190`) calls `HmacValidator.validate`, which only checks `B` against `H` — passes.
5. Handler receives `WebhookMetadata.new(topic:, shop: "shop-victim.myshopify.com", body: parsed(B), ...)` and processes data under the victim's tenant identity, even though the victim never sent this data.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
