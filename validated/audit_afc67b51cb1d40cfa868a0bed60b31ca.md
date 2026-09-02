### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `HmacValidator` checks in `Registry.process` authenticates the *payload bytes* but never binds the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers to that signature. `Registry.process` nonetheless trusts `request.shop` and hands it straight to the registered handler as the tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` as plain header reads: [1](#0-0) 

But the signable content used for HMAC verification is only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC over that body-only string, then immediately trusts the *unauthenticated* `request.shop` header to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The bound equality the gem implicitly claims is: `shop header == shop that produced/owns this HMAC-signed body`. In reality the HMAC only proves `HMAC(secret, raw_body) == received_signature`; it says nothing about which shop header accompanies that body. Any attacker capable of obtaining one legitimately-signed `(raw_body, hmac)` pair — e.g., an unprivileged user who installs the app on their own shop and receives real webhooks for it — can replay that exact `(raw_body, hmac)` pair while swapping the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to a victim shop's domain. `HmacValidator.validate` still succeeds because it only re-derives the signature from `@raw_body`, and `Registry.process` will dispatch the handler with `request.shop` equal to the victim shop, `request.parsed_body` equal to the attacker's own (legitimately obtained) payload.

This is the same class of bug as the report's "field acted on but not covered by the signature": Chainlink's deprecated `latestAnswer()` decouples the trusted price from round completeness/staleness checks; here the shop identity used by the handler is decoupled from the bytes the signature actually authenticates.

### Impact Explanation
This breaks the tenant/shop identity binding relied upon by any host application that keys storage, side effects, or session lookups off `WebhookMetadata#shop` (which is the documented and expected usage pattern for `ShopifyAPI::Webhooks::Registry`). An attacker with a legitimate, low-privilege installation on shop A can cause the app to process webhook data under shop B's identity, enabling cross-tenant data injection/confusion — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires the attacker to already hold one valid `(raw_body, hmac)` pair, which is trivially obtainable by installing the app on any shop they control and capturing a real webhook delivery (no `api_secret_key` or privileged access needed — only their own shop's normal use of the app). The header rewrite is a standard unprivileged HTTP replay, so likelihood is moderate to high wherever the host application trusts `WebhookMetadata#shop` for tenant scoping, which is the intended usage of this API.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed/verified material, or explicitly re-validate that the `shop-domain` header matches an expected/allow-listed value for the signed body before dispatching to handlers. At minimum, document that `request.shop` is unauthenticated and must not be used as a sole tenant-binding key, and make `HmacValidator`/`Request#to_signable_string` bind the header value into the string that is verified.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets it register for a webhook topic (e.g., `orders/create`).
2. Shopify delivers a legitimate webhook to the app: body `B`, headers include `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the identical request to the app's webhook endpoint, keeping body `B` and the HMAC header unchanged, but rewrites `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` from `to_signable_string` (body only) and it matches, so validation passes: [4](#0-3) 
5. `Registry.process` builds `WebhookMetadata` with `shop: request.shop` == `"victim-shop.myshopify.com"` and dispatches to the host app's handler, which processes attacker-controlled data under the victim's tenant identity: [5](#0-4)

### Citations

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
