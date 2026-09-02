This confirms the vulnerability. The `shop`, `topic`, `webhook_id`, and `api_version` fields are all read from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) but `Request#to_signable_string` returns only `@raw_body` — none of these header-derived fields are covered by the HMAC signature that `HmacValidator.validate` checks.

### Title
Webhook Tenant Identity (`shop`) Not Covered by HMAC Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field (and `topic`, `webhook_id`, `api_version`) from unauthenticated HTTP headers, while `to_signable_string` — the value verified by `Utils::HmacValidator.validate` — only covers the raw request body. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` to build `WebhookMetadata` and dispatch it to the app's handler, without that value ever being bound to the HMAC.

### Finding Description
In `lib/shopify_api/webhooks/request.rb`, `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

The HMAC that authenticates the request is computed only over the raw body: [2](#0-1) 

`Registry.process` validates only that signature, then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` that is handed to the app's handler: [3](#0-2) 

This is exactly the class of bug described in the report: a field acted on downstream (`shop`, the tenant-binding identifier) is not covered by the cryptographic check (`HmacValidator.validate`) that gates trust in the request. The equality that should hold — `shop bound in HMAC == shop delivered to handler` — never holds, because the HMAC binds only the body bytes.

### Impact Explanation
Any party who can obtain one genuine, validly-signed webhook body for *any* shop on the app (e.g., their own store, after installing the app, an action fully available to an unprivileged internet user) can replay that exact raw body to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop's domain. `Utils::HmacValidator.validate` will still succeed (it only checks the raw body against the app's `client_secret`-derived HMAC), and `Registry.process` will hand the attacker-controlled body to the handler tagged with the victim's `shop`. Because host apps are documented to key their business logic and persistence directly off `data.shop` (per `docs/usage/webhooks.md`), this allows cross-tenant data confusion/corruption — e.g. spoofing `app/uninstalled`, `shop/redact`, or resource-mutating webhooks as if they originated from a different merchant's store, without ever possessing that merchant's credentials.

### Likelihood Explanation
The prerequisite (installing the app once to obtain a single genuinely-signed webhook payload) is achievable by any unprivileged internet user for apps listed publicly or offering trial installs, and no part of the exploit requires the app's `client_secret`, an access token, or any privileged access — only replay of a previously-observed valid body with a modified header. The gem itself performs no tenant binding check between the signed bytes and the header-derived `shop`; the flaw is entirely in this library's `Request`/`Registry` code, not host-application misuse.

### Recommendation
Bind the tenant/topic identity into the signed payload validation, e.g., by including `shop`, `topic`, and `webhook_id` header values in `to_signable_string` (matching what Shopify actually signs), or by requiring host apps to independently verify that `request.shop` corresponds to a shop with an active session/installation before dispatching to a handler. At minimum, document and enforce that `shop`, `topic`, and `webhook_id` are unauthenticated and must not be trusted for authorization decisions without additional binding.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, triggers a webhook (e.g. `orders/create`), and captures the raw POST body `B` and its valid `shopify-hmac-sha256` header `H` (computed by Shopify over `B` using the app's `client_secret`).
2. Attacker sends a POST to the app's webhook endpoint with the same body `B` and same `hmac` header `H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop: "victim-shop.myshopify.com", hmac: H})` is constructed; `to_signable_string` returns `B` unchanged. [2](#0-1) 
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `B`. [4](#0-3) 
5. The app's handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and acts on attacker-controlled data as if it came from the victim's tenant. [5](#0-4)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
