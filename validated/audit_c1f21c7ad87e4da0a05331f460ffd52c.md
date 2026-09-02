### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates the webhook's HMAC signature and then dispatches the handler using `request.shop`, but the HMAC is computed only over the raw request body — never over the `shop` (or `topic`/`webhook-id`) header. Any party who can obtain one valid `(body, hmac)` pair signed with the app's shared secret (e.g. by being a merchant with the app installed on their own store) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header, and the gem will accept it as an authentic webhook "from" that other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from an unauthenticated HTTP header with no cryptographic binding to the body that was signed: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate`, which only checks `verifiable_query.to_signable_string` (i.e., the body) against the secret, and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The identity binding that should hold is:
`HMAC_valid(body, secret) == true` should imply `shop == the shop Shopify actually generated this signed body for`.

In reality the equality that holds is only `HMAC_valid(body, secret) == true`, with `shop` supplied out-of-band and unauthenticated. Since a single app-level `api_secret_key` is shared across every merchant that installs the app, any merchant who legitimately receives a real webhook delivery for their own shop (body + valid HMAC, both known to that merchant since the delivery is HTTP POSTed to their configured endpoint, which they control) can resend that exact same body and HMAC value to the app's webhook endpoint while swapping the `x-shopify-shop-domain` header to name a different, victim shop. `HmacValidator.validate` will still pass because it never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop.

### Impact Explanation
This breaks the tenant boundary that webhook processing is supposed to enforce: the gem asserts to the host application "this authenticated payload came from shop X," when X was never actually validated. If the host application uses `WebhookMetadata#shop` to select the tenant record to update (the documented, expected use of the field), an attacker-controlled shop can inject a webhook payload attributed to any other shop's domain, leading to cross-tenant data corruption/exfiltration. This satisfies the Critical bar for cross-tenant access.

### Likelihood Explanation
Likely exploitable by any merchant with a legitimate install of the target app (an "unprivileged internet user" relative to other tenants of the same app): they need only capture one webhook delivery destined for their own store (trivial, since they control the receiving endpoint) and replay it with a modified shop header. No access to the app's `client_secret`/`api_secret_key` is required — only knowledge of one valid signed body, which every installed merchant already possesses.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signed material, or otherwise cryptographically bind the `shop` claim to the payload before trusting it — e.g., verify the header value against an out-of-band trusted registration record, or require `Registry.process` to reject webhooks whose `shop` was not independently confirmed. At minimum, document prominently that `request.shop` is unauthenticated and must not be used as a tenant key without independent verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` and configures/observes the webhook endpoint (e.g. `orders/create`) to capture a legitimate delivery: body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker POSTs to the app's webhook endpoint the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(api_secret_key, B)`, which still equals `H`, so validation succeeds.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-supplied data under the victim shop's identity.

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
