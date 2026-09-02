### Title
Webhook shop-domain header not covered by HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute (used to identify which merchant a webhook belongs to) purely from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, while the HMAC signature that `Registry.process` validates only covers the raw request body.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the request headers and is never included in the signed payload: [2](#0-1) 

`Registry.process` validates the webhook solely via `Utils::HmacValidator.validate(request)` (which calls `to_signable_string`, i.e. body-only), then immediately trusts `request.shop` when building the `WebhookMetadata` passed to the host application's handler: [3](#0-2) 

The identity binding that should hold is: `shop attributed to the webhook == shop cryptographically bound to the HMAC`. Because the HMAC is computed only over `@raw_body` and never incorporates the `shop-domain` header, this equality does not hold — an attacker who possesses one valid `(raw_body, hmac)` pair for topic X (e.g., from their own development/test store, which they legitimately control and can generate valid webhooks for) can replay that exact body and signature while substituting an arbitrary `shopify-shop-domain` header value. The signature check will still pass because it never inspects the header, yet `WebhookMetadata#shop` will reflect the attacker-chosen value and get passed to the host app's `handle` method.

### Impact Explanation
This is a cross-tenant identity binding break in the webhook receiver: an app's `WebhookHandler#handle` implementation receives `WebhookMetadata.shop` as an authenticated fact (it just passed HMAC validation) but it is actually attacker-controlled. Any host application logic that looks up per-shop settings/records or writes data keyed by `WebhookMetadata.shop` can be misled into operating on the wrong tenant's data (cross-tenant access), a Critical-class impact per the report's own credential/identity-binding framing — it directly parallels the reported issue of "no checks on a value used for identity/state decisions", except here it is a header value rather than an oracle rate.

### Likelihood Explanation
Exploitation requires only the ability to obtain one valid signed webhook body from Shopify — trivial for any developer with a development store (no privileged credentials, access tokens, or `api_secret_key` needed) — and the ability to POST an HTTP request to the app's public webhook endpoint with a forged header, which is exactly the kind of unprivileged-internet-user capability in scope.

### Recommendation
Include the `shop-domain` header (and ideally `topic`, `api-version`, `webhook-id`) in the HMAC-signed material, or otherwise verify that the `shop` claimed in the header matches an independently derived/expected shop (e.g., from a route parameter tied to a stored session) before constructing `WebhookMetadata`. At minimum, document clearly that `WebhookMetadata.shop` is unauthenticated and host apps must independently corroborate it.

### Proof of Concept
1. Register a webhook for topic `orders/create` and receive one legitimate delivery from Shopify (or generate a valid HMAC using a store's own webhook secret in a dev store) — the attacker legitimately controls this store, so they have a valid `(raw_body, hmac)` pair.
2. Replay the exact same HTTP request to the target app's webhook endpoint, but replace the `X-Shopify-Shop-Domain` header with the victim shop's domain (`victim-shop.myshopify.com`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the shared secret — the same secret is used across all shops installed via the same app/API key.
4. `WebhookMetadata.new(... shop: request.shop ...)` at [4](#0-3)  now carries `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own store, and the host app's `handle` method processes it as if it were victim data.

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
