### Title
Webhook shop-domain header trusted without HMAC binding enables cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop` as a plain, unauthenticated HTTP header value, while the HMAC signature that `Registry.process` validates only covers the raw request body. Because the tenant-identifying field (`shop-domain`/`x-shopify-shop-domain`) is never included in the signed material, an attacker can take any of their own legitimately-signed webhook deliveries (which is trivial to obtain — they only need to install the app on their own store) and replay it against the app's webhook endpoint with a forged `shop-domain` header pointing at a victim shop. The HMAC check still passes because it never inspected that header, and the host application receives a `WebhookMetadata` object claiming the payload belongs to the victim's shop.

### Finding Description
`Registry.process` authenticates a webhook solely via: [1](#0-0) 

which calls `Utils::HmacValidator.validate(request)`. That validator computes the signature over `request.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw body: [3](#0-2) 

but `request.shop` is read straight out of the (attacker-controlled, transport-level) HTTP headers with no cryptographic binding to that body: [4](#0-3) [5](#0-4) 

`Registry.process` then hands this unauthenticated `shop` straight to the host application's handler as the tenant identity for the payload: [6](#0-5) 

This is the exact bug class from the report: `claimee`/`token` (an identity key) is acted on using data that isn't part of the cryptographically-verified material, while a *different* key (the raw body) is what's actually checked. Here, the equality that should hold is:

`shop bound by HMAC == shop delivered to handler`

but the code only guarantees:

`raw_body bound by HMAC == raw_body delivered to handler`

The `shop` field is never part of the signable string, so the equality silently breaks whenever the header and body diverge.

### Impact Explanation
Because the app's `api_secret_key` (used to compute/verify webhook HMACs) is shared across every shop that installs the app, any attacker who installs the app on their own (attacker-controlled) store can capture a webhook delivery that Shopify has validly signed (e.g. `orders/create` for their own shop). They can then replay that exact `raw_body` + `hmac-sha256` header to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header value (a victim's `myshopify.com` domain). `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` invokes the host app's handler with `WebhookMetadata#shop` set to the victim's shop. Any host application that uses this `shop` to route/persist/act on the payload (which is the documented, expected usage per `docs/usage/webhooks.md`) will attribute the attacker's data to the victim tenant — a cross-tenant data-integrity/confusion issue reachable by any unprivileged internet user who can register as a merchant of the app.

### Likelihood Explanation
Likelihood is high: no special privileges are required beyond installing the target app on a store the attacker controls (a normal, unprivileged action), capturing one valid webhook delivery, and replaying it with a modified header — something any HTTP client can do since the shop-domain header is not authenticated at all.

### Recommendation
Bind the shop identity to the verified payload. Concretely, either:
- Include `shop-domain` (and `topic`/`webhook-id`) in the HMAC-signable string in `Request#to_signable_string`, so `HmacValidator.validate` fails if the header is tampered with, or
- Cross-check `request.shop` against a shop value embedded in the verified body (if available), or against the session/shop the caller expects for that endpoint, before invoking the handler in `Registry.process`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g. `orders/create`) and captures the raw body `B` and the resulting `X-Shopify-Hmac-Sha256: H` header that Shopify computed with the app's shared `api_secret_key`.
3. Attacker sends a POST to the app's webhook endpoint with:
   - `raw_body = B`
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`)
   - `X-Shopify-Topic: orders/create`
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` only and succeeds.
5. The host app's handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: parsed(B), ...)` — attacker-supplied data now falsely attributed to the victim shop, as shown in the equivalent test setup where `data.shop` is taken directly from the header value: [7](#0-6) .

### Citations

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
