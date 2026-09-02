## Finding

Shopify's webhook HMAC validation in this gem authenticates only the request body — not the shop that the webhook claims to be from. The `shop` value used to identify the tenant in `WebhookMetadata` comes from an HTTP header that is completely outside the HMAC's coverage, so an attacker who legitimately receives real, validly-signed webhooks for their own store (any developer can install the app on a free/dev store) can replay that exact signed body to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop, and the gem will report the request as verified and route it under the wrong tenant.

### Title
Webhook shop-domain header is unauthenticated by HMAC, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  and `HmacValidator.validate` computes/compares the HMAC exclusively over that signable string [2](#0-1) . Meanwhile `#shop` is read verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [3](#0-2) , and `Registry.process` passes that unauthenticated header value straight into the handler as the tenant identity, only checking the body HMAC: `raise ... unless Utils::HmacValidator.validate(request)` then `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) .

### Finding Description
The identity binding that should hold is: **`shop` bound in the HMAC == `shop` acted upon by the handler**. In this implementation that equality does not hold — the HMAC only binds `raw_body`, while `shop` is taken from a separate, unsigned header:

- Before: attacker has a validly-signed webhook `(raw_body=B, hmac=HMAC(secret, B), shop-domain=attacker-shop.myshopify.com)` delivered to them by Shopify for their own store.
- Attack: attacker POSTs the same `raw_body=B` and same `hmac` to the app's webhook endpoint, but sets `shop-domain: victim-shop.myshopify.com`.
- After: `Utils::HmacValidator.validate` still succeeds because it only recomputes the HMAC over `B` [1](#0-0) , and `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"` [4](#0-3) .

This is possible without ever knowing `Context.api_secret_key`, because the attacker reuses a real signature Shopify itself generated for the attacker's own (unprivileged) shop — they never need to forge an HMAC.

The gem's own documentation reinforces the false assumption that a validated webhook is fully authenticated, including the shop: "This will verify the request did indeed come from Shopify and then call the specified handler" [5](#0-4) , and describes `data.shop` simply as "The shop domain of the webhook" [6](#0-5)  with no caveat that it is unauthenticated and must be cross-checked against a registered/known shop list. The example handler in the docs uses `data.shop` directly to key downstream work [7](#0-6) , so an app author following the gem's documented usage inherits the cross-tenant confusion.

### Impact Explanation
This breaks the shop-authenticated vs. shop-acted-upon binding described in scope. A malicious but otherwise unprivileged app-installer (any developer can create a free store and install the target app) can inject fabricated events attributed to an arbitrary victim shop domain into the host app's webhook processing pipeline — e.g., triggering fulfillment, inventory, or order-processing logic for a shop they don't own, or polluting per-shop data keyed by `data.shop`. This is cross-tenant access/data confusion, matching the Critical impact category ("cross-tenant access").

### Likelihood Explanation
High for any app that follows the documented pattern of trusting `data.shop` from `Registry.process` without independently verifying it against a stored/registered shop for the corresponding webhook subscription. The attacker only needs a real (even free) Shopify store to obtain genuinely signed webhook bodies — no secret material or privileged account is required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signable string, or otherwise cryptographically bind `shop` to the verified payload before exposing it to handlers; at minimum, update `to_signable_string` to combine the raw body with the shop header used for authorization decisions, and update the documentation to explicitly warn that `data.shop` is not covered by the HMAC and must be cross-referenced against known/registered shops before being trusted.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and receives a real webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs to the app's webhook endpoint the same `B` and same HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` accepts the request (`Utils::HmacValidator.validate` passes because only `B` is checked) [8](#0-7)  and invokes the handler with `shop: "victim-shop.myshopify.com"` [9](#0-8) .

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

**File:** docs/usage/webhooks.md (L13-14)
```markdown
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
