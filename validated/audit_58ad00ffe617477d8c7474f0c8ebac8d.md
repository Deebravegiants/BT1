### Title
Webhook shop identity is not covered by HMAC verification, enabling cross-tenant impersonation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, and `ShopifyAPI::Webhooks::Registry.process` uses this body-only HMAC to authenticate the request, then trusts the unauthenticated `shop-domain` header as the tenant identity passed to the app's handler. Since the HMAC never binds the `shop` (or `topic`/`webhook-id`) header to the signature, an attacker who can replay any single valid `(body, hmac)` pair for the app can substitute an arbitrary `shop-domain` header and have the handler execute as if the event originated from a victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)` (which only checks `to_signable_string`, i.e. the body, against the secret), then dispatches to the handler using `request.shop` as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it with `OpenSSL.secure_compare`: [4](#0-3) 

The identity binding that should hold is:
`hmac_verified_bytes == bytes_that_determine_tenant_and_topic_acted_on`

Here it does not: `hmac_verified_bytes = raw_body` while `tenant_acted_on = header["shop-domain"]` and `topic_acted_on = header["topic"]`. The `shop-domain`, `topic`, and `webhook-id` headers are completely outside the HMAC's coverage, exactly matching the "field acted on but not covered by the HMAC" analog class.

Because the app's `api_secret_key` (and thus the HMAC key) is a single shared secret across every shop that installs the app — not a per-shop secret — a `(raw_body, hmac)` pair that is valid for one shop's webhook delivery is also a valid HMAC for the exact same body regardless of which shop header accompanies it. An unprivileged attacker who obtains one legitimate webhook delivery (e.g., from their own shop where they installed the app, from a publicly logged/leaked webhook payload, or from a shop they control) can replay that captured request to the app's public webhook endpoint while swapping the `X-Shopify-Shop-Domain` header value to a victim shop's domain. `Utils::HmacValidator.validate` will still succeed because it only checks the raw body signature, and `Registry.process` will invoke the registered handler with `WebhookMetadata` claiming the victim shop as the origin: [5](#0-4) 

Test coverage confirms `request.shop`/`data.shop` is taken verbatim from the header with no cross-check against the signed payload: [6](#0-5) 

### Impact Explanation
Host applications built on this gem rely on `WebhookMetadata#shop` (sourced from `request.shop`) to determine which merchant's data/state the webhook event applies to (e.g., `app/uninstalled`, `shop/redact`, `orders/create`, `customers/data_request`). Because this field is not bound by the HMAC, an attacker can forge the tenant context of an otherwise-valid webhook delivery, causing the host app to perform actions (data deletion, session/token invalidation, order processing, GDPR redaction, etc.) against a victim shop chosen by the attacker rather than the shop that actually triggered the event. This is a cross-tenant identity confusion enabled entirely by this gem's verification logic, matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
The attacker needs at least one legitimate `(raw_body, hmac)` pair for the target app — trivially obtainable by installing the app on their own development/free shop (any unprivileged internet user can do this) or by observing a webhook payload leaked through logs, proxies, or a public endpoint. No access to `api_secret_key`, access tokens, or the victim shop is required; only the ability to POST an HTTP request with a modified `shop-domain` header to the app's public webhook endpoint. This is a documented header value under attacker control combined with a gem-level verification gap, making the likelihood high wherever the host app trusts `request.shop`/`WebhookMetadata#shop` for authorization or data-scoping decisions.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`/`api-version`) headers in the signable string used for HMAC verification, or otherwise cryptographically bind the shop identity to the signed payload before `Registry.process` dispatches to handlers. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant scoping without an independent authenticated lookup (e.g., verifying the shop against a known installed-shop record before acting).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (or otherwise observes a valid webhook delivery for the app) and captures a delivered webhook: raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint with the same body `B` and the same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` and any desired `X-Shopify-Topic` (e.g. `app/uninstalled`).
3. `ShopifyAPI::Webhooks::Request.new` parses the headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and compares it to `H` via `to_signable_string` (body only) — validation succeeds since `B` and `H` are unchanged.
4. `Registry.process` invokes the topic's handler with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host app to treat the event as originating from `victim.myshopify.com`, even though the shop never sent this webhook. [3](#0-2)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
