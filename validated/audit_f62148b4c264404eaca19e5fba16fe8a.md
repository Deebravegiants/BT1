This confirms the vulnerable pattern. The docs explicitly document `data.shop` as the "shop domain of the webhook" that the handler is expected to trust for tenant identification (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), yet this field is never covered by the HMAC signature.

### Title
Webhook `shop` domain is not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, excluding the `x-shopify-shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC over that signable string, then dispatches the handler using the unauthenticated `request.shop` value. This breaks the intended identity binding `HMAC-verified data == data acted upon`.

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, and for webhook requests that method is defined as: [1](#0-0) 
which returns only `@raw_body`, never the `shop`, `topic`, or other headers.

`Registry.process` validates this HMAC, then immediately builds `WebhookMetadata` using `request.shop`, which is read directly from the (unverified) `x-shopify-shop-domain` header: [2](#0-1) [3](#0-2) 

Because the app's `client_secret` (`api_secret_key`) is shared across all shops that install the app, any legitimate merchant who installs the app can capture a genuinely-Shopify-signed webhook (valid HMAC over a body they control, e.g. by creating an order in their own store). They can then replay that exact `raw_body` + `hmac` pair to the app's webhook endpoint while forging the `x-shopify-shop-domain` header (and even the `topic` header, similarly unverified: [4](#0-3) ) to claim it belongs to a different (victim) shop. `HmacValidator.validate` will still pass because `shop` is not part of the signed content, and the handler will process attacker-controlled body data tagged as belonging to a shop the attacker does not own.

This is the direct analog of the reported bug class: a field (`shop`) is acted upon by the business logic (used to key session lookups, job queues, per-tenant records, etc., as shown in the documented handler example: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) but is not covered by the same integrity check (`HMAC`) that gates whether the request is trusted at all — exactly like the deposit cap being adjusted for one identity but not restored/verified against the same identity on refund.

### Impact Explanation
This allows a malicious but "legitimate" app installer (any internet user who installs the public app on their own store — no special credentials, access tokens, or `api_secret_key` needed) to inject spoofed webhook events attributed to an arbitrary victim shop into the host application's business logic. If the host app trusts `data.shop` (as the gem's own documentation instructs it to) to route the webhook payload to the correct tenant's session/data/queue, this is a cross-tenant data injection: attacker-controlled data is processed as if it came from a shop the attacker doesn't control. Depending on how the host app uses `shop` downstream, this can corrupt or trigger actions against another tenant's data — matching the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high in real deployments: the vulnerability only requires (a) installing the target app on an attacker-controlled Shopify dev/free store (something any internet user can do for a public app) to obtain a validly-signed body+HMAC pair, and (b) sending a crafted HTTP POST to the app's public webhook endpoint with a forged `shop` header — no secrets or victim credentials required. The main constraint is that the host application must key sensitive per-tenant behavior off `data.shop` without independent verification, which the gem's own documentation explicitly recommends doing.

### Recommendation
Include the `shop` (and ideally `topic`) header value in the HMAC-signed content the same way `AuthQuery#to_signable_string` binds `shop` into its signature, or otherwise cryptographically bind the shop domain to the verified payload before it is trusted by the caller. At minimum, document that `request.shop` is unauthenticated and must be independently cross-checked against the shop associated with a valid registered webhook subscription/session before being used for tenant-sensitive routing.

### Proof of Concept
1. Install the target Shopify app on attacker-owned store `attacker.myshopify.com`.
2. Trigger an event (e.g. create an order) to receive a legitimate webhook POST to the app's registered endpoint, with headers `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, and body `B`.
3. Replay the exact same body `B` and `x-shopify-hmac-sha256: H` to the same endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(B, api_secret_key)` and it matches `H` (unchanged), so validation succeeds via `Registry.process`: [5](#0-4) 
5. `WebhookMetadata.new(... shop: request.shop ...)` now reports `shop: "victim-shop.myshopify.com"` with attacker-controlled body `B`, and the app's handler processes/queues this as data belonging to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-18)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
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
