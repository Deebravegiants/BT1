This confirms the vulnerability: the gem's own documentation (`docs/usage/webhooks.md`, lines 12-14, 25-26) explicitly instructs developers to trust `data.shop` — sourced from the unauthenticated `X-Shopify-Shop-Domain` header — as the tenant identity to act on (`shop_domain: data.shop`), while `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) only checks `Utils::HmacValidator.validate(request)`, whose `to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) covers `@raw_body` alone. This is a genuine, gem-documented-API-consistent binding break, not one that "depends on the host application ignoring this gem's documented API" — the host app is doing exactly what the docs say.

### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the shop identity (`shop`) exclusively from the `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` HTTP header [1](#0-0) , but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` verifies via `Utils::HmacValidator.validate(request)` only covers the raw request body [2](#0-1) . The `shop` header is therefore not bound to the signature at all.

### Finding Description
The equality broken here is: **`shop` field acted upon by the application == `shop` field authenticated by the HMAC**. In `Request#to_signable_string`, only `@raw_body` is signed [2](#0-1) , while `Request#shop` is read straight from an attacker-controllable HTTP header with no cryptographic tie to that signature [1](#0-0) .

`Registry.process` only validates the HMAC and then immediately forwards `request.shop` to the app-provided handler as the trusted tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [3](#0-2) .

Because the `client_secret`/HMAC key is shared across all shops installed on a given app (it is not per-shop), any actor who can obtain one valid `(raw_body, HMAC)` pair signed by Shopify for *any* shop on the app — e.g., a merchant who installed the app on their own store and can observe/replay their own legitimate webhook delivery — can resend that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still succeed because it never inspected the header [4](#0-3) , and the handler will process the payload under the spoofed shop identity.

This is not a case of the host app ignoring documented behavior — the gem's own documentation instructs consumers to treat `data.shop` as the authoritative per-shop key: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [5](#0-4) .

### Impact Explanation
An unprivileged actor (a merchant of shop A, or anyone who can capture one legitimate webhook delivery) can cause the app to attribute another shop's — or a fabricated — webhook body to a victim shop B's tenant record, corrupting per-tenant state, triggering unauthorized actions (e.g., `perform_later` jobs keyed off `data.shop`), or exfiltrating cross-tenant information depending on how the host app's handler uses `data.shop`. This is a cross-tenant identity-binding break, matching the Critical "cross-tenant access" category, since the shop the app acts on is decoupled from the shop Shopify actually signed for.

### Likelihood Explanation
High. No secret material is required by the attacker beyond a single previously-observed valid webhook (which any installed merchant naturally receives for their own store, or which could be replayed from logs/monitoring proxies). The only header required to change (`X-Shopify-Shop-Domain`) is explicitly excluded from the signed content by design of `to_signable_string`.

### Recommendation
Bind the shop domain (and other identity-relevant headers such as `topic`/`webhook_id`, if they influence trust decisions) into the signed material used for verification, or otherwise cryptographically or contextually verify that the shop header corresponds to a shop actually authorized to send the received body (e.g., cross-check against the currently registered shop sessions, or require the handler layer to independently authenticate `shop` before trusting it). At minimum, update the documentation to explicitly warn that `data.shop` is unauthenticated and must not be trusted as a tenant boundary without additional verification.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`, sharing the same `client_secret`.
2. Shopify sends a legitimate webhook to the app for `shop-a.myshopify.com`: body `B`, header `X-Shopify-Shop-Domain: shop-a.myshopify.com`, header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`.
3. An actor with access to that delivery (e.g., the merchant of shop A viewing delivery logs, or a network intermediary) resends the identical `B` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `to_signable_string` returns `B` unchanged [2](#0-1) .
5. `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)` and it matches the (unchanged) received signature — validation passes [6](#0-5) .
6. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: <parsed B>, ...)` [7](#0-6) , causing shop A's data to be processed under shop B's identity.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
