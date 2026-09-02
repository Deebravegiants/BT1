### Title
Webhook Shop Identity Spoofing via Unauthenticated `shop-domain` Header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as fully authenticated once the HMAC check passes, and hands the handler a `WebhookMetadata` object whose `shop` field is taken directly from the `shop-domain` HTTP header. However, the HMAC signature computed by `HmacValidator`/`Request#to_signable_string` only covers the raw request body — it never covers the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers. This breaks the intended identity binding: `HMAC-verified bytes (body) == trusted shop identity (header)` does not hold, because the header is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#shop` simply reads an unsigned header: [1](#0-0) 

The signable string used for HMAC verification is only the raw JSON body: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC purely against `to_signable_string` (i.e., the body), with no reference to the `shop`, `topic`, or `webhook-id` headers: [3](#0-2) 

`Registry.process` only performs this body-only HMAC check, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` delivered to the app's handler: [4](#0-3) 

The gem's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "the shop domain of the webhook" — i.e., it is documented and consumed as a verified, trustworthy identifier, when in fact it is attacker-controllable header data: [5](#0-4) [6](#0-5) 

Because a merchant/app-installer for shop A legitimately receives real, validly-HMAC'd webhook bodies for their own shop from Shopify, they can capture a body+HMAC pair and resend it to the target app's webhook endpoint with the `shop-domain` (and `x-shopify-shop-domain`) header rewritten to shop B's domain. The HMAC check still passes (it only checks the body against the app's `api_secret_key`, which the attacker never needs), but `WebhookMetadata#shop` will now report shop B, even though the payload actually originates from and pertains to shop A's data.

### Impact Explanation
This crosses a tenant boundary: the app's webhook handler, which typically uses `data.shop` as the lookup/session key to attribute the payload to a merchant record, will process shop A's real (but attacker-resent) event data under shop B's identity, or vice versa. Depending on the host app's logic (e.g., `perform_later(shop_domain: data.shop, webhook: data.body)` as shown in this gem's own documented usage pattern), this can lead to cross-tenant data corruption/injection — writing shop A's order/customer/product data into shop B's tenant records, or triggering shop-B-scoped side effects (e.g., webhook-driven billing/inventory updates) using attacker-supplied shop identity. This matches the "Critical - cross-tenant access" impact category, since the vulnerability lets one unprivileged app-installing merchant forge the shop attribution of webhook data delivered to the app.

### Likelihood Explanation
Any merchant who has installed the app (an "unprivileged internet user" relative to other tenants) automatically receives real HMAC-signed webhook deliveries for their own shop from Shopify. They need no special access, `api_secret_key`, or access token to exploit this — replaying a captured body with a modified `shop-domain` header against the app's public webhook endpoint is trivial and requires only basic HTTP tooling.

### Recommendation
Bind the identity fields to the HMAC-verified material instead of trusting bare headers:
- Include `shop`, `topic`, and `webhook_id` in the HMAC-covered signable string (or otherwise cryptographically bind them), or
- Cross-validate that the JSON body itself embeds/authenticates the shop, or
- At minimum, clearly document that `shop`/`topic`/`webhook_id` are NOT covered by the signature so integrators can add their own binding (e.g., matching the reported shop against a shop that already has an active, previously-registered webhook subscription/session) before trusting `data.shop`.

### Proof of Concept
1. App installs on shop A; app registers a webhook via `ShopifyAPI::Webhooks::Registry.register_all`.
2. Shopify sends a legitimate webhook to the app's endpoint for shop A: body `B`, `x-shopify-hmac-sha256: H = HMAC(api_secret_key, B)`, `x-shopify-shop-domain: shop-a.myshopify.com`.
3. A user with control over shop A's request path (e.g., a proxy, malicious middleware, or by simply being able to observe/replay their own shop's inbound webhook traffic) resends the exact same body `B` and HMAC `H` to the same app endpoint, but with header rewritten to `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate`, which recomputes HMAC over `B` only and matches `H`( [7](#0-6) ) — validation succeeds.
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` is built with `shop == "shop-b.myshopify.com"` even though the actual data came from shop A( [8](#0-7) ), and the app's handler processes/stores it under shop B's tenant identity.

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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L125-126)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
