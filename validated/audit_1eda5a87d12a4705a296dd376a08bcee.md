### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, never the `shopify-shop-domain` / `x-shopify-shop-domain` header, yet `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` as the tenant identifier when dispatching the webhook payload to the registered handler. Because the HMAC signature never binds the `shop` value, an attacker who possesses one valid `(body, hmac)` pair for the shared app secret can replay it with an arbitrary `shop-domain` header and have the payload accepted and dispatched as if it belonged to a different shop.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` and compares it (constant-time) to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be just the raw request body: [2](#0-1) 

while `shop` is read from a separate, unauthenticated header: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` validates only the HMAC of the body and then unconditionally forwards `request.shop` (and `request.topic`, `request.webhook_id`, `request.api_version` — also unauthenticated headers) to the app's handler as the tenant/shop identity: [4](#0-3) 

The identity binding that should hold is:
`shop_header == shop_that_produced_this_HMAC_signed_body`

But the implementation only proves `hmac == HMAC(secret, body)`; it never proves anything about which shop that body/HMAC pair actually belongs to. Any entity that can obtain one legitimate `(body, hmac)` pair signed with the app's own `client_secret` — for example the developer/owner of any shop that has the same app installed, who can trigger a webhook on their own store and observe Shopify emit a validly-signed request to the app's webhook endpoint (or otherwise capture one) — can resend that exact body+hmac pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop. `HmacValidator.validate` still succeeds because it never inspected the shop header, and `Registry.process` dispatches the handler believing the event originated from the victim shop.

### Impact Explanation
This breaks the tenant-authentication boundary the webhook mechanism is meant to enforce: verified bytes (the HMAC-covered body) are decoupled from the trusted identity field (`shop`) that host applications key their tenant data storage/session lookup on. An attacker with a legitimate webhook from their own store can inject attacker-controlled event data attributed to a different, victim shop, leading to cross-tenant data corruption/confusion in any application that uses `WebhookMetadata#shop` to select which tenant's records to update — this is a cross-tenant access primitive, matching the Critical impact bucket ("cross-tenant access").

### Likelihood Explanation
Exploitability requires the attacker to have obtained at least one HMAC-valid `(body, hmac)` pair produced with the app's shared `client_secret`. Any user who legitimately installs the target app on their own store can trigger events and observe/replay the webhook Shopify sends to the app (same secret is shared across all shops using that app installation), so this does not require leaking the secret itself — only having a normal, low-privilege relationship with the app. The webhook HTTP endpoint is by design internet-reachable and unauthenticated aside from the HMAC check, so the replay with a substituted header is trivial once a valid pair is available.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signable string, or otherwise cryptographically bind the shop identity to the signed body (e.g., verify shop domain against a value looked up from the app's own session store keyed by a value that IS covered by the signature) before dispatching to handlers in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook event (e.g., `orders/create`) and capture the raw request Shopify sends to the app's webhook endpoint, including `x-shopify-hmac-sha256` and body.
2. Resend the identical body and `x-shopify-hmac-sha256` header to the same webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (body/hmac unchanged), and `ShopifyAPI::Webhooks::Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)`, as shown at: [5](#0-4)

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
