### Title
Webhook Shop-Domain Spoofing Enables Cross-Tenant Webhook Injection - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while `shop` (used to route/attribute the webhook to a tenant) is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is never included in the signed material. Any party that can obtain one validly-signed webhook body (e.g., by installing the app on their own store) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and dispatch it under the attacker-chosen shop.

### Finding Description
The webhook signable string is defined as just the raw body: [1](#0-0) 

`shop` is pulled straight from a header with no cryptographic binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` against `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` validates the HMAC, then trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` handed to the app's handler — none of these fields are part of the signed payload: [4](#0-3) 

Because all shops using a given app share the same `api_secret_key`, a valid `(raw_body, hmac)` pair captured from a webhook legitimately delivered to attacker-controlled shop A remains a valid `(raw_body, hmac)` pair regardless of which `shop-domain` header accompanies it. The identity binding that should hold — "the shop whose data the HMAC vouches for" == "the shop the application attributes the webhook to" — is broken: the HMAC vouches only for the body, but the application derives tenant identity from an unauthenticated header.

### Impact Explanation
This crosses a tenant boundary: an unprivileged internet user who merely installs the app on their own shop (no special privilege, no leaked secret, no access token needed) can forge webhook deliveries that the host application will process as originating from any other shop (`victim.myshopify.com`) merely by relabeling the `shop-domain` header on a replayed, validly-signed body. Any app logic that trusts `WebhookMetadata#shop` to select which tenant's records to create/update/delete (a very common pattern for `orders/create`, `app/uninstalled`, `customers/redact`, etc.) can be manipulated into writing attacker-supplied data into another merchant's tenant context — i.e., cross-tenant data injection/corruption.

### Likelihood Explanation
Moderate-to-high: no secret material is required beyond running the app on an attacker-owned shop, which is available to any unprivileged internet user (Shopify apps are typically installable by any store owner). The attacker only needs one webhook delivery with a body they want replayed and can trivially replay it with a different `shop-domain` header — no HMAC computation or key knowledge is needed, since the header is outside the signed portion of the payload.

### Recommendation
Include the shop/topic/webhook-id/api-version identity fields in the HMAC-signable string (or otherwise cryptographically bind them, e.g., HMAC over `"#{shop}\n#{topic}\n#{raw_body}"`), or require the host application to independently confirm `request.shop` corresponds to a shop with an active session/installation before trusting it for tenant attribution.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) with a body they fully control (their own order data).
2. Shopify delivers the webhook to the app with headers including a valid `x-shopify-hmac-sha256` computed over that raw body using the shared `api_secret_key`, and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures the raw body and its accompanying HMAC, then re-sends the exact same request to the app's webhook endpoint but with `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because `to_signable_string` never included the shop header (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`), so `Registry.process` dispatches the handler with `WebhookMetadata#shop == "victim.myshopify.com"` and attacker-controlled body content, even though the payload never originated from `victim.myshopify.com`.

### Citations

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
