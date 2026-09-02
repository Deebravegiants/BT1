### Title
Cross-tenant shop attribution in `Webhooks::Registry.process` due to `shop-domain` header not covered by HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so the HMAC that `HmacValidator.validate` checks in `Registry.process` [2](#0-1)  authenticates only the body bytes. The `shop` value used to attribute the webhook to a tenant comes from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header [3](#0-2)  and is passed straight into the handler as the tenant identity [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop` used by the host application to select/route tenant data == `shop` value cryptographically bound by the HMAC signature. Here that equality is broken — the HMAC only covers `@raw_body` [1](#0-0) , while `request.shop` is read directly from an HTTP header outside of the signed material [3](#0-2) .

Critically, `Context.api_secret_key` used by `HmacValidator` (`lib/shopify_api/utils/hmac_validator.rb`) is the app's single `client_secret`, shared across every shop that installs the app — it is not shop-specific. Any unprivileged internet user can install the target app on their own shop (free/dev store) and thereby legitimately receive real webhook deliveries, each with a raw body and a correctly computed HMAC signed with the app's shared secret. Because `to_signable_string` excludes the `shop-domain` header, that same `(raw_body, hmac)` pair remains valid regardless of which `shop-domain` header value accompanies the request. An attacker who controls their own webhook delivery endpoint (or replays a captured request to the host app's webhook endpoint with the header value swapped to a victim's shop domain) produces a request that:
- passes `Utils::HmacValidator.validate(request)` in `Registry.process` [5](#0-4) , and
- is delivered to the handler tagged with an attacker-chosen `shop` value [4](#0-3) .

Any host application logic that keys session lookup, data writes, or authorization decisions off `WebhookMetadata#shop` (as intended/documented usage of this gem's webhook API) will act on data attributed to the wrong tenant, using a body that was never actually associated with that tenant by Shopify.

### Impact Explanation
This is a cross-tenant identity-confusion vector reachable by any unprivileged user who can install the app once (a normal, unprivileged action) and does not require possession of `api_secret_key`, an access token, or any victim credential. It matches the Critical "cross-tenant access" impact category: an attacker-controlled webhook body can be attributed to an arbitrary victim shop domain in the host application's webhook processing pipeline, because the tenant-selecting field (`shop`) is not part of the value verified by `HmacValidator`.

### Likelihood Explanation
Likelihood is high for any host application that trusts `WebhookMetadata#shop` as an authenticated tenant identifier after `Registry.process` succeeds (which is the documented, expected usage pattern of this gem's webhook API). No secret material beyond what any app installer already legitimately possesses (the ability to receive real webhooks for their own shop) is required, and the header is trivially attacker-controlled at the HTTP layer.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`/`api-version`) header values in the signable string used for HMAC verification, or otherwise cryptographically bind the shop identity to the verified payload, so that `Utils::HmacValidator.validate` fails if the `shop-domain` header is altered relative to the body that was actually signed for that tenant.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; the app's shared `client_secret` is used to sign webhook deliveries, so the attacker receives valid `(raw_body, x-shopify-hmac-sha256)` pairs for their own tenant.
2. Attacker crafts an HTTP request to the host application's webhook endpoint using the captured `raw_body` and `x-shopify-hmac-sha256` value unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request object; `to_signable_string` only returns `raw_body`, unaffected by the header change [1](#0-0) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and succeeds [5](#0-4) .
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)` [4](#0-3) , causing the host app to process attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-196)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
