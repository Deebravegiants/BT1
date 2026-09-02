This confirms the design: `Utils::HmacValidator.validate` only checks integrity of `to_signable_string`, and for webhooks that method returns solely `@raw_body`, excluding every header field.### Title
Webhook `shop-domain` header is trusted for tenant identity but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop-domain` header straight through to the app's handler as the trusted tenant identifier, without that header ever being part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate` computes/compares the HMAC exclusively over that signable string [2](#0-1) . Meanwhile `Request#shop` is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header [3](#0-2) , a value that is never fed into `to_signable_string` and therefore never covered by the HMAC.

`Registry.process` validates the HMAC and, if it matches, immediately trusts `request.shop` (from the unauthenticated header) when constructing the `WebhookMetadata` object passed to the app's handler: [4](#0-3) 

This breaks the identity binding the equality should enforce: `shop authenticated-by-HMAC == shop delivered-to-handler`. In reality the gem only proves `body authenticated-by-HMAC == body-received`; the `shop` value used for tenant routing is an independent, unsigned field.

Because `to_signable_string` only depends on `@raw_body`, an HMAC that is valid for one webhook delivery (e.g., a real, Shopify-issued webhook triggered on an attacker's own store, which any unprivileged user can install a public app on and trigger) remains valid for that exact body regardless of which `shop-domain` header accompanies the request. An attacker who controls the HTTP request reaching the app's webhook endpoint (e.g., replaying a captured request, or any client able to reach the endpoint directly since it is a public callback URL) can swap the `shop-domain` header to a victim shop while keeping the original body and HMAC intact; `Utils::HmacValidator.validate` still returns `true` because it only checks the body, and `WebhookMetadata.shop` will report the victim's shop domain to the handler.

The documented and tested usage pattern shows apps keying persistence/business logic directly off `data.shop`: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [5](#0-4) , and the test suite confirms `data.shop` is populated straight from the header with no cross-check against the signed body [6](#0-5) .

### Impact Explanation
This allows cross-tenant confusion: webhook payload data that is only cryptographically proven to have originated from Shopify for *some* body can be attributed by the app to an arbitrary `shop` value, since that value carries no integrity guarantee from the gem. Any app that uses `WebhookMetadata#shop` (as the gem's own documentation instructs) to select which tenant's data store to write into is vulnerable to having attacker-supplied/attacker-triggered event data injected under a victim tenant's identity — a cross-tenant integrity/data-injection issue rooted in this gem's failure to bind the `shop` field to the HMAC-verified payload.

### Likelihood Explanation
Exploitability depends on the attacker being able to influence the headers of the request that reaches the app's webhook endpoint (e.g., via a proxy/replay setup, or if the transport between Shopify and the app does not otherwise pin the header) while reusing a validly-signed body captured from a webhook the attacker can legitimately trigger (e.g., on their own store, since installing a public Shopify app is available to any unprivileged actor). The gem itself provides no defense — `Utils::HmacValidator.validate` and `Registry.process` will accept such a request as fully authenticated. This is a design gap in the gem's verification contract rather than a purely theoretical concern, since the gem explicitly directs apps to trust `data.shop` post-validation.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the HMAC-signable material for webhooks, or otherwise cryptographically bind the shop identity to the verified payload, so that `Utils::HmacValidator.validate` fails whenever any of these header fields are altered relative to what Shopify actually signed. At minimum, document clearly that `shop-domain` is unauthenticated so implementers do not use it as a sole tenant key.

### Proof of Concept
1. Attacker installs the target's public Shopify app on their own store (`attacker.myshopify.com`) and triggers a webhook (e.g., `orders/create`) with a body they control.
2. Shopify sends the webhook to the app's callback URL with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw body>`.
3. Attacker intercepts/replays this exact request but rewrites only the `x-shopify-shop-domain` header to `victim.myshopify.com`, leaving the raw body and `x-shopify-hmac-sha256` untouched.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` whose `to_signable_string` is unchanged (`lib/shopify_api/webhooks/request.rb:35-38`).
5. `Utils::HmacValidator.validate` recomputes the HMAC over the same raw body and it matches — the forged request passes verification (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
6. `Registry.process` invokes the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled body content under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
