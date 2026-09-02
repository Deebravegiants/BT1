This confirms the finding: `ShopifyAPI::Webhooks::Request#to_signable_string` (used by `HmacValidator.validate`) signs only `@raw_body`, while `shop` is read from the `shop-domain` header and is never included in the HMAC computation.### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `X-Shopify-Shop-Domain` / `shopify-shop-domain` header, but `HmacValidator` only verifies the HMAC over the raw request body (`to_signable_string` returns `@raw_body`). The identity binding "shop the webhook is attributed to" == "shop the HMAC was computed for" is never enforced, so the value handed to the app's webhook handler as the tenant identifier is attacker-controllable while still passing signature verification.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor simply reads an untrusted header with no cross-check against anything signed: [2](#0-1) 

`HmacValidator.validate_signature` computes the signature purely from `to_signable_string` (i.e., the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` calls `Utils::HmacValidator.validate(request)` — which only proves the body/secret pairing — and then unconditionally dispatches the handler using `request.shop`, the unauthenticated header value, as the tenant identity: [4](#0-3) 

Equality the code should enforce but doesn't:
`shop attributed to the webhook (used by the app's handler for tenant lookup)` == `shop bound into the HMAC-verified payload`.

Because the app's single `client_secret` (api_secret_key) is shared across every shop that installs the app, any attacker who can install the app on their own (e.g., free/dev) store receives real, validly-signed webhook deliveries for that store. Since the shop header is not part of the signed content, the attacker can capture one such valid `(raw_body, hmac)` pair and replay it directly to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will still return `true` (the body/HMAC pair is genuine and secret-bound), and `Registry.process` will invoke the app's `WebhookHandler#handle` with `data.shop` set to the victim's domain and `data.body` containing attacker-controlled/attacker's-own-shop content.

### Impact Explanation
This breaks the shop/tenant authentication boundary the gem's webhook processing is meant to provide: `Registry.process`'s only job is to assert "this payload legitimately came from Shopify for this shop," but it only proves "this payload legitimately came from Shopify for *some* shop belonging to this app," and the tenant binding is left to be forged via a plain HTTP header. Any host application that (reasonably, per the gem's own documented usage in `docs/usage/webhooks.md`) trusts `data.shop` to key session/tenant lookups will process attacker-supplied webhook content under a spoofed victim shop identity — a cross-tenant access primitive originating entirely from this gem's verification contract.

### Likelihood Explanation
Requires an attacker to be able to install the app on at least one shop (trivial for dev/free stores, which is the normal minimum bar for testing an app) and to post directly to the app's public webhook callback URL with forged headers, which is straightforward since the endpoint is a normal public HTTP route and the gem's `Request#initialize` header parsing accepts either `x-shopify-*` or `shopify-*` prefixed headers without any additional origin restriction. No API secret, access token, or privileged access is required.

### Recommendation
Bind the `shop` identity into the HMAC-verified payload before it is trusted as the tenant key, e.g., by validating the returned `webhook_id`/`shop` pair against a per-shop registration record obtained through an authenticated channel, or by requiring/validating a Shopify-issued mechanism (such as looking up the destination shop's stored offline session) rather than trusting `shopify-shop-domain` at face value in `WebhookMetadata`/`Registry.process`.

### Proof of Concept
1. App developer installs the app onto `attacker.myshopify.com` (a store they control) and registers a webhook, e.g., `orders/create`.
2. Shopify sends a legitimate webhook to the app's endpoint:
   - Headers: `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of raw body>`
   - Body: attacker-controlled JSON (attacker fully controls their own store's order data).
3. Attacker captures this raw body and its valid HMAC value.
4. Attacker replays the exact same `(raw_body, hmac)` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`: [5](#0-4) 
   This returns `true` because the HMAC only covers `raw_body`, which is unchanged and correctly signed.
6. `handler.handle` is invoked with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: <attacker's own order data>, ...)`, causing the host app to process attacker-controlled data under the victim shop's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
