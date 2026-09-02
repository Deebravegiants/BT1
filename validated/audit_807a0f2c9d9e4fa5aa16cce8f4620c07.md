### Title
Webhook `shop` and `topic` identifiers are trusted from unauthenticated headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body (`to_signable_string` returns `@raw_body`), while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers that are never included in the signed material. `Registry.process` verifies only the body's HMAC, then trusts the unauthenticated `shop` header to route/attribute the webhook to a tenant.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received signature. [1](#0-0) 
For webhook requests, `to_signable_string` returns only `@raw_body`; the `shop` accessor pulls the tenant identity straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed string. [2](#0-1) 
`Registry.process` validates the HMAC and then immediately passes the unauthenticated `request.shop` into `WebhookMetadata`, which the host app's handler uses to attribute the webhook body to a specific merchant/tenant. [3](#0-2) 

This breaks the intended binding: `shop header used for tenant attribution == shop that produced/authorized the signed bytes`. Because the app's `client_secret`/webhook secret is shared across every merchant installation of the same app, any tenant that legitimately receives real Shopify webhooks (correctly signed with the app's shared secret) can capture a genuine `raw_body` + `X-Shopify-Hmac-Sha256` pair from their own shop, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header (or `x-shopify-shop-domain`). The HMAC check still passes because the signed bytes (raw body) are unchanged, but the `shop` value delivered to the handler now points to a victim tenant chosen by the attacker.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker who controls one shop's outbound webhook data can forge webhook payloads that are processed as if they came from any other shop of the app's choosing (as long as they can produce/capture one validly-signed body). Downstream handlers that key persistence, side effects, or shop-scoped data mutation off `WebhookMetadata#shop` (as documented and demonstrated in `docs/usage/webhooks.md`) will attribute attacker-controlled data to another merchant's tenant, i.e., cross-tenant data injection/confusion, which is a Critical-class impact per the scope's own criteria ("cross-tenant access").

### Likelihood Explanation
Exploitation requires a valid signed body/HMAC pair, which any merchant using the same app already legitimately receives for topics they subscribe to (e.g., `orders/create`); no access to `api_secret_key` or another tenant's credentials is needed—only capturing one's own webhook traffic and replaying it with a different header. This is fully reachable through the gem's documented `Registry.process` / `Request.new` flow with no reliance on host-app misuse of undocumented behavior.

### Recommendation
Include `shop`, `topic`, and any other identity-bearing values in the HMAC-signed material, or independently verify the `shop-domain` header against a value bound to the webhook subscription/session (e.g., cross-check against the shop that owns the corresponding registered webhook_id) before dispatching to a handler, rather than trusting an unauthenticated header for tenant attribution.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both webhooks signed with the same app secret.
2. Attacker subscribes to `orders/create` on their own shop and receives a legitimate webhook: `raw_body = B`, header `X-Shopify-Hmac-Sha256 = H` (valid signature of `B`), header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker POSTs to the app's webhook endpoint with the same `raw_body = B` and `X-Shopify-Hmac-Sha256 = H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds. [4](#0-3) 
5. `WebhookMetadata.new(topic: ..., shop: request.shop, body: request.parsed_body, ...)` is built with `shop = "victim-shop.myshopify.com"` even though the body content originated from the attacker's own shop, and is dispatched to the app's handler as if it were victim data. [5](#0-4)

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
