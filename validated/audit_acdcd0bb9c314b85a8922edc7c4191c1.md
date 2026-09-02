### Title
Webhook `shop` and `topic` fields are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` verifies only that the body's HMAC is valid, then dispatches the handler using the unverified header values, breaking the equality `shop_bound_by_hmac == shop_used_by_handler`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are all pulled directly from headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` computes the signature over `to_signable_string` (the body) and compares it against the `hmac` header — it says nothing about the other headers: [3](#0-2) 

`Registry.process` accepts the request purely on this body-HMAC check, then builds `WebhookMetadata` using `request.shop` and `request.topic` taken from the (unverified) headers: [4](#0-3) 

Because Shopify webhooks for a given app are all signed with the same `api_secret_key` regardless of which shop triggered them, any merchant who has installed the app can legitimately receive a webhook with a valid HMAC for some body. Since the header set (`shop-domain`, `topic`, `webhook-id`) is not part of the signed content, that same body+HMAC pair can be replayed to the app's webhook endpoint with the `shop-domain` header rewritten to a different (victim) shop and/or the `topic` rewritten to a different registered topic. The signature still validates because it only attests to the body bytes, not to which shop or topic they are claimed to belong to.

### Impact Explanation
This breaks the tenant boundary the host application relies on: the "authenticated" shop (verified via HMAC) is not the same as the shop that the webhook handler is told the data belongs to. A host app that keys business logic (e.g., updating inventory, order state, billing, or customer data) off `WebhookMetadata#shop` can be tricked into applying data intended for the attacker's own shop to a different tenant's shop record — a cross-tenant data integrity/isolation violation, which the rules classify as Critical.

### Likelihood Explanation
Any unprivileged actor who can install the app on their own store (or otherwise trigger events on any Shopify shop that has it installed) can capture a genuine webhook body/HMAC pair from their own tenant traffic and replay it with altered headers. No access token, `client_secret`, or privileged account is required — only the ability to receive one webhook for their own shop and re-POST it with modified headers to the app's public webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable content verified against the HMAC (or otherwise cryptographically bind them, e.g., by re-deriving/checking them against a value stored server-side that is tied to the delivery), rather than trusting header values purely because the body's HMAC is valid.

### Proof of Concept
1. Attacker installs the target app on their own store (`attacker-shop.myshopify.com`) and triggers any registered webhook topic (e.g., `orders/create`), legitimately receiving from Shopify: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's `api_secret_key`), `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker POSTs the same `B` and `H` to the app's webhook endpoint again, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC of `B` and compares to `H` — validation succeeds because the header was never part of the signed content (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to process attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
