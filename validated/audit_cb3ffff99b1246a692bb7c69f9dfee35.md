### Title
Webhook Shop Domain Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw request body via HMAC, while the `shop-domain` header — which the library treats as the authoritative tenant identifier passed to the app's webhook handler — is never included in the signed payload. Any attacker who can obtain one validly-signed webhook body (e.g., by installing the app on their own shop and receiving a real webhook) can replay that body with an arbitrary `shop-domain` header, and `Registry.process` will accept it as authentic for the spoofed shop.

### Finding Description
`Utils::HmacValidator.validate` verifies the request by computing `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and comparing it to the presented `hmac`. [1](#0-0) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — the header-derived `shop`, `topic`, `webhook_id`, and `api_version` values are excluded from what is signed. [2](#0-1) 

`Registry.process` relies solely on this HMAC check as its authenticity gate, then immediately trusts `request.shop` (parsed straight from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header) as the tenant identity forwarded to the app's handler via `WebhookMetadata`: [3](#0-2) 

Because the HMAC secret is the app's single `client_secret` — shared across every shop that has installed the app — rather than a per-shop secret, the signature only proves "this body was signed by holders of this app's secret," not "this body belongs to shop X." The `shop-domain` header, which is the field the equality `shop authenticated == shop trusted for tenant routing` is supposed to bind, is verified-but-not-bound: it is validated to exist (`request.rb` lines 50-58) but never covered by the cryptographic check.

An unprivileged internet user who can install the target app on their own store will legitimately receive real, correctly-HMAC-signed webhook deliveries from Shopify for their own shop. They can capture one such `(raw_body, hmac)` pair and resend it to the app's webhook endpoint with the `shop-domain` header changed to point at a victim shop. `HmacValidator.validate` still succeeds (it only checks the body/secret), so `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: request.shop, ...)` set to the victim's domain, even though the body's HMAC has no relationship to that shop at all.

### Impact Explanation
This breaks the tenant-identity binding the library is meant to guarantee: `shop` authenticated by the signature check should equal the `shop` value acted upon by the handler, but here the acted-upon `shop` is taken from bytes outside the signed scope. Any app that keys per-tenant state (installation status, tokens, mandatory GDPR topics like `shop/redact`, `customers/redact`, `customers/data_request`, order/product sync state, etc.) off `WebhookMetadata#shop` can be made to apply attacker-supplied webhook payloads to a victim shop's tenant record — a cross-tenant access/injection primitive.

### Likelihood Explanation
Exploitation requires only an unprivileged actor able to install the target app on a shop they control (the normal, unauthenticated app-installation flow) and the ability to send an HTTP POST to the app's public webhook endpoint with modified headers — no access token, `client_secret`, or privileged account is needed. This satisfies the in-scope "unprivileged internet user" threat model.

### Recommendation
Bind the tenant identifier into the signed material, e.g. include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise cryptographically bind the header values to the body before computing/verifying the HMAC), so `Registry.process` cannot be tricked into accepting a validly-signed body for a shop it was never issued to. At minimum, document and enforce that consumers must independently verify `request.shop` corresponds to a shop with an active session/installation before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (public, unauthenticated OAuth install flow).
2. Shopify delivers a real webhook to the app, e.g. `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(client_secret, B)` — attacker records `(B, H)`.
3. Attacker replays the request to the app's webhook endpoint, keeping body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC_SHA256(client_secret, B)` — matches `H` since the body is unchanged — validation passes. [4](#0-3) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker-controlled parsed body>, ...)`, causing the app to process attacker-controlled order data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
