### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , and `HmacValidator.validate` verifies the HMAC solely against that body [2](#0-1) . The `shop-domain` header, which `Registry.process` trusts and forwards to the webhook handler as the tenant identifier, is never part of the signed material [3](#0-2) [4](#0-3) . This breaks the binding "shop asserted by header == shop the HMAC was computed for."

### Finding Description
`Request#hmac`/`Request#to_signable_string` are computed purely from `@raw_body`, and no other header (`shop`, `topic`, `webhook_id`, `api_version`) participates in the signature: [5](#0-4) 

`Registry.process` validates only this body-bound HMAC, then reads `request.shop` from the (unverified) header and passes it straight into the handler as the merchant/tenant identity: [3](#0-2) 

Because the signature never binds the body to the `shop-domain` header, any `(raw_body, hmac)` pair that is valid for *some* shop is also valid, unmodified, when replayed with a different `x-shopify-shop-domain` (or `shopify-shop-domain`) header value. A merchant who installs the app on their own store legitimately receives genuinely-signed webhook deliveries (valid `body`/`hmac` pairs signed with the app's `api_secret_key`) addressed to their own store. Since the header is not part of the signed content, that same body+HMAC pair can be resent to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop's domain, and `Utils::HmacValidator.validate` will still return `true`.

### Impact Explanation
If the host application's webhook handlers use `WebhookMetadata#shop` to scope data writes/reads (the intended and documented use, since `Registry.process` passes `shop: request.shop` to every handler), an attacker can inject attacker-controlled webhook payloads that are processed under a victim shop's identity. This is cross-tenant access/data-injection across merchants sharing the same app deployment — a Critical-impact class explicitly in scope (cross-tenant access via a field acted on but not covered by the HMAC).

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the app on an attacker-controlled store (or otherwise obtain one legitimately-signed webhook body/HMAC pair — the body content for many topics is attacker-influenced, e.g. `orders/create` fields the attacker controls when placing an order in their own store), and (2) the ability to send an HTTP request to the app's public webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or privileged access is required — only unprivileged interaction available to any internet user/merchant.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed/verified material, or independently verify that the `shop-domain` header corresponds to a shop that is actually subscribed to/expected for that specific webhook delivery (e.g., cross-check against a known active session/shop record) before trusting `request.shop` in `WebhookMetadata`. At minimum, document that host applications must not treat `request.shop` as authenticated by the HMAC and must independently confirm shop identity.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) with attacker-chosen order data. Shopify delivers `raw_body = B` with header `x-shopify-hmac-sha256 = HMAC(secret, B)` to the app's endpoint.
2. Attacker captures `(B, HMAC(secret,B))` (they control the delivery target/network path for their own shop) and replays a POST to the same endpoint with identical body `B` and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` against `request.hmac` — this still matches [6](#0-5) .
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: B, ...)` [7](#0-6)  and processes attacker-controlled data under the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
