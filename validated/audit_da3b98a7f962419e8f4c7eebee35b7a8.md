Confirmed. The `shop` field in `WebhookMetadata` (`lib/shopify_api/webhooks/webhook_handler.rb:8`) is populated directly from `request.shop` [1](#0-0) , which is read from an HTTP header [2](#0-1) , while the HMAC verification only ever covers the raw request body [3](#0-2) .

### Title
Webhook `shop` tenant identifier is not covered by HMAC verification, enabling cross-tenant data attribution - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` value from the `shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only ever binds the raw request body. Consequently, an attacker who obtains one validly-signed webhook body/HMAC pair (e.g. by installing the app on their own store and receiving a legitimate webhook) can replay that exact body to the app's webhook endpoint while substituting an arbitrary `shop-domain` header. `HmacValidator.validate` still succeeds because it only recomputes the signature over `@raw_body`, and the forged `shop` value flows unchanged into `WebhookMetadata.shop`, which host applications use as the authoritative tenant identifier for the payload.

### Finding Description
`process` accepts a request the moment `Utils::HmacValidator.validate(request)` returns true [1](#0-0) . That validator computes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it against the `hmac` field [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [3](#0-2) , and `hmac` is likewise derived only from the `hmac-sha256` header contents, never mixed with `shop` [5](#0-4) . Meanwhile `shop` is read straight from the `shop-domain` header with no cryptographic binding at all [2](#0-1) .

This breaks the intended equality `shop-header == HMAC-authenticated tenant`. The gem hands this unauthenticated `shop` straight to the host application as `WebhookMetadata#shop` [6](#0-5) , and the library's own tests demonstrate the `shop` header being trusted and forwarded to the handler untouched [7](#0-6) .

### Impact Explanation
This is a cross-tenant integrity break at the library boundary: the SDK explicitly names and exposes `request.shop` (and `WebhookMetadata#shop`) as the tenant identifier for the delivered payload, yet never authenticates it. Any unprivileged party that can obtain one legitimately-signed webhook body (trivially available by installing the app on their own, attacker-controlled shop) can present that body with a forged `shop-domain` header to the app's webhook endpoint and have it pass HMAC verification. A host application that follows the gem's documented pattern of trusting `data.shop` from `WebhookMetadata` to select which merchant's records to update will process/store attacker-supplied data under a victim shop's identity — a cross-tenant access/data-integrity violation attributable directly to this gem's verification contract.

### Likelihood Explanation
Exploitation requires no privileged credentials: any developer/merchant can install the target app on their own store to legitimately receive at least one webhook with a valid `hmac-sha256` body signature, then replay that raw body with a spoofed `shop-domain` header to the app's public webhook endpoint. Because verification is entirely header/field-independent of `shop`, this succeeds every time regardless of which shop is targeted.

### Recommendation
Include the `shop-domain` header (and ideally `topic`/`webhook-id`) as part of the HMAC-signable material in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind `shop` to the verified payload before exposing it via `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as the sole tenant selector without additional verification (e.g., cross-checking against a shop already known to have an active session/access token).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` and receives a legitimate webhook: body `B` with header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker sends `POST /webhooks` to the victim app's endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), and `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds successfully; `shop` returns `"victim-shop.myshopify.com"` per `lib/shopify_api/webhooks/request.rb:20-23`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely over `B` and matches `H`, so validation passes despite the mismatched `shop-domain` header [8](#0-7) .
5. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body(B), ...)`, causing the host app to associate attacker-controlled `B` with the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** test/webhooks/registry_test.rb (L266-302)
```ruby
      def test_process_with_new_format_headers
        handler_called = false

        handler = TestHelpers::FakeWebhookHandler.new(
          lambda do |data|
            assert_equal(@topic, data.topic)
            assert_equal(@shop, data.shop)
            assert_equal({}, data.body)
            assert_equal("b1234-eefd-4c9e-9520-049845a02082", data.webhook_id)
            assert_equal("2024-01", data.api_version)
            handler_called = true
          end,
        )

        ShopifyAPI::Webhooks::Registry.add_registration(
          topic: @topic, path: "path", delivery_method: :http, handler: handler,
        )

        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        new_format_headers = {
          "shopify-topic" => @topic,
          "shopify-hmac-sha256" => Base64.encode64(hmac),
          "shopify-shop-domain" => @shop,
          "shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "shopify-api-version" => "2024-01",
        }

        webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: new_format_headers)
        ShopifyAPI::Webhooks::Registry.process(webhook_request)

        assert(handler_called)
      end
```
