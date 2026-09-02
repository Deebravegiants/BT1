### Title
Webhook shop identity spoofing via HMAC that only covers the request body, not the shop-domain header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, while the `shop` value used downstream to attribute the webhook to a tenant is read from an HTTP header that is never included in the signed bytes. An attacker who obtains one authentically-signed webhook (body + HMAC) can replay it to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header, and `Registry.process` will accept it as valid and dispatch it under the attacker-chosen shop identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived independently from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signable string: [2](#0-1) 

`Registry.process` validates the HMAC against the body only (`Utils::HmacValidator.validate(request)` → `verifiable_query.to_signable_string`), and then unconditionally trusts `request.shop` to build the metadata handed to the app's handler: [3](#0-2) 

The identity binding that should hold is:
`bytes_verified_by_HMAC == bytes_that_determine_tenant("shop")`

Here that equality is broken: `bytes_verified_by_HMAC = raw_body`, while `bytes_that_determine_tenant = headers["shop-domain"]`. Because the header is entirely outside the HMAC's scope, the HMAC computed over a legitimate body from tenant A remains valid no matter which `shop-domain` header value is attached to the replayed request. Any actor capable of capturing one authentic `(raw_body, hmac)` pair — for example by installing the app on their own store and observing the webhooks Shopify sends to the app's endpoint, or via a logging/debug surface that echoes the raw payload — can resend that exact payload with a forged `shop-domain` header naming a different tenant. The app will process it as data belonging to that other tenant.

This directly mirrors the report's flagged bug class of "a field acted on but not covered by the HMAC": the `shop` field is acted upon (used as the tenant key for the handler) but is not bound to the signature the way the `shop` field is bound to the signature in the OAuth callback's `AuthQuery` (`lib/shopify_api/auth/oauth.rb`), where `shop` participates in `to_signable_string`.

### Impact Explanation
This allows cross-tenant webhook injection: an attacker can make the host application ingest or act on data (order/customer/app events) while attributing it to a shop other than the one that actually produced it, without needing `api_secret_key`, an access token, or TLS interception — only capture of one legitimately-signed payload for a shop the attacker controls or has visibility into. Depending on how the host app's webhook handlers use `data.shop` (e.g., looking up sessions, writing tenant-scoped records), this can lead to cross-tenant data corruption or unauthorized cross-tenant actions, which maps to the "Critical — cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one valid `(raw_body, hmac)` pair. The simplest path is installing the target app on the attacker's own (unprivileged) shop or dev store — this is available to any internet user without special privileges — and capturing the webhook Shopify legitimately sends for that shop. The attacker then only needs to change the `shop-domain` header value in a replayed POST to the app's public webhook endpoint. No secrets, tokens, or MITM capability are required, making this readily reachable for a motivated unprivileged actor, though it depends on the attacker being able to trigger and observe (or otherwise obtain) an authentic webhook body first.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the HMAC-signed content, or otherwise cryptographically bind the shop domain to the signed body before trusting it in `Registry.process`. At minimum, this gem's documentation/implementation should make explicit that `request.shop` is unauthenticated header data and instruct consuming apps to cross-check it against a shop already known/authorized for that webhook subscription (e.g., compare with the value used at webhook registration time) rather than trusting it outright.

### Proof of Concept
1. Attacker installs the app on shop `attacker-shop.myshopify.com` and triggers an event (e.g., `orders/create`), causing Shopify to POST a legitimately HMAC-signed webhook to the app's endpoint:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-of-raw-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id":123,...}
   ```
2. Attacker captures this exact `raw_body` and `X-Shopify-Hmac-Sha256` value (e.g., via their own request logs, since it's their own app installation).
3. Attacker resends the identical body and HMAC to the app's public webhook endpoint, changing only the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-hmac>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id":123,...}   # unchanged
   ```
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks the (unchanged) body against the (unchanged) HMAC — `lib/shopify_api/utils/hmac_validator.rb` lines 26-31.
5. `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb` lines 188-199), even though the payload actually originated from `attacker-shop.myshopify.com`.

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
