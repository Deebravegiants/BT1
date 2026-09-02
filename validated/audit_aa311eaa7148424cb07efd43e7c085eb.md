### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `HmacValidator` verifies the HMAC purely over that body [1](#0-0) . The `shop-domain` header, which is later trusted as the tenant identifier passed to the app's webhook handler, is not included in the signed payload [2](#0-1) . `Registry.process` only validates the HMAC and then hands `request.shop` straight to the handler without any cross-check against the signed content [3](#0-2) .

### Finding Description
The equality this breaks is: **shop bound by HMAC == shop delivered to handler**. In the correct design these must be the same value; here they are independent. `HmacValidator.validate` recomputes an HMAC only over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that string is `@raw_body` alone [4](#0-3) [1](#0-0) . The `shop` accessor pulls from the `shop-domain`/`x-shopify-shop-domain` header, which is never mixed into the signed bytes [2](#0-1) .

Because every shop that installs a given app shares the same `api_secret_key`, a real webhook delivered by Shopify for shop A's own data carries a valid HMAC over that body computed with the app's shared secret. Since the header carrying the tenant identity is not part of the signed material, an attacker who controls shop A (a legitimate, unprivileged installer of the target app) can capture one of their own genuine webhook deliveries (valid body + valid HMAC), then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header for victim shop B. `Registry.process` only checks `Utils::HmacValidator.validate(request)` (body-only) before dispatching to the handler with `request.shop` [3](#0-2) , so the forged request passes verification and the handler executes believing the data originated from shop B.

### Impact Explanation
This crosses a tenant boundary using only unprivileged means (an attacker's own legitimate app installation). A host application that keys webhook processing (job enqueue, cache invalidation, order/customer sync, GDPR-relevant compliance webhooks, etc.) off `data.shop` as documented — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [5](#0-4)  — will process attacker-supplied body content under a different, unrelated tenant's identity. This is a cross-tenant data-integrity/confusion vector satisfying the "cross-tenant access" impact class, since the app has no cryptographic assurance the `shop` value it acts on matches the value Shopify actually authenticated for that specific payload.

### Likelihood Explanation
Any merchant who can install the app (a normal, unprivileged action) can capture their own valid webhook deliveries (e.g., via a temporary endpoint they control) and immediately has a valid `(body, hmac)` pair usable against the shared client secret. Forging the `shop-domain` header when replaying the HTTP POST requires no secret knowledge at all. This is a low-effort, always-reachable path for anyone who signs up for the app, with no dependency on stolen credentials or privileged access.

### Recommendation
Bind the shop domain to the signed content: verify that `request.shop` corresponds to a shop for which the app has an active/expected webhook registration (e.g., cross-check webhook_id/topic pairing recorded at registration time), and/or include the `shop-domain` header value in the HMAC-signed material used by `to_signable_string`, rejecting requests where the header shop and any independently-tracked expected shop diverge. At minimum, document that host applications must not trust `data.shop` as authenticated on its own and must validate it against their own installation records before acting on webhook content.

### Proof of Concept
1. Attacker installs the target Shopify app on shop `attacker.myshopify.com` (normal signup, no privileges).
2. App registers a webhook (e.g., `orders/create`) for that shop; Shopify later POSTs a webhook with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`, and some JSON body.
3. Attacker captures the raw body and the `x-shopify-hmac-sha256` value (e.g., by pointing their own webhook callback path to a logger).
4. Attacker replays an HTTP POST to the same app's public webhook endpoint, keeping the identical raw body and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` and succeeds because the body is unchanged [6](#0-5) .
6. The handler is invoked with `WebhookMetadata` carrying `shop: "victim.myshopify.com"` and the attacker-controlled body, even though Shopify never authenticated this payload for `victim.myshopify.com` [7](#0-6) .

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
