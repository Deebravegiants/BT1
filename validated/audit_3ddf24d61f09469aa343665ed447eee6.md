Confirmed: the `Registry.process` flow validates only the webhook body against the HMAC and never verifies that the `shop` header matches the tenant the app expects. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC only to the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and never included in the signed material. `Registry.process` validates the HMAC and then blindly trusts `request.shop` when constructing `WebhookMetadata` passed to the app's handler.

### Finding Description
`HmacValidator.validate` computes and compares the HMAC solely over `verifiable_query.to_signable_string`. For webhook requests, that method returns only `@raw_body`: [1](#0-0) 

However, `request.shop` (and `topic`, `webhook_id`, `api_version`) is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed data: [4](#0-3) 

`Registry.process` verifies only the body's HMAC and then forwards `request.shop` unchecked to the app's webhook handler: [3](#0-2) 

The identity binding that should hold is: `shop header value == shop that produced/authorized this signed payload`. Because the header is outside the HMAC, that equality is never enforced by the gem. Any party who can produce one validly-HMAC-signed body+header set for their own shop (e.g., an attacker who installs the app on their own store and receives a real, correctly-signed webhook from Shopify for a topic/body they control, such as `customers/data_request` or any webhook whose body content they influence) can replay that exact `raw_body` + `hmac` pair while substituting an arbitrary `shop-domain` header value naming a different merchant. `HmacValidator.validate` still passes (it only checks the body), and the handler receives `WebhookMetadata` with `shop` set to the attacker-chosen tenant, causing the host application to act on/attribute the payload to a shop that never actually sent or authorized it.

### Impact Explanation
This is a cross-tenant identity confusion: the gem hands the host application webhook data tagged with a shop identity that was never cryptographically bound to that data. Any downstream logic that keys storage, redaction, deprovisioning, or entitlement decisions off `WebhookMetadata#shop` (which is exactly the documented intended use, e.g. mandatory `shop/redact`, `customers/redact`, `customers/data_request` topics) can be tricked into applying another merchant's webhook data/actions to a shop the attacker chooses. This matches the in-scope "Critical - cross-tenant access" category since the trust boundary between tenants is broken entirely within the gem's own verification logic.

### Likelihood Explanation
Medium-High: the attacker needs one genuine, HMAC-valid webhook delivery under their own control (trivial to obtain — installing the app on an attacker-owned store and using standard webhook payload contents such as a `customers/data_request` request they trigger, or any webhook whose body is attacker-influenced/predictable), then can freely replay it with any spoofed `shop-domain` header value to the app's webhook endpoint. No secret material or privileged access is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` value to the verified body before constructing `WebhookMetadata`, e.g., cross-check `request.shop` against a shop known to be associated with the specific `access_token`/session context of the receiving endpoint, or require Shopify to sign headers together with the body and validate that signature in `HmacValidator`.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers a webhook whose body content they control or can predict (e.g., a mandatory compliance topic or an order/product webhook with attacker-set fields). Shopify delivers it with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-raw_body>`, and the raw body.
2. Attacker replays the identical HTTP POST to the app's webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` unchanged but rewriting `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against the secret — validation succeeds.
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though `victim-shop` never sent this payload, causing the host app to act on forged tenant data.

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
