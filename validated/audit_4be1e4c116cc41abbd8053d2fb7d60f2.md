### Title
Webhook `shop` field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates the HMAC signature over the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from unauthenticated HTTP headers. `Registry.process` accepts any request whose body HMAC is valid and then forwards the header-derived `shop` value to the host application's webhook handler, without any binding between the authenticated bytes and the shop identity.

### Finding Description
`HmacValidator.validate` verifies the signature against `verifiable_query.to_signable_string`, and for webhooks `to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

The `shop` accessor is derived purely from the `shopify-shop-domain` (or `x-shopify-shop-domain`) HTTP header, which is not part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the body, then immediately trusts `request.shop` and hands it to the registered handler as the authoritative tenant identifier: [3](#0-2) 

The identity binding that should hold is: `shop that produced the HMAC-authenticated bytes == shop attributed to the webhook event`. Here, the HMAC only authenticates the body bytes; the `shop` field consumed by the handler comes from a header entirely outside the signed scope. Since any legitimate app installer (any unprivileged internet user who installs the app on their own free/dev shop) can obtain real Shopify webhooks with a valid HMAC for their own shop and body content they can influence (e.g., a webhook topic/body they trigger themselves, such as `app/uninstalled` or any event they can produce on their own store), they can replay that exact `(raw_body, hmac)` pair while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with an arbitrary victim shop domain. `Utils::HmacValidator.validate` still succeeds because it only checks the body against the secret, and `Registry.process` passes the attacker-chosen `shop` through to `WebhookMetadata` unchanged.

### Impact Explanation
Host applications built on this gem are documented to trust `ShopifyAPI::Webhooks::Registry.process` to have "verif[ied] the request did indeed come from Shopify" (per `docs/usage/webhooks.md`) and then use `data.shop` from `WebhookMetadata` to look up the merchant's stored session/access token and perform privileged actions (e.g., sync data, revoke access, delete data on `shop/redact`) attributed to that shop. Because `shop` is not bound to the HMAC, an attacker can forge the shop identity of a webhook while keeping a valid signature, causing the host app to execute shop-scoped, credentialed operations against a victim tenant chosen by the attacker — a cross-tenant confusion/spoofing vector.

### Likelihood Explanation
Any developer/attacker can install the target app on a shop they control (free trial/dev store) to obtain a genuinely HMAC-signed webhook body, then simply resend it over HTTP with a modified shop-domain header to the app's webhook endpoint. No access token, `client_secret`, or privileged access is required — only observation of one's own legitimately received webhook and header modification, both of which are unprivileged and within the described gem's own verification flow (`Registry.process` / `HmacValidator.validate`).

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) inside the HMAC-signed scope, or otherwise cryptographically bind the header-derived `shop` to the authenticated body — for example, require the host app / gem to independently confirm that `shop` corresponds to a shop with an active, previously-established session/webhook registration before trusting `WebhookMetadata#shop`, rather than trusting the raw header value once the body HMAC passes.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com` and trigger any subscribed webhook (e.g. `app/uninstalled`), capturing the raw body `B` and the resulting `X-Shopify-Hmac-Sha256: H` header, where `H = HMAC-SHA256(client_secret, B)`.
2. Send a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), and header `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` builds successfully; `Utils::HmacValidator.validate(request)` returns `true` because it only checks `HMAC(client_secret, B) == H`.
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)`, causing the host app to treat the forged request as an authentic webhook from `victim.myshopify.com`, per [3](#0-2) .

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
