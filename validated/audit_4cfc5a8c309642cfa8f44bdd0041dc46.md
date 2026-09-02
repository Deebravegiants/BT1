### Title
Webhook `shop` field trusted for tenant identification without HMAC coverage - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop` header value—unverified—to the app's handler as the tenant identifier.

### Finding Description
`Utils::HmacValidator.validate` computes and compares an HMAC only over `verifiable_query.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 
None of the HTTP headers—including `shop-domain`—are part of the signed material.

`Registry.process` validates only this body HMAC and then immediately trusts `request.shop` (read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header) as the tenant identity passed into the handler: [2](#0-1) [3](#0-2) 

This is exactly the bug class in the report generalized to this gem: "a field acted on but not covered by the HMAC." The equality the code implicitly assumes is:
`shop_used_by_handler == shop_that_was_actually_HMAC-authenticated`
but in reality `shop_used_by_handler = header["shopify-shop-domain"]` while the HMAC only authenticates `raw_body`. These two are never bound together.

### Impact Explanation
Compare this to `Auth::Oauth::AuthQuery`, where the equivalent identity fields (`code`, `host`, `shop`, `state`, `timestamp`) are all included in `to_signable_string` and thus covered by the HMAC: [4](#0-3) 
The webhook path lacks this binding for `shop`.

An attacker who controls a legitimate Shopify store can trigger a real webhook for their own shop (a routine, unprivileged action), obtaining a body + a correctly computed HMAC signed with the app's shared secret for that body. They can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value (any victim shop domain). `HmacValidator.validate` still passes because it never looks at the header, and `Registry.process` forwards the attacker-chosen `shop` to the handler as if it were authenticated. If the host application uses this `shop` value to select per-tenant credentials/data (which is the very schema this gem's own `WebhookMetadata` struct—`shop:`—is designed for downstream consumers to use for tenant routing), this enables cross-tenant confusion/access, satisfying the Critical "cross-tenant access" impact bar.

### Likelihood Explanation
Reachability is high: any Shopify merchant can generate a valid webhook body+HMAC pair for their own store by performing an ordinary action (e.g., updating an order), then replay it against the target app's public webhook endpoint with a forged `shop` header — no access token, secret, or privileged account is required, satisfying the unprivileged-internet-user constraint.

### Recommendation
Bind the authenticated payload to the shop it claims to represent, e.g., include the `shop-domain` (and ideally `topic`/`webhook-id`) header values inside the signed material, or cross-check the header-derived `shop` against a shop value embedded in the HMAC-covered body/claims before trusting it for tenant lookup. At minimum, document/enforce that consumers must independently verify `shop` against their own installed-shops registry rather than treating the header as authenticated by `HmacValidator.validate`.

### Proof of Concept
1. As a merchant of `attacker-shop.myshopify.com`, trigger any webhook subscription (e.g., `orders/create`) and capture the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header `H` that Shopify computes over `B` with the app's shared secret.
2. Send a POST to the target app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request; `Utils::HmacValidator.validate` computes the HMAC over `@raw_body` only (`lib/shopify_api/webhooks/request.rb:35-38`) and it matches `H`, so validation succeeds.
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:188-199`), even though the payload was never signed for that shop.

Note: full verification of exactly how `WebhookMetadata` is consumed downstream (its exact struct definition) could not be located in the indexed code (`lib/shopify_api/webhooks/webhook_metadata.rb` was not found in the index), so the ultimate severity depends on how host applications use the `shop` field from webhook handlers; this is stated as a limitation of the available index rather than a gap in the root-cause analysis of the HMAC/header binding itself.

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
