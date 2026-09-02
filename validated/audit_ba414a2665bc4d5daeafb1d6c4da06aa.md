### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read straight from an HTTP header, but the HMAC signature that `HmacValidator` verifies only covers the raw request body. An attacker who can obtain any one valid `(raw_body, hmac)` pair for a topic (trivially available to them by installing the app on their own store and receiving a real webhook) can replay that exact body/signature pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for an arbitrary victim shop. `HmacValidator.validate` still returns `true`, because the shop field is never part of the signed content.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is populated from the `shopify-shop-domain` / `x-shopify-shop-domain` header, entirely independent of the signed content: [2](#0-1) 

`HmacValidator.validate_signature` computes the signature purely over `verifiable_query.to_signable_string` (i.e. the raw body) and compares it to the `hmac` field with `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to hand the (attacker-controlled) `request.shop` straight to the app's handler as the tenant identity, with no secondary check that `shop` is consistent with anything cryptographically verified: [4](#0-3) 

The binding that is broken, expressed as an equality that should hold but doesn't:
`shop_header_used_as_tenant_identity == shop_bound_by(hmac_signature)` — in this code the left side is attacker-controllable while the right side never includes `shop` at all, so the two are permanently decoupled. This is the same bug class as the External Report: a value that participates in a security decision (there, `addendA1`; here, the tenant identity `shop`) is not actually covered by the check that is supposed to make it trustworthy (there, the overflow/equality check; here, the HMAC signature).

### Impact Explanation
Any actor able to install the target app on a store they control (an ordinary, unprivileged action — no credentials, tokens, or secrets required) can harvest a valid `(raw_body, hmac)` pair from a genuine webhook Shopify sends them, then POST that identical pair to the app's public webhook endpoint with the `shop` header rewritten to a victim merchant's domain. `HmacValidator.validate` passes because it never inspected `shop`. The handler then executes tenant-scoped logic (e.g. `shop/redact`, `customers/redact`, `app/uninstalled`, `shop/update`, or any custom handler that uses `WebhookMetadata#shop` to select which merchant's session/data to mutate) against a shop the attacker does not control. This is a cross-tenant integrity/authorization break rooted entirely in this gem's own webhook verification primitive (`HmacValidator` + `Webhooks::Request`), not in any misuse of a documented contract — the gem documents `HmacValidator.validate` as sufficient proof of authenticity for the whole `Request`, including `shop`.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker needs (a) the ability to install the app on any store (public/dev store, trivial), (b) the app's webhook endpoint to be reachable directly over the internet (true by construction, since Shopify itself must reach it), and (c) the handler to key any tenant-sensitive action off `WebhookMetadata#shop`/`request.shop` rather than an independently-verified session lookup. Condition (c) is exactly the pattern the gem's own `Registry#process` implementation encourages, since it forwards `request.shop` unchecked.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`) to the cryptographic check instead of trusting it purely from headers:
- Include the shop domain (and topic) in the signable content used by `HmacValidator`, or
- Require callers of `Registry.process`/`WebhookMetadata` to cross-verify `request.shop` against a shop they already have an established, authenticated session for before acting, and document this requirement prominently, or
- At minimum, warn in `Webhooks::Request`/`HmacValidator` documentation that `shop`, `topic`, and `webhook_id` are **not** covered by the HMAC and must not be trusted for authorization decisions on their own.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled test store `attacker-shop.myshopify.com`.
2. Trigger any webhook topic (e.g. `app/uninstalled`) and capture the exact `raw_body` and `x-shopify-hmac-sha256` header Shopify sent to the app's webhook endpoint — this pair is valid because it was legitimately signed by Shopify with the app's `client_secret`, which the attacker never needs to know.
3. Replay an HTTP POST to the same app's public webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes (per `lib/shopify_api/utils/hmac_validator.rb:26-31`, only `raw_body` is checked). The handler then receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` (per `lib/shopify_api/webhooks/registry.rb:198-199`), and executes tenant-scoped logic against the victim's shop record, even though the victim never sent this webhook and the attacker has no relationship with that shop.

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
