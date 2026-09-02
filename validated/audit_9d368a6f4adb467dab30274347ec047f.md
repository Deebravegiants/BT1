## Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates an incoming webhook using `Utils::HmacValidator.validate(request)`, but the HMAC signature that request computes over is defined by `Webhooks::Request#to_signable_string`, which returns only `@raw_body`. None of the `topic`, `shop-domain`, `api-version`, or `webhook-id` HTTP headers are part of the signed content. Once the body/HMAC pair validates, `Registry.process` hands `request.shop` (taken verbatim from the unauthenticated `shop-domain` header) straight to the app's webhook handler as the tenant identifier.

### Finding Description
The binding that should hold is: `shop value verified by HMAC` == `shop value acted on by the handler`. Here that equality is broken:

- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the HMAC header. [1](#0-0) 
- For webhooks, `to_signable_string` returns only the raw body — the `shop`, `topic`, `api_version`, and `webhook_id` values come from separate, unsigned headers. [2](#0-1) 
- `Registry.process` treats a passing HMAC check as authorization to trust the whole `Request`, including `request.shop`, and forwards it to the merchant's handler unmodified: [3](#0-2) 

Because the header `shop-domain` (and `topic`/`webhook-id`/`api-version`) are not part of `to_signable_string`, an attacker who possesses one genuine `(raw_body, hmac)` pair — trivially obtainable by installing the target app on the attacker's own store and receiving one real webhook for any topic that has a fixed/predictable body, or any topic whose body they don't need to control — can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g., a victim's shop). `Utils::HmacValidator.validate` still succeeds because it only checks the body against the secret; `Registry.process` then calls `handler.handle` with `WebhookMetadata.new(topic:, shop: request.shop, body: ..., ...)` using the attacker-chosen shop value, so the host application processes the (attacker-supplied) payload under the identity of a different, arbitrary shop.

This is confirmed by the test suite, which shows `data.shop` is asserted to equal whatever the header says, with no cross-check against anything HMAC-protected: [4](#0-3) 

### Impact Explanation
This breaks the identity binding "webhook is authenticated for shop X" versus "webhook is processed as belonging to shop X." An attacker with no credentials, access token, or `client_secret` can cause the merchant application to process attacker-controlled/replayed webhook data under an arbitrary tenant's `shop` value, i.e., cross-tenant data injection through the app's own webhook processing pipeline — a Critical-tier "cross-tenant access" scenario as defined by the rules, achieved purely by exploiting the gem's own `Registry.process`/`Request` design (not misuse of the documented API — the documented usage is exactly `Registry.process(Request.new(...))`, as shown in `docs/usage/webhooks.md`).

### Likelihood Explanation
Likelihood is limited by two factors: (1) the attacker needs at least one legitimate `(raw_body, hmac)` pair for the target app, which they can generally obtain cheaply (e.g., install the app on a store they control and capture any webhook, since the body doesn't need to relate to the victim), and (2) the impact depends on the host application relying on `WebhookMetadata#shop` for tenant scoping without independent verification against the list of installed/authorized shops. Given this is the documented and expected usage pattern of `Registry.process`, likelihood is moderate-to-high for apps that trust `data.shop` directly.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the HMAC-verified content, or otherwise cryptographically tie header values to the authenticated request. If Shopify's real signature scheme is truly body-only, the library should not silently hand back `request.shop` as if it were validated — `Registry.process`/`WebhookMetadata` should be documented explicitly warning that `shop` is unauthenticated header data, or the library should provide (and use, when available) an independently signed/verifiable shop identifier before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and receives a real webhook: body `B` with a valid `x-shopify-hmac-sha256: H` (computed by Shopify over `B` using the app's real secret).
2. Attacker sends a forged HTTP request to the app's webhook endpoint with:
   - `x-shopify-topic`: any registered topic
   - `x-shopify-hmac-sha256`: `H` (unchanged)
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com`
   - body: `B` (unchanged)
3. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` only checks `B` against `H`. [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and body `B`, processing attacker data as if it originated from the victim's shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** test/webhooks/registry_test.rb (L218-239)
```ruby
      def test_process
        handler_called = false

        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal(@headers["x-shopify-webhook-id"], data.webhook_id)
            assert_equal(@headers["x-shopify-api-version"], data.api_version)
            handler_called = true
          end,
        )

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: @topic, path: "path", delivery_method: :http, handler: handler,
        )

        ShopifyAPI::Webhooks::Registry.process(@webhook_request)

        assert(handler_called)
      end
```
