## Finding

### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, enabling shop-identity spoofing on replayed webhooks - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop and topic identity used by the registry to route/attribute a webhook are taken from unauthenticated HTTP headers. An attacker who can obtain one valid `(body, hmac)` pair for any shop (trivial to do, since anyone can install a public app on their own store and receive real webhooks for it) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` (and `topic`) header. `Utils::HmacValidator.validate` still reports success because it only re-derives the signature from the body, so `Registry.process` will hand the forged shop identity to the app's webhook handler as if the payload legitimately originated from a different tenant.

### Finding Description
The HMAC signable string for a webhook request is defined as just the raw body: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` values, however, come directly from HTTP headers that are never mixed into that signable string: [2](#0-1) 

`HmacValidator.validate` only ever verifies `verifiable_query.to_signable_string` against the received HMAC — i.e., it only proves the *body* bytes are untampered, not the headers: [3](#0-2) 

`Registry.process` trusts this validation result and then immediately uses the unauthenticated `request.shop` / `request.topic` header values to dispatch to the handler: [4](#0-3) 

This reproduces the report's bug class exactly: "a field acted on but not covered by the HMAC." In the CREATE2 report, `salt` was written into a memory region that was not part of the value actually keccak256-hashed for authentication; here, `shop-domain`/`topic` are values acted upon (used as the tenant identity) that are not part of the bytes actually HMAC-authenticated. The binding that should hold is:

`hmac == HMAC(secret, body || shop || topic)` (or equivalent binding of headers to the signature)

but the code only enforces:

`hmac == HMAC(secret, body)`

leaving `shop` and `topic` completely attacker-controllable on any request carrying a previously-valid `(body, hmac)` pair.

### Impact Explanation
An unprivileged internet user who has installed the app on their own store (a normal, unprivileged action available to anyone for a public app) legitimately receives real webhook deliveries — each is a valid `(body, hmac)` pair for their own shop. That user can capture such a delivery and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to name a *different* (victim) shop. Because the signature check ignores headers, the forged request passes validation, and the host application's webhook handler executes with `WebhookMetadata.shop` set to the victim's domain while carrying attacker-chosen body content. Depending on how the host app keys data by `shop` (which is the documented multi-tenant partition key throughout this gem, e.g. `Auth::Session` IDs are `"#{shop}_..."`), this enables cross-tenant data injection/corruption — data belonging to one merchant is written or acted upon under another merchant's identity. This falls under "cross-tenant access," rated Critical in the assessment rules.

### Likelihood Explanation
Likelihood is high: no secrets, tokens, or privileged access are required. The attacker only needs to install the target app once (a normal unprivileged flow for any public embedded app) to obtain a valid `(body, hmac)` sample, then can replay it against the same public webhook endpoint with arbitrary header values for `shop-domain`/`topic`/`webhook-id`. This is a deterministic protocol-level gap, not a race condition or timing issue.

### Recommendation
Bind the shop/topic identity into the value that is actually HMAC-verified, or otherwise cryptographically tie the headers to the signature, e.g.:
- Include `shop-domain`, `topic`, and `webhook-id` in the canonical string that is HMAC'd (this requires coordinating with Shopify's webhook signing scheme, or maintaining a secondary application-level check), or
- At minimum, cross-check the `shop-domain` header against an independently-trusted source (e.g. confirm the shop is one that has an active, stored session/installation) before trusting it as the tenant key, rather than relying solely on the body HMAC to imply header authenticity.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify sends a legitimate POST to the app's webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this request (e.g., by running their own receiving server as their app's webhook URL, or logging proxy) and resends it to the app's public webhook endpoint, keeping body `B` and header `H` unchanged, but replacing:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it still matches `H`, so `Registry.process` proceeds using `shop: "victim-shop.myshopify.com"` from the header:
```ruby
ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {
  "x-shopify-hmac-sha256" => H,
  "x-shopify-topic" => "orders/create",
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
})
```
5. The registered handler executes with attacker-controlled body content attributed to `victim-shop.myshopify.com`, demonstrating the identity-binding break.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
