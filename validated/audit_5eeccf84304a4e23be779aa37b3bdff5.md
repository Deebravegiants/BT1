Confirmed: `Registry.process` validates only `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string` = `@raw_body` only [1](#0-0) , and then trusts `request.shop`, read verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, to build the `WebhookMetadata` handed to the app's handler [2](#0-1) . The `shop` header is never included in the signed payload [3](#0-2) , so it is not covered by the HMAC that authenticates the request.

### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (tenant) attribute is read from an unauthenticated HTTP header. `ShopifyAPI::Webhooks::Registry.process` verifies only that the body's HMAC is valid and then unconditionally trusts the header-derived `shop` value when dispatching to the app's webhook handler. This breaks the identity binding: `shop-covered-by-hmac == shop-used-by-handler` does not hold, because `shop` is never part of the signed content.

### Finding Description
- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field [4](#0-3) .
- For webhooks, `to_signable_string` returns only `@raw_body` [1](#0-0) .
- `Request#shop` is derived purely from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is outside the signed data [3](#0-2) .
- `Registry.process` validates the HMAC once, then immediately trusts `request.shop` to construct the `WebhookMetadata` delivered to the app-defined handler, which apps use to attribute the event/data to a tenant [2](#0-1) .

Because the app-wide `api_secret_key` is shared across all shops that install the app, any shop that has installed the app can legitimately receive a real webhook (valid body + valid HMAC) from Shopify. An unprivileged attacker who owns such a shop can capture that body+HMAC pair (it stays valid since it depends only on the body) and replay it directly to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header value, e.g. a victim shop's domain. `HmacValidator.validate` will accept it because the body is unmodified, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity spoofing vulnerability: an attacker who has installed the app on their own shop (an unprivileged, low-trust tenant) can forge webhook deliveries that appear to originate from any other shop of their choosing. Depending on how the host application uses `WebhookMetadata#shop` (e.g., looking up per-shop session/access tokens, updating per-shop state, processing mandatory compliance topics like `customers/redact` or `shop/redact`), this can lead to cross-tenant data corruption, unauthorized actions taken against another merchant's data, or bypass of tenant isolation — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Any merchant/developer who installs the app (a low-privilege, unauthenticated-relative-to-other-tenants position) automatically receives real webhook traffic with valid HMACs tied to the shared `api_secret_key`. Capturing a `(raw_body, hmac)` pair requires no special access — it can be observed from the attacker's own webhook endpoint/logs. Forging the `shop` header on a replayed POST is trivial. No access token, `client_secret`, or privileged account is needed, only the fact that the gem itself never signs or otherwise authenticates the `shop` value it hands to the handler.

### Recommendation
Bind the `shop` identity into the value that is actually verified. Include the shop domain (and/or webhook id / topic) in the HMAC-signable string, or otherwise cryptographically bind the header-provided `shop` to the signed body before trusting it in `Registry.process`. At minimum, document/require callers to independently corroborate `shop` against a known, previously-established relationship (e.g., an existing session for that shop) before acting on webhook data, and consider that the current `to_signable_string` for `Webhooks::Request` should incorporate more than just the raw body.

### Proof of Concept
1. Install the app on an attacker-controlled shop `attacker.myshopify.com`. Trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify sends a real webhook to the app's endpoint with headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-hmac-sha256: <valid-hmac-of-body>`, and some JSON `raw_body`.
2. Capture the exact `raw_body` and `shopify-hmac-sha256` value from that legitimate delivery (available from the attacker's own server logs/tap).
3. Send a new POST request directly to the app's webhook endpoint with the same `raw_body` and `shopify-hmac-sha256`, but set `shopify-shop-domain: victim-shop.myshopify.com` (and any other unsigned headers such as topic/webhook-id as needed).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the signature check only covers `raw_body` [4](#0-3) ; the handler is then invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the request never came from Shopify on behalf of that shop [2](#0-1) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
