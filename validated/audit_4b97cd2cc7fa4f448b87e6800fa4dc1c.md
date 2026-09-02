### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers. `Registry.process` verifies the HMAC against the body only, then trusts the header-derived `shop` value to dispatch the webhook payload to the app's handler as if it originated from that shop.

### Finding Description
`Registry.process` validates the webhook solely via `Utils::HmacValidator.validate(request)`, which computes `to_signable_string` and compares it against the `hmac` value: [1](#0-0) 

`Request#hmac` and `Request#to_signable_string` are computed purely from the raw body: [2](#0-1) 

Meanwhile `Request#shop` (and `topic`, `api_version`, `webhook_id`) are pulled straight from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header with no cryptographic binding to the HMAC-signed body: [3](#0-2) 

The equality this breaks is: `shop value authenticated by the HMAC` should equal `shop value delivered to the handler`, but the gem only proves `body value authenticated by the HMAC` = `body value delivered to the handler`; the `shop` header is never part of that proof. `Registry.process` forwards this unauthenticated `shop` straight into the handler's `WebhookMetadata`: [4](#0-3) 

Any party who can produce one valid `(body, hmac)` pair — e.g., the operator of their own shop that has installed the app, who legitimately receives real webhooks from Shopify for their own shop with a valid HMAC — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. Because `HmacValidator.validate` never inspects the `shop` header, the forged request passes validation and the handler receives attacker-chosen `shop` metadata bound to genuinely-signed (but shop-mismatched) body content.

### Impact Explanation
This crosses a tenant boundary: a handler that uses `WebhookMetadata#shop` to look up session/credentials or to attribute the webhook payload to a shop (a common integration pattern per `docs/usage/webhooks.md`) can be tricked into processing another merchant's identifier against attacker-controlled body content, or vice versa — attacker's own legitimately-signed payload attributed to a victim shop. Depending on how the host application keys off `shop` (e.g., to select which tenant's data to mutate), this can lead to cross-tenant data corruption or unauthorized actions performed under a victim shop's identity, which maps to the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires only the ability to (a) operate one's own Shopify shop that has installed the target app (to obtain a genuinely HMAC-signed webhook body/signature pair) and (b) send arbitrary HTTP headers to the app's public webhook endpoint — no access token, `client_secret`, or privileged account is needed, satisfying the "unprivileged internet user" threat model. The only unresolved uncertainty is how much host applications actually trust `WebhookMetadata#shop` without independent cross-checks (e.g., verifying it against a known list of installed shops before trusting the payload); the gem itself provides no such binding, so the risk is inherent to the API surface exposed.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` header values in `to_signable_string` (or otherwise cryptographically bind them, mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop`/`host`/`state` alongside other fields), so `HmacValidator.validate` fails whenever any of these fields are altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com`, which has the target app installed, and legitimately receives a webhook: `raw_body = "{...attacker payload...}"` with headers `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds the request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only [5](#0-4)  — validation succeeds because the body is unchanged.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed attacker payload, ...)`, believing the attacker's payload originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
