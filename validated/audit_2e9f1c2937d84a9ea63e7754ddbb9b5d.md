Confirmed the full picture: `WebhookMetadata` is a plain `T::Struct` with `shop`, `topic`, `webhook_id`, `api_version` fields populated directly from unverified HTTP headers, and `Registry.process` only checks the HMAC over the raw body.

### Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies authenticity of an inbound webhook solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string` — the raw request body only. The `shop`, `topic`, `webhook_id`, and `api_version` values, which are read straight from HTTP headers and passed unverified into `WebhookMetadata`, are never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop`, `#topic`, `#webhook_id`, `#api_version` are all pulled directly from caller-supplied headers with no cross-check against the HMAC [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., the body signature) before dispatching to the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` [3](#0-2) . `HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it only to the received `hmac`, never incorporating `shop`, `topic`, or `webhook_id` [4](#0-3) .

This breaks the identity binding: `shop` (trusted by the handler as the tenant identity) == `shop` (covered by the HMAC that "verif[ies] the request did indeed come from Shopify," as the docs claim) [5](#0-4) . In fact the two are disjoint: the HMAC authenticates only the byte content of the body, and the header-derived `shop` is passed through to the application's handler as if authenticated [6](#0-5) . The library's own documentation encourages exactly this trust: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [7](#0-6) .

### Impact Explanation
An unprivileged internet user who is a legitimate merchant/installer of the target app (able to trigger any webhook topic on their own store, e.g. `products/create`) receives a genuine `(raw_body, hmac)` pair signed by Shopify for their own shop. They can then replay that exact body+HMAC to the app's public webhook endpoint while spoofing the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a victim shop. Because `HmacValidator` never binds these header values to the signature, the request still validates, and the handler receives `WebhookMetadata` claiming the data belongs to the victim tenant. Any app that keys per-tenant side effects (job routing, data writes, cache invalidation, webhook dedup by `webhook_id`) off `data.shop`/`data.webhook_id` as this gem's own documentation instructs can be tricked into cross-tenant data confusion.

### Likelihood Explanation
Webhook endpoints are unauthenticated-by-design public HTTP endpoints, and any real shop installing the app can generate a validly-signed body for arbitrary content it controls (e.g., product titles/notes containing attacker-chosen payloads), then simply resend it with modified headers — no secret material or privileged access is required beyond installing the app once as a normal merchant.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-covered signable content (or independently verify `shop` against the session/shop the webhook was registered for) before constructing `WebhookMetadata`, rather than trusting header values that sit outside the cryptographic envelope.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; trigger `products/create` to receive a legitimate webhook POST with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(secret, B)`).
2. Replay the captured request to the app's webhook URL, keeping body `B` and header `H` unchanged, but replace `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches `H` — validation succeeds [8](#0-7) .
4. The registered handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, and any per-tenant logic keyed on `data.shop` now operates against the wrong tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
