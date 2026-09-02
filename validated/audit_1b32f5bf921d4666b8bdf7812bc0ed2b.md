### Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, enabling cross-tenant webhook confusion - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` and `topic` values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook are read from unauthenticated HTTP headers that are never included in the signed payload. An attacker who can obtain one legitimately signed webhook (e.g., a webhook delivered for their own installed shop) can replay that exact body/HMAC pair while substituting the `shop-domain` and/or `topic` headers, and the gem's `HmacValidator.validate` will still report success because it only checks the raw body bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) [2](#0-1) 

`hmac` is derived from the `X-Shopify-Hmac-Sha256` (or `shopify-hmac-sha256`) header, and `to_signable_string` returns only `@raw_body`. Meanwhile `shop` and `topic` are read directly from separate, independently-supplied headers: [3](#0-2) 

`Registry.process` verifies the HMAC and then trusts `request.topic` and `request.shop` for dispatch and tenant attribution without any cross-check that they were part of the signed material: [4](#0-3) 

`HmacValidator.validate` only recomputes the signature over `verifiable_query.to_signable_string` (the raw body) and compares it to the received `hmac`: [5](#0-4) 

This breaks the intended binding: `HMAC(secret, body) == received_hmac` is meant to authenticate "this body came from Shopify for this shop/topic", but the implementation only proves "this body came from Shopify for *some* shop/topic". The `shop` and `topic` headers are bytes-parsed but not bytes-verified — exactly the "bytes verified versus bytes parsed" identity-binding gap.

### Impact Explanation
Any unprivileged actor who can install the target app on their own store (a normal, unprivileged capability) will legitimately receive real webhook deliveries for their own shop, each with a valid HMAC over the body. Because the shop-domain and topic headers are outside the signed scope, the attacker can capture one such delivery and replay the identical `raw_body`/`hmac` pair to the app's webhook endpoint while swapping:
- `shop-domain` to a victim shop's domain — causing the handler to process/store data as if it came from a different tenant (cross-tenant data confusion), or
- `topic` to a different registered topic — causing a body crafted for one event type to be dispatched to a handler expecting a different schema/semantics (e.g., turning an innocuous webhook body into a trigger for a sensitive handler such as `app/uninstalled` or a data-deletion handler), amplifying the cross-tenant effect.

Since `WebhookMetadata.shop` is what most host applications use to look up/attribute the affected tenant, this can lead to cross-tenant access/corruption of another merchant's data purely by manipulating unauthenticated headers alongside a replayed, previously-valid signature — no possession of `client_secret` or any merchant credential is required beyond running the app on one's own store.

### Likelihood Explanation
Any developer/attacker with a free or trial installation of a Shopify app that uses this gem can trivially install it, trigger at least one benign webhook topic that is registered, capture the raw HTTP request (body + `hmac-sha256` header), and replay it against the endpoint with modified `shop-domain`/`topic` headers using any HTTP client. No special privileges, secrets, or timing are required, making this readily reachable.

### Recommendation
Include `shop`, `topic`, and `webhook_id`/`api_version` (or at minimum `shop` and `topic`) in the signed material verified by `HmacValidator`, or require the host application to independently bind the header-derived `shop`/`topic` to session/tenant context before dispatching to handlers. At minimum, document and enforce that `WebhookMetadata.shop`/`topic` must not be trusted for tenant attribution unless corroborated by a value that is part of the HMAC-signed payload.

### Proof of Concept
1. Install the app (using this gem) on attacker-controlled store `attacker.myshopify.com` and register a webhook for topic `carts/update`.
2. Capture a real Shopify-delivered webhook request: raw body `B`, header `shopify-hmac-sha256: H` (valid, since `H = HMAC(secret, B)`), `shopify-shop-domain: attacker.myshopify.com`, `shopify-topic: carts/update`.
3. Replay the same body `B` and header `H` to the app's webhook endpoint, but set `shopify-shop-domain: victim.myshopify.com` (and/or `shopify-topic:` to another registered topic handled by the app).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: replayed_headers)` builds successfully; `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`:
   - `request.to_signable_string` returns `B`
   - `HMAC(secret, B) == H` → validation passes
5. The handler is invoked with `WebhookMetadata.new(topic: <attacker-chosen topic>, shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host application to act on victim-shop context or on an attacker-chosen topic using attacker-supplied body content, despite the HMAC never having covered those values.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
