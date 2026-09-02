## Title
Webhook shop identity spoofing due to HMAC only covering the body, not the shop-domain header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook purely by validating the HMAC over the raw request body, then trusts the `shop-domain` header — which is never included in the signed bytes — to identify which tenant the event belongs to.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers that are not part of the signable string: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` verify the HMAC using only `verifiable_query.to_signable_string` (the body) against `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` checks only that HMAC, then forwards the unauthenticated `request.shop` value straight into `WebhookMetadata` that is handed to the host application's handler: [4](#0-3) 

The identity binding that should hold is: `shop header == the tenant whose secret produced this HMAC`. Because the HMAC is computed solely from `client_secret` + body, and `client_secret` (`api_secret_key`) is shared across **all** shops that install the same app, any unprivileged merchant who has installed the app can:
1. Receive a genuine webhook for their own shop with a body they can influence (e.g. by crafting an order note, product title, or other field that flows into the payload), computing a body whose HMAC they now know is valid for the app's secret.
2. Replay that exact body/HMAC to the app's webhook endpoint, but swap the `X-Shopify-Shop-Domain` header to a victim shop's domain.
3. `Registry.process` validates the HMAC successfully (since it's still valid for that body under the shared `client_secret`), extracts `shop` from the now-forged header, and dispatches to the handler claiming the event is `WebhookMetadata` for the victim shop.

This breaks the equality `shop_header == HMAC-authenticated_tenant`: the header is acted upon (used as the tenant key by any host app built on this gem's documented API) but is never covered by the same signature that authenticates the payload.

### Impact Explanation
Host applications are expected — and this gem's own test suite demonstrates the pattern — to key data (e.g., `data.shop`) directly off `WebhookMetadata#shop` returned from `Registry.process`: [5](#0-4) 

Since `shop` is not authenticated, an attacker who legitimately installed the app on their own store can forge webhook deliveries that appear to originate from an arbitrary victim shop that also installed the same app, causing the host application to process attacker-controlled data (order/product/customer state) under another tenant's identity — a cross-tenant integrity violation reachable by any unprivileged app-installer, without needing the victim's or the app's credentials.

### Likelihood Explanation
Any user who can install the app on their own store (a normal, unprivileged action) can trigger real webhook deliveries with attacker-influenced body content and a correctly computed HMAC for the shared `client_secret`. Forging the `shop-domain` header on the replayed request requires no additional secret. This is a low-effort, directly reachable path through the gem's documented `Webhooks::Registry.process` API.

### Recommendation
Include the shop identity (and ideally topic/webhook-id) in the bytes that are HMAC-verified, or otherwise cryptographically bind the `shop-domain` header to the signature (e.g., verify the header against Shopify's per-request signing that already covers it, or require host apps to independently confirm `shop` via a signed source such as the JWT session token rather than trusting the webhook header). At minimum, document that `WebhookMetadata#shop` is unauthenticated and must be cross-checked against a known/installed shop record before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (legitimate, unprivileged action).
2. Attacker triggers an event (e.g. updates an order note) so the app's real webhook delivery contains an attacker-chosen body `B`.
3. Shopify sends `X-Shopify-Hmac-Sha256: HMAC(client_secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
4. Attacker replays the identical body `B` and HMAC to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) calls `Utils::HmacValidator.validate(request)`, which only checks `B` against the HMAC — it passes. The handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, impersonating the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** test/webhooks/registry_test.rb (L246-255)
```ruby
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
```
