This confirms the finding. Let me verify how the webhook `shop` field is actually consumed by app handlers (via `WebhookMetadata`) to confirm the cross-tenant impact.### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable value from the raw body only, while the `shop`, `topic`, `api_version`, and `webhook_id` fields are read directly from unauthenticated HTTP headers. `Registry.process` validates only that the body's HMAC is correct, then trusts the header-derived `shop` value when building `WebhookMetadata` passed to the app's handler. This breaks the identity binding `shop_authenticated == shop_acted_on`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from HTTP headers with no cryptographic binding to the signed payload: [2](#0-1) 

`HmacValidator.validate` (and the underlying `validate_signature`) verifies the HMAC exclusively against `to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` checks only this body HMAC, then forwards the header-derived (unauthenticated) `shop` value into `WebhookMetadata`, which is exactly what app handlers use to identify which merchant/tenant the event belongs to: [4](#0-3) [5](#0-4) 

Because the `client_secret`/`api_secret_key` used to compute webhook HMACs is shared at the app level (identical across every merchant that installs the app), any merchant who receives a legitimately signed webhook for their own shop possesses a valid `(raw_body, hmac)` pair signed with the app's secret. That merchant can replay this exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header to name a different, victim shop. `HmacValidator.validate` will still return true (the body and HMAC are untouched), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event originated from the victim's shop.

Equality that should hold but doesn't: `shop_value_hmac_authenticated == shop_value_delivered_to_handler`. Before the request: the HMAC secures `(topic_A, shop_A_body_or_none, body)`. After the attacker's crafted request: the HMAC still validates the same `body`, but `request.shop` now equals `shop_B` (attacker-chosen), with no signature covering that substitution.

### Impact Explanation
This is a cross-tenant identity binding failure: an app relying on `WebhookMetadata#shop` (as documented/intended by this gem's webhook API) to scope subsequent data lookups, cache invalidation, order/customer processing, or session identification per shop can be tricked into processing or attributing a payload to the wrong tenant. Depending on how the host app uses `data.shop`, this can range from data confusion between merchants to processing forged events as if they came from a victim shop — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate merchant/install of the target app (an "unprivileged internet user" relative to other tenants of the same app) so as to receive one genuine webhook with a valid HMAC, and (2) the ability to send an HTTP request to the app's public webhook endpoint with modified headers, both of which are realistic for any external actor with a normal install. No possession of `api_secret_key` or any privileged credential is needed — only reuse of an already-delivered, validly-signed body.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the HMAC-covered signable string, or otherwise cryptographically bind the header-derived `shop` to the verified payload before constructing `WebhookMetadata`. At minimum, the gem should document this limitation prominently and/or provide a mechanism for host apps to reconcile the delivered `shop` against an independently known merchant/session context rather than trusting the header value outright.

### Proof of Concept
1. Merchant M installs an app using this gem; app_secret is shared across all merchants of the app.
2. Shopify sends M a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: HMAC(app_secret, B)`, header `X-Shopify-Shop-Domain: m-shop.myshopify.com`.
3. M captures this exact request, then replays it to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (body and HMAC header unchanged).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers)` is constructed; `HmacValidator.validate` succeeds because it only checks `Digest.hexencode(Base64.decode64(hmac)) == HMAC(app_secret, B)`.
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., the app now believes this payload belongs to `victim-shop.myshopify.com` even though it never sent it.

### Citations

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
