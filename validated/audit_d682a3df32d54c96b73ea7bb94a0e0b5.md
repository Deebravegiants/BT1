I have enough evidence to confirm the finding. The HMAC covers only the raw request body, while `topic`, `shop`, `webhook_id`, and `api_version` are taken directly from unauthenticated headers, then handed to the app's handler as trusted metadata.

### Title
Webhook shop identity is trusted from an unauthenticated header while the HMAC only signs the body, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature verified by `Utils::HmacValidator.validate` binds *only* the body bytes to the app's `client_secret`. The `shop` (and `topic`/`webhook_id`) values are read straight from HTTP headers that are never included in the signed material. `Registry.process` trusts `request.shop` unconditionally when constructing the `WebhookMetadata` passed to the app's handler.

### Finding Description
The identity binding that should hold is:
`shop_authenticated_by_hmac == shop_delivered_to_handler`

In this gem it instead holds:
`shop_delivered_to_handler == header["shop-domain"]` — a value with **no cryptographic relationship** to the HMAC.

Concretely:
- `Request#to_signable_string` returns `@raw_body` only [1](#0-0) .
- `Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed data [2](#0-1) .
- `Registry.process` verifies the HMAC over the body, then immediately builds the handler payload using `request.shop`, `request.topic`, and `request.webhook_id`, none of which were part of the signature check [3](#0-2) .

Since the app's webhook secret (`Context.api_secret_key`, the app's `client_secret`) is **shared across every shop that installs the app**, any tenant that can obtain one validly-signed webhook body/HMAC pair for their own shop (e.g., by configuring their own webhook subscription address via the Admin API and capturing the delivered request, which is standard, unprivileged, self-service functionality) can replay that exact body+HMAC to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. Because the header is not covered by the signature, `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` will hand the app's handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: a shop-level actor (not privileged, not in possession of the app's `client_secret`) can forge webhook events that the host application will attribute to a different merchant. Any host app logic keyed off `WebhookMetadata#shop` (e.g., updating per-shop data, redact/GDPR flows, billing state, mandatory `shop/redact` handling) can be manipulated cross-tenant. This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
Reaching this requires no secret material and no privileged account beyond being a legitimate (even free-tier) installer of the app — exactly the kind of low-privilege actor the assessment targets. Capturing one's own valid webhook delivery and replaying it with a different `shop-domain` header is trivial once observed, and nothing in `Request` or `Registry` re-derives or checks `shop` against anything bound by the HMAC.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the material that is HMAC-verified, or otherwise cryptographically bind them — e.g., have `to_signable_string` incorporate the header values Shopify signs, or independently verify the `shop` header against a per-shop secret/session record rather than trusting the raw header value once the body's HMAC passes.

### Proof of Concept
1. App exposes a webhook endpoint and lets shop A (attacker's own store, which they can freely configure) register a webhook subscription (any topic) pointing to a server the attacker controls (using the Admin API — normal supported functionality).
2. Shopify delivers a webhook for shop A: body `B`, header `x-shopify-shop-domain: shop-a.myshopify.com`, header `x-shopify-hmac-sha256: sign(secret, B)`.
3. Attacker captures this request, then replays it directly to the app's real webhook processing endpoint, changing only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `sign(secret, B)` — identical to the captured value — and returns `true` [4](#0-3) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ...)` [5](#0-4) , causing the host app to act on attacker-controlled data as if it came from the victim tenant.

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
