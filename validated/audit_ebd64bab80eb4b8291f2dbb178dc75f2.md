### Title
Webhook `shop` (and `topic`/`webhook-id`) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the `shop-domain` (and `topic`, `webhook-id`) HTTP headers — none of which are included in the signed payload — when dispatching the event to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers that are never mixed into the signed string: [2](#0-1) 

`Registry.process` validates the HMAC (`Utils::HmacValidator.validate(request)`, which hashes `request.to_signable_string`, i.e., the raw body only) and then, once validation succeeds, immediately uses `request.shop` — an unauthenticated header — as the tenant identity handed to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop-domain header == shop bound inside the HMAC-signed payload`. In this implementation that equality is never enforced — the HMAC only certifies the bytes of `raw_body`, not the header claiming which shop the body belongs to. Since a single app has one `client_secret` shared across every installed shop, HMACs are valid across all of an app's shops/tenants. An attacker who controls their own shop (trivial to create, e.g., a free Shopify partner/dev store) and installs the target app can capture a genuine `(raw_body, hmac)` pair from a webhook Shopify sends them, then replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header with an arbitrary victim shop domain. The HMAC still validates (it only covers the body), so `Registry.process` will call the app's handler with `WebhookMetadata.new(shop: request.shop, ...)` pointing at the attacker-chosen victim shop, even though the payload actually originated from the attacker's own store.

### Impact Explanation
This breaks the tenant/shop identity binding for any host application that uses `WebhookMetadata#shop` (or `Request#shop`) to key data lookups, cache invalidation, redaction/GDPR actions, or any per-tenant processing — precisely the intended use documented for `WebhookHandler#handle`. An attacker can inject events attributed to a shop they do not own/control, i.e., cross-tenant access/confusion, without needing the app's `client_secret`, an access token, or any privileged account.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on a shop the attacker controls (free/self-serve), (2) capturing one legitimate webhook body+HMAC pair sent to their own endpoint, and (3) POSTing it to the shared webhook endpoint with a forged `shop-domain` header. No secrets, tokens, or Shopify-side privileges are needed — only public/unprivileged interaction with the app's own webhook endpoint, matching the report's "attacker manipulates an unbound field to break an identity binding" pattern.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook-id`) into the signed material verified against the HMAC, or independently verify that the `shop-domain` header matches a shop for which this raw body/HMAC combination was actually generated (e.g., by including the header value in `to_signable_string`, or by requiring the caller to supply/verify the expected shop out-of-band before trusting the header). At minimum, document that `request.shop` is unauthenticated and must not be used for authorization decisions without additional binding.

### Proof of Concept
1. Attacker creates/uses a shop (`attacker.myshopify.com`) with the target app installed; Shopify sends a legitimate webhook: `raw_body = B`, header `X-Shopify-Hmac-Sha256 = HMAC(secret, B)`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker replays the exact same `raw_body = B` and the same `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, request.to_signable_string)` = `HMAC(secret, B)`, which matches — validation passes (`lib/shopify_api/webhooks/registry.rb:190`).
4. `Registry.process` dispatches to the handler with `shop: request.shop` = `"victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198`), even though the event content actually came from the attacker's own shop — cross-tenant identity confusion confirmed.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
