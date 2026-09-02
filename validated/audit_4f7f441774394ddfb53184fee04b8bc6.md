### Title
Webhook shop-tenant identity spoofing via unsigned `X-Shopify-Shop-Domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) used to process an inbound webhook from an HTTP header that is never covered by the HMAC signature check, letting anyone who can obtain one validly-signed webhook body (e.g. by installing the app on their own store) relabel that request as belonging to a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` validates the webhook solely by comparing this signable string's HMAC against the `hmac-sha256` header via `Utils::HmacValidator.validate(request)` [2](#0-1) . However, the tenant identity used downstream — `request.shop` — is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2)  and is not part of the signed payload. `Registry.process` passes this unverified `shop` straight into `WebhookMetadata` for the handler to act on: [2](#0-1) .

The binding that should hold is: `shop (used for tenant dispatch) == shop (covered by HMAC)`. Here it is instead: `shop (used for tenant dispatch) == shop (header value, unauthenticated)`, while only `raw_body` is authenticated. Because the HMAC key (the app's `client_secret`) is shared across all shops that install the app, a genuine webhook delivery for the attacker's own store — legitimately signed by Shopify — produces a valid `hmac-sha256`/body pair usable with *any* shop-domain header, since the header is excluded from the signable string.

### Impact Explanation
An attacker who installs the app on their own store receives real, validly-signed webhook deliveries (body + `hmac-sha256` header) from Shopify. By replaying that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain, the request still passes `HmacValidator.validate` (only `raw_body` is checked) but is dispatched to the handler as if it originated from the victim tenant (`WebhookMetadata.new(topic:, shop: request.shop, body: request.parsed_body, ...)`). This breaks the shop/tenant identity boundary: attacker-controlled body content (email addresses, order data, customer data, redact/data-request payloads, etc., depending on topic) is processed under a victim shop's identity, enabling cross-tenant data injection, corruption of a victim merchant's records, or forged mandatory-compliance webhooks (`shop/redact`, `customers/redact`, `customers/data_request`) attributed to a shop the attacker does not control. This satisfies the Critical criterion of cross-tenant access.

### Likelihood Explanation
Likelihood is high for any app that trusts `Request#shop` for per-tenant business logic: the only prerequisite is that the attacker can install the app on a shop they control (an ordinary, unprivileged action available to any merchant/developer) to obtain one legitimately signed webhook body, then replay it to the app's public webhook endpoint with a modified shop header — no knowledge of `client_secret` or any Shopify credential is required, and no TLS interception is needed since the attacker is the legitimate recipient of their own webhook.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signable string, or otherwise cryptographically bind the shop identity to the signed payload, so that `Utils::HmacValidator.validate` fails if the shop header does not match the value Shopify actually signed for that delivery. At minimum, document and enforce that consumers must independently verify `request.shop` against a known/installed-shop list before trusting it, rather than treating a passing HMAC check as proof the shop header is authentic.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid because computed by Shopify over `B` using the app's shared `client_secret`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Replay the exact same request to the app's webhook endpoint, changing only the header to `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (`= B`, unchanged) and compares to `H` — validation passes [4](#0-3) .
4. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker's parsed body>, ...)` [5](#0-4) , causing the app to process attacker-supplied data under the victim's tenant identity.

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
