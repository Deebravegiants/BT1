### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate` succeeds, but the HMAC signature only covers the raw request body, not the `shop`, `topic`, `webhook_id`, or `api_version` values that are read from HTTP headers and handed to the application's handler as trusted identity fields.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and its `to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly, unauthenticated, from HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, etc., and dispatches it to the app's handler: [3](#0-2) 

The documentation reinforces the false impression that the whole request — not just the body bytes — has been authenticated: "This will verify the request did indeed come from Shopify and then call the specified handler." [4](#0-3) 

This breaks the identity binding `shop header verified == shop header used by the app`. Because the HMAC only signs body bytes, an unprivileged internet user who legitimately receives one authentic webhook for their own shop (a valid `raw_body` + `x-shopify-hmac-sha256` pair, computed by Shopify itself using the app's `client_secret`) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value (e.g., a victim shop's domain). `HmacValidator.validate` will still return `true`, because it only re-computes the HMAC over `@raw_body`, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen, unauthenticated value.

### Impact Explanation
Any application that uses `data.shop` from the handler to key persistence, look up install/session state, or route processing (exactly as shown in the gem's own documented usage example) can be tricked into attributing an unprivileged user's own webhook data to another tenant/shop, i.e., cross-tenant data association. This matches the "cross-tenant access" impact category, since a value that is used to determine tenant identity is not covered by the authenticity check that is documented to authenticate the whole request.

### Likelihood Explanation
Likelihood is limited by the fact that the attacker can only replay body content they already legitimately received for their own shop (they cannot forge or alter the body content, since that would break the HMAC). The exploit is a replay/header-substitution attack requiring only a normal Shopify webhook subscription on the attacker's own shop and the ability to send an HTTP POST — no special privileges, tokens, or `client_secret` access are required by the attacker themselves.

### Recommendation
`Registry.process` (or `Request`) should require and verify that the `shop` header value matches a shop that the app has an active session for, and/or the gem should more clearly document that only body bytes are authenticated by `HmacValidator.validate`, and that `shop`/`topic`/`webhook_id`/`api_version` headers must be independently cross-checked by the host application against known/installed shop records before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker's own shop installs the app and receives a legitimate webhook: `raw_body = '{"id":1}'`, headers include `x-shopify-hmac-sha256: <valid HMAC over raw_body computed by Shopify>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the tampered headers; `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only and it matches (per `lib/shopify_api/utils/hmac_validator.rb`).
4. `Registry.process` calls the app handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id"=>1}, ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
