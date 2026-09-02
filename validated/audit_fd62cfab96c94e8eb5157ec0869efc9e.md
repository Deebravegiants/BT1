## Finding: Webhook shop-domain header is not covered by the HMAC signature

### Title
Cross-tenant webhook shop-domain spoofing via HMAC signing gap - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` (tenant identifier) is read from a separate, unsigned header. `ShopifyAPI::Webhooks::Registry.process` validates the body's HMAC but then hands the unsigned `shop` value straight to the app's webhook handler as the trusted tenant identity, breaking the binding: `HMAC-covered bytes == bytes acted on as the shop identity`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor reads the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)` (which hashes `request.to_signable_string`, i.e. the body only) and, once that check passes, forwards the unsigned `request.shop` value to the app's handler as the authoritative tenant identity: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm the HMAC is computed purely from `verifiable_query.to_signable_string` (the body) against `Context.api_secret_key`: [4](#0-3) 

Because the shop-domain header sits outside the HMAC-covered bytes, a payload body+HMAC pair genuinely produced by Shopify for one shop (e.g. an attacker's own store, which they fully control and can trigger real webhook events from) remains cryptographically valid when replayed with the `shop`-domain header swapped to a different (victim) shop. `WebhookMetadata.shop` — the field host applications rely on to select which tenant's session/state to act on — is therefore attacker-controllable despite HMAC verification succeeding.

### Impact Explanation
This breaks the identity binding `HMAC-verified bytes == bytes used to select the tenant`. An unprivileged attacker who owns any Shopify store can generate authentically-signed webhook bodies for topics they control (e.g. `app/uninstalled`, `shop/update`, `orders/create`, etc., depending on what's subscribed) and replay them with an arbitrary victim `shop` domain in the header. Any host application that trusts `WebhookMetadata#shop` (as documented/intended usage of this gem's webhook API) to route or key its per-tenant logic will process the event as if it originated from the victim tenant — a cross-tenant access/confusion vector, matching the CWE-1284/Improper Validation of Specified Quantity in Input class cited in the report (data was HMAC-validated in scope, but a field used for authorization decisions falls outside that scope).

### Likelihood Explanation
Likelihood is High for any app that has at least one Shopify store account (trivial to obtain) and subscribes to webhooks whose body content the attacker can influence or replicate. No access token, `client_secret`, or privileged credential is required — only a standard, self-provisioned Shopify shop to generate legitimately-signed webhook traffic.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) values in the HMAC-signable string, or otherwise cryptographically bind them to the verified body (e.g., verify the header-provided shop against a shop-scoped secret, or require the host app to independently confirm the shop via a separate authenticated channel) before exposing them to `WebhookMetadata`.

### Proof of Concept
1. Attacker registers a normal Shopify development store and installs the target app so it subscribes their store to a webhook topic (e.g. `orders/create`).
2. Attacker triggers the real webhook from their own store, capturing the genuine `x-shopify-hmac-sha256` header and raw body Shopify sends (HMAC signed only over the body).
3. Attacker resends this exact body + hmac header to the app's webhook endpoint, but overwrites `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `HmacValidator.validate` succeeds because `to_signable_string` only checks the (unmodified) body. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host app to act on the victim tenant's behalf using attacker-supplied payload data.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
