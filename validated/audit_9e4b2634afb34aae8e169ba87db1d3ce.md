Confirmed: the webhook HMAC only covers `to_signable_string` (the raw body) via `ShopifyAPI::Webhooks::Request#to_signable_string` [1](#0-0) , while `shop` is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) . `Registry.process` validates only the HMAC over the body and then forwards `request.shop` straight into `WebhookMetadata` passed to the app's handler [3](#0-2) , and `WebhookMetadata.shop` is declared as a trusted `String` field with no indication it is unauthenticated [4](#0-3) .

### Title
Webhook tenant identity (`shop`) is not bound to the HMAC-verified payload, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw request body via `Utils::HmacValidator.validate(request)` [5](#0-4) . The `shop` value delivered to the app's handler, however, comes from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the signed content (`to_signable_string` returns only `@raw_body`) [1](#0-0) . This breaks the equality that should hold between "the tenant whose secret validated this HMAC" and "the tenant identity handed to the app," because the header can be freely set to any value while the body+HMAC pair remains valid.

### Finding Description
`Request#shop` is read directly from an attacker-controllable header with no cryptographic binding to the signed body [2](#0-1) . Because `HmacValidator.validate_signature` only recomputes the HMAC over `verifiable_query.to_signable_string`, which for a webhook `Request` is exclusively `@raw_body` [6](#0-5) , an attacker who can obtain any single valid `(raw_body, hmac)` pair signed with the app's `api_secret_key` (e.g., by installing the app on their own shop and capturing one of their own legitimate webhook deliveries) can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary victim shop domain in the `shop-domain` header. `Registry.process` will consider this a fully valid, authenticated webhook and dispatch `WebhookMetadata.new(shop: request.shop, body: request.parsed_body, ...)` to the app's handler [7](#0-6) , asserting attacker-controlled body content under the victim shop's identity.

The broken identity binding, stated as an equality that should hold but does not:
`shop authenticated by HMAC` ("the shop whose secret produced this HMAC over this body") ≠ `shop stored/used by the handler` (`request.shop`, taken from an unsigned header).

### Impact Explanation
Any app relying on `WebhookMetadata.shop` to select which tenant's data/session the webhook body applies to (a documented and expected usage pattern per `docs/usage/webhooks.md`, which shows `data.shop` used directly to key background jobs) would process attacker-supplied body content as if it originated from and applies to an arbitrary victim shop. This is a cross-tenant data-integrity/access issue: an attacker can inject fabricated events (e.g., fake `orders/create`, `app/uninstalled`, GDPR topics) attributed to a victim shop, using only a body+HMAC pair legitimately obtained from their own tenant. This satisfies the "cross-tenant access" critical impact category.

### Likelihood Explanation
The webhook endpoint is a public HTTP endpoint by design (the app must expose it to receive Shopify's webhook POSTs), so no privileged credential is required beyond installing the target app on an attacker-controlled shop to capture one legitimate `(body, hmac)` pair — something any developer/tester can trivially obtain. No `api_secret_key`, access token, or victim-side compromise is needed; only network access to the app's public webhook route and possession of any one valid signed body from the same app's secret.

### Recommendation
Bind the `shop` identity into the HMAC-verified content, not just the header. Concretely:
1. Include the shop domain header value in the signable string used by `HmacValidator` for webhook requests (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` explicitly includes `shop` in its signed parameters) [8](#0-7) , or
2. Cross-check `request.shop` against a shop identifier embedded in the verified JSON body (where the topic's payload includes one), rejecting mismatches, and
3. Document clearly in `WebhookMetadata`/`Request` that `shop` is derived from an unauthenticated header unless bound as above, so integrators are not misled into trusting it as tenant-authenticated.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery: raw body `B` with header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `api_secret_key`) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `B` and succeeds [5](#0-4) .
4. The handler registered for the topic in `B` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [7](#0-6) , causing the app to process attacker-chosen data under the victim tenant's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
