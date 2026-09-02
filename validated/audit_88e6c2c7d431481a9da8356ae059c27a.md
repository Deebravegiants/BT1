### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing on a validly-signed webhook body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain` HTTP header — which is completely outside the signed bytes — as the tenant identity passed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read from a separate, unsigned header: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (i.e. the raw body) against the HMAC-SHA256 secret, and then immediately forwards `request.shop` — never re-derived from or bound to the signed payload — to the registered handler: [3](#0-2) 

The identity binding that should hold is:
`shop header used for tenant routing == shop the signed body was actually produced for`

Because the HMAC only signs the body, this equality is never enforced. An attacker who is able to obtain one genuine, validly-signed webhook body+HMAC pair from Shopify (e.g., triggered from their own store, a free trial shop, or a shop they legitimately administer) can replay that exact `raw_body` and `hmac-sha256` header to the target app's public webhook endpoint while substituting the `shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds, because it only recomputes the HMAC over the untouched raw body, and `Registry.process` passes the attacker-chosen `shop` value straight into `WebhookMetadata`/the app handler as the trusted tenant identifier.

### Impact Explanation
This breaks the tenant/shop identity boundary: the webhook payload is authenticated as "genuinely HMAC-signed by Shopify," but the shop it is attributed to is attacker-controlled. Any host application that uses `data.shop` from the handler to look up sessions, update per-shop records, or gate `shop/redact`, `customers/redact`, `customers/data_request` compliance actions will act on the wrong tenant's data using content or fields chosen by the attacker's own shop's webhook. This is a cross-tenant confusion vulnerability rooted entirely in this gem's webhook verification API (`Registry.process`, `Request`), not a misuse of undocumented behavior.

### Likelihood Explanation
Likelihood is Low: the attacker needs to obtain one valid signed webhook (achievable by owning/controlling any shop that installs the target app, or any dev/trial shop configured to send webhooks to the same app, since Shopify signs with the app's single shared secret regardless of shop), then replay it to the victim-scoped installation's webhook route with a modified `shop-domain` header. This requires no knowledge of `api_secret_key` and no access token.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-signed payload check, or independently verify that the `shop-domain` header value corresponds to a shop the receiving app instance actually expects/has an active session for, before trusting it for routing. At minimum, document that host apps must cross-check `request.shop` against known installed shops rather than treating it as authenticated by the HMAC.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any registered webhook topic (e.g. `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker crafts a new HTTP request to the app's webhook endpoint using the identical captured `raw_body` and `hmac-sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the secret (`Request#to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38`).
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the handler with `shop: request.shop == "victim-shop.myshopify.com"`, even though the body's content is entirely from `attacker-shop`, causing the host app to process attacker-controlled data under the victim shop's identity.

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
