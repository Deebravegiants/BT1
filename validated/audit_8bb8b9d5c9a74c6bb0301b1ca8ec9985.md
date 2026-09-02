### Title
Registry.process trusts unauthenticated `shop-domain` header for webhook attribution - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates only that the HMAC matches the raw body, then reads `request.shop` from the unsigned `shop-domain`/`x-shopify-shop-domain` header and passes it straight into `WebhookMetadata` given to the app's handler. Because the HMAC signable string is exclusively `@raw_body` [1](#0-0) , the shop attribution has no cryptographic binding to the signature at all.

### Finding Description
The broken binding: `shop authenticated by HMAC` should equal `shop acted on by handler`, but the gem computes `shop authenticated by HMAC = ∅` (HMAC covers only the body) and `shop acted on by handler = request.shop` (read straight from a client-supplied header), so these are never actually the same value by construction. `HmacValidator.validate_signature` computes the signature purely from `verifiable_query.to_signable_string`, which for `Request` is `@raw_body` [2](#0-1) [1](#0-0) . `Registry.process` then does exactly: validate HMAC → look up handler by `request.topic` → call `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))`, where `request.shop` is `shopify_header("shop-domain")`, i.e. `@headers["shopify-shop-domain"] || @headers["x-shopify-shop-domain"]` [3](#0-2) [4](#0-3) [5](#0-4) . There is no call to `Utils::ShopValidator` or any session/install lookup inside `Registry.process` to cross-check `request.shop` against a known-installed shop for the given `api_secret_key`/app — that check exists elsewhere in the gem (`ShopValidator.sanitize!`, used for OAuth callback shop params [6](#0-5) ) but is not invoked anywhere in the webhook processing path.

Exploit flow: attacker installs the app on their own dev shop, `attacker-shop.myshopify.com`. Because `api_secret_key` is per-app (shared across every shop that installs it), Shopify's real webhook delivery to the attacker's registered endpoint for `orders/create` carries a legitimately-computed HMAC over the JSON body plus a `x-shopify-shop-domain: attacker-shop.myshopify.com` header. The attacker captures this raw body + HMAC header, then resends the identical `raw_body` and `hmac-sha256` header to the same app endpoint but with `x-shopify-shop-domain` rewritten to `victim-shop.myshopify.com`. `HmacValidator.validate` still returns `true` because it only recomputes the HMAC over the untouched `raw_body`. `Registry.process` then builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's payload>, ...)` and invokes `handler.handle`, attributing attacker-controlled data to the victim shop.

This is confirmed by the existing test suite itself: `test_process` asserts `data.shop` equals whatever `x-shopify-shop-domain` header was supplied, with no independent verification tying the header to the HMAC-covered body [7](#0-6) .

### Impact Explanation
Any app built directly on `Registry.process` without adding its own out-of-band shop/session verification will process cross-tenant webhook data: an attacker who has installed the app once can make the app's webhook handler believe arbitrary attacker-chosen JSON bodies originate from any other merchant's shop domain, for any topic the app has registered (`orders/create`, and potentially higher-impact topics like `customers/data_request`/`app/uninstalled` if registered as `:http`). Since apps commonly key persistence (queue jobs, DB writes, side effects) off `data.shop`, this allows injecting attacker data into another tenant's records/queue — a cross-tenant data integrity breach reachable through the gem's own webhook API surface, matching "Critical - cross-tenant access."

### Likelihood Explanation
Preconditions are modest but non-trivial: (1) the app must use `Registry.add_registration`/`Registry.process` for `:http` delivery, and (2) critically, the app must not perform its own additional shop-validation against a store of known installs before acting on `data.shop` — this is a design gap the gem does not close, but which is explicitly the standard app-side mitigation documented for exactly this Shopify webhook property (HMAC covers body only, not the shop header) in Shopify's own platform documentation. The gem's docs (`docs/usage/webhooks.md`) do not mention this caveat or recommend verifying `data.shop` against known installs before acting on the payload, which is a real gap, but the vulnerability's exploitability entirely depends on host-app behavior outside this gem's code — the gem faithfully reproduces Shopify's own webhook verification contract (HMAC over raw body only), it does not introduce an additional flaw beyond what Shopify's webhook protocol itself defines. The attacker cost is low (one dev-shop install, replay a captured request with a modified header), and it is repeatable against arbitrary victim shop domains for as long as the attacker's own webhook secret/HMAC stays valid.

### Recommendation
None to give in ask-only mode; conceptually, `Registry.process` could optionally accept an app-supplied shop-lookup callback to require the caller to confirm `request.shop` belongs to a known session/install before invoking `handler.handle`, and `docs/usage/webhooks.md` should explicitly document that `data.shop` is not cryptographically bound to the HMAC and must be cross-checked by the host app against its own installed-shop registry.

### Proof of Concept
A minitest + WebMock test could construct two `ShopifyAPI::Webhooks::Request` instances sharing the same `raw_body` and valid `hmac-sha256` header (computed once with `Context.api_secret_key`), but with `x-shopify-shop-domain` set to `"attacker-shop.myshopify.com"` on one and `"victim-shop.myshopify.com"` on the other, asserting `Utils::HmacValidator.validate` returns `true` for both, and that `Registry.process` invokes the handler with `data.shop == "victim-shop.myshopify.com"` while `data.body` is unchanged from the attacker's original payload — demonstrating the HMAC-validated side (`raw_body`) and the shop-attributed side (`header`) diverge freely. This can be assembled directly from the existing pattern in `test_process`/`test_process_with_new_format_headers` [7](#0-6) .

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/shop_validator.rb (L56-64)
```ruby
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
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
