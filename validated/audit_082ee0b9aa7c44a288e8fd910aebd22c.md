## Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) fields are trusted for tenant identification despite being excluded from the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the HMAC only over the raw request body [1](#0-0) , while the `shop`, `topic`, `webhook_id`, and `api_version` values used by `Registry.process` and handed to app handlers are all read directly from unauthenticated HTTP headers [2](#0-1) . This is precisely the "field acted on but not covered by the HMAC" class the rules call out. Since `api_secret_key` is a single per-app secret shared across every merchant/shop that installs the app (not a per-shop secret), any shop owner who legitimately receives a webhook for their own store can capture a valid `raw_body` + `hmac` pair and replay it with a modified `X-Shopify-Shop-Domain` header pointing at a *different* shop.

### Finding Description
`HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` and compares it to the received `hmac` [3](#0-2) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) . The `shop` accessor, however, is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header [4](#0-3) , which is never included in the signed bytes.

`Registry.process` performs the HMAC check and then immediately forwards `request.shop` (unauthenticated) to the app's handler as the tenant identifier: `raise ... unless Utils::HmacValidator.validate(request)` followed by `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [5](#0-4) . The gem's own documentation instructs the host app to trust `data.shop` as the shop domain of the webhook and use it directly, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [6](#0-5) . This is the gem's documented, recommended usage pattern - the host application is not "ignoring the documented API"; it is following it exactly.

The identity binding that should hold is:
`hmac verified over bytes == bytes that determine which shop/tenant the payload is attributed to`

but the actual behavior is:
`hmac verified over raw_body only != shop header used to route/attribute the payload`

Because the `api_secret_key` HMAC secret is shared by the app across *all* installed shops (this is standard OAuth app design - one client secret, many merchant installations), any single malicious merchant who has installed the app can obtain a validly-signed `(raw_body, hmac)` pair from their own webhook traffic and then send it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to name a victim shop. `Utils::HmacValidator.validate` will report the request as valid (since it only checks the body), and `Registry.process` will call the handler with `shop` set to the attacker-chosen victim domain.

### Impact Explanation
This enables cross-tenant data injection: an attacker-controlled shop can forge webhook events (e.g., `orders/create`, `app/uninstalled`, `shop/update`, etc.) that the host application attributes to a different, victim merchant, because the gem hands the unauthenticated `shop` value straight through as the trusted tenant key. Depending on how the consuming app persists or reacts to webhook data keyed by `data.shop` (which is exactly the documented usage), this can corrupt another merchant's stored data, trigger unauthorized side effects (e.g., simulating `app/uninstalled` for a shop the attacker doesn't own, or injecting order/customer data attributed to another tenant), i.e. cross-tenant access as described in the Critical impact category.

### Likelihood Explanation
Any current or former merchant of the app (an "unprivileged internet user" relative to other merchants) can trivially capture one legitimately-signed webhook body/HMAC pair from their own shop and replay it against the app's webhook endpoint with an altered shop-domain header - no access token, `client_secret`, or privileged access is required, only participation as a normal app installer, and no cryptographic secret needs to be broken since the header is simply outside the signed scope.

### Recommendation
Include the shop domain (and ideally `topic`/`webhook_id`/`api_version`) in the HMAC-signed material, or otherwise cryptographically bind the header-provided `shop` to the signed body before trusting it for tenant routing. At minimum, `ShopifyAPI::Webhooks::Request` should not expose `shop` as an implicitly trusted field for downstream use without documenting that it is not covered by HMAC verification and must be independently corroborated (e.g., cross-checked against a shop record that has already completed OAuth and is expecting a webhook with that `webhook_id`).

### Proof of Concept
1. App is installed on `attacker.myshopify.com` and `victim.myshopify.com`, both apps sharing the same `api_secret_key`.
2. Attacker triggers a real event on their own shop (e.g., updates a product), causing Shopify to send a legitimate webhook to the app's endpoint with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-hmac-sha256: <valid-hmac-of-raw-body>`
   - body: `{"id": 123, ...}`
3. Attacker captures this `raw_body` and `hmac` (e.g., via a proxy on a server they control).
4. Attacker resends the same `raw_body`/`hmac` to the app's webhook endpoint, but with the header changed to `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request#hmac` still decodes to the same valid signature and `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` [7](#0-6) .
6. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` [5](#0-4) , and the host app - following the gem's documented pattern of trusting `data.shop` [6](#0-5)  - processes the attacker's payload as if it belonged to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
