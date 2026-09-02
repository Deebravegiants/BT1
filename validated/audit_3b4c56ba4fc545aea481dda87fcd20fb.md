### Title
Webhook shop identity spoofing via replay — HMAC covers only the raw body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then hands the caller-supplied, unauthenticated `shop-domain` header straight to the app's handler as the trusted tenant identity. Because the same `client_secret` is shared across every shop that installs the app, any merchant who legitimately receives a signed webhook for their own shop can replay that exact body/HMAC pair to the app's webhook endpoint while substituting a different `shopify-shop-domain` header, and the gem will report it as an authenticated webhook "from" the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` — the value that is HMAC-verified — is defined as only the raw body: [1](#0-0) 

The `shop` (and `topic`, `api_version`, `webhook_id`) values are read from separate, unsigned HTTP headers: [2](#0-1) 

`Registry.process` verifies the HMAC via `Utils::HmacValidator.validate(request)` — which only checks `request.to_signable_string` (the raw body) against `request.hmac` — and, once that single check passes, immediately trusts `request.shop` as the tenant identity and forwards it to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` confirms only that the body's signature matches `Context.api_secret_key` — it has no notion of which shop the body came from: [4](#0-3) 

The identity binding that should hold is:
`shop header used to build WebhookMetadata` == `shop cryptographically bound to the signed bytes`

That equality does not hold: the HMAC only binds the body bytes to the app's secret, not to any particular shop. Since `client_secret`/`api_secret_key` is a single app-wide secret (not per-shop), a genuine webhook received by shop A carries a signature that is equally "valid" no matter which `shop-domain` header accompanies it. An attacker who is a legitimate (but malicious) merchant on shop A can:
1. Install the app on their own shop A and receive a real, correctly-signed webhook (`raw_body`, `hmac`) for an event on shop A.
2. Replay that identical `raw_body`/`hmac` pair to the app's webhook endpoint, but change the `X-Shopify-Shop-Domain` header to shop B (a different tenant of the same app).
3. `Utils::HmacValidator.validate(request)` still succeeds (it never inspects the shop header), so `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "shop-B.myshopify.com", body: <shop A's real payload>, ...)`.

This directly matches the "field acted on but not covered by the HMAC" analog described in the rules: `shop` is used to route/attribute webhook data but is excluded from the signed payload.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: cross-tenant data can be injected/misattributed to any other shop using the same app, without needing the app's secret, an access token, or any credentials belonging to the victim shop. Depending on what the host app's webhook handler does with `data.shop` (e.g., look up a merchant's session/store record, trigger fulfillment/inventory actions, or write to a shop-scoped database row keyed by `shop`), this can result in cross-tenant state corruption or cross-tenant access to another merchant's records — a Critical-class impact per the rules ("cross-tenant access").

### Likelihood Explanation
Any customer of the app who installs it on their own shop can obtain a fully legitimate signed webhook payload for that shop at will (e.g., by triggering an order/update event). Replaying that body with a spoofed shop header requires no special access beyond being a normal, unprivileged merchant/user of the app — it is a pure HTTP replay with header substitution.

### Recommendation
Bind the shop identity into the verified payload rather than trusting an unauthenticated header:
- Include the `shop-domain` (and ideally `topic`, `webhook_id`) header value in the string that is HMAC-verified (`to_signable_string`), so any header tampering invalidates the signature, or
- Cross-check the `shop-domain` header against the shop encoded inside the verified body (Shopify webhook payloads include the shop's data), rejecting the webhook if they diverge, before constructing `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the raw POST body and the `X-Shopify-Hmac-Sha256` header sent by Shopify (both are valid for the app's shared `client_secret`).
2. Send a new POST request to the app's webhook endpoint using the exact same body and `X-Shopify-Hmac-Sha256` value, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) raw body against the (unchanged, valid) HMAC: [5](#0-4) 
4. The app's handler receives `WebhookMetadata` claiming the event is from `victim-shop.myshopify.com`, even though the payload actually originated from the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
