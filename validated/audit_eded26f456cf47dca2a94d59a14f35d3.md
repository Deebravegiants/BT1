This confirms the root cause: `ShopifyAPI::Webhooks::Request#to_signable_string` (line 36-38) returns only `@raw_body`, while `shop` (line 20-23) is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the HMAC-signed content. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) validates the HMAC over the request and then dispatches to the handler using `request.shop` as the tenant identifier, without ever checking that this header was itself covered by the signature.

### Title
Webhook shop-domain header is not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only [1](#0-0) , but the `shop` value used to identify which tenant a webhook event belongs to is read straight from the `shopify-shop-domain` header without being part of that signed content [2](#0-1) . `Registry.process` validates the HMAC and then hands `request.shop` straight to the app's handler as the authoritative tenant identity [3](#0-2) .

### Finding Description
The identity binding broken here is: `shop header used by the handler` ≠ `shop bound by the HMAC signature`. Because the app's shared secret is the same across all shops that install the app, and only the raw body bytes are ever fed into `OpenSSL::HMAC.hexdigest` [4](#0-3) , any HTTP request that supplies a body+HMAC pair that was legitimately generated for shop A (e.g. an attacker's own shop, which they legitimately control and receive real webhooks for) remains "valid" under `HmacValidator.validate` even if the `shopify-shop-domain` header is replaced with victim shop B's domain. The `Registry.process` method never cross-checks the header-derived `shop` against anything bound by the signature — it simply passes it into `WebhookMetadata.new(... shop: request.shop ...)` for the handler to trust [5](#0-4) .

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook consumers: an app handler that uses `WebhookMetadata#shop` to look up/update per-tenant state (sessions, settings, order data, etc.) can be made to act on behalf of a shop the attacker doesn't control, by replaying a self-obtained, validly-signed webhook body with a forged `shop-domain` header. This is a cross-tenant confusion vulnerability consistent with the Critical severity bar for cross-tenant access.

### Likelihood Explanation
Exploitation requires only that the attacker (1) installs the app on their own shop — an unprivileged, ordinary action — to legitimately receive one valid webhook body+HMAC pair, and (2) can reach the app's public webhook endpoint directly with a modified `shop-domain` header while keeping the original body and HMAC. No access token, `client_secret`, or privileged credential is needed, since the gem itself does not bind the header to the signature.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook-id`) header values in the signable string used for HMAC computation, or otherwise cryptographically bind the header-derived identity to the verified payload before it is exposed via `WebhookMetadata`, so `Registry.process` cannot be tricked into associating a validly-signed body with an attacker-chosen shop.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body `B` and the `shopify-hmac-sha256` header `H` that Shopify computed for it — both fully legitimate since the attacker owns that shop.
2. Attacker sends `POST` to the app's webhook endpoint with body `B`, header `shopify-hmac-sha256: H` (unchanged), `shopify-topic: orders/create` (unchanged), but `shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and matches `H`, so the check in `Registry.process` passes: `raise ... unless Utils::HmacValidator.validate(request)` does not fire [6](#0-5) .
4. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's order data>, ...)`, believing the event genuinely originated from `victim.myshopify.com`, even though it never sent this webhook.

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
