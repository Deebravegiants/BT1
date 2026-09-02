## Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, and then hands `request.shop` — the merchant/tenant identity — straight to the app's handler. However the HMAC signature only covers the raw request body; the `shop` value is read from an HTTP header that is never included in the signed bytes. This breaks the equality that the framework implicitly promises: `hmac_verified(bytes) == identity_bound(shop)`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

`to_signable_string` returns only `@raw_body`, while `shop` is read from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is completely disjoint from the signed payload.

`Utils::HmacValidator.validate` computes the HMAC solely over `to_signable_string` (the raw body) and compares it to the `hmac` header value: [2](#0-1) 

`Registry.process` uses this single check to gate trust for the *entire* request, then forwards the unauthenticated `request.shop` header value to the app's handler as if it were verified: [3](#0-2) 

Because the app's `api_secret_key` is shared across all shops that install the app (it is not shop-specific), any tenant that has installed the app can obtain a validly-HMAC-signed webhook body for their own shop (e.g., by triggering any webhook topic on their own store and capturing the raw request). That attacker can then replay the exact same `raw_body` + `hmac` header pair to the app's webhook endpoint while substituting the `shop-domain`/`x-shopify-shop-domain` header with an arbitrary victim shop domain. `HmacValidator.validate` still returns `true` (it never looked at the header), and `Registry.process` calls `handler.handle` with `data.shop` set to the attacker-chosen victim domain and `data.body`/`data.topic` under the attacker's control.

This is exactly the "field acted on but not covered by the HMAC" identity-binding failure: the equality that should hold — `shop_the_signature_was_issued_for == shop_the_handler_believes_it_is_processing` — does not hold anywhere in this code path.

### Impact Explanation
This enables cross-tenant confusion/spoofing: any low-privileged tenant of the app can cause the host application to process fabricated webhook events (arbitrary topic/body) attributed to a shop domain of their choosing. Depending on how the host app's handler uses `data.shop` (e.g., looking up and mutating a session/merchant record, honoring GDPR mandatory topics such as `shop/redact` or `customers/redact`, or triggering `app/uninstalled` cleanup), this can lead to cross-tenant data manipulation or denial of a victim merchant's app functionality — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Any actor who can install the app on their own (attacker-controlled) shop — the normal, unprivileged path for using a public/embedded Shopify app — can trigger a real webhook for their store, capture the raw body + HMAC header, and replay it to the app's registered webhook endpoint with a forged `shop-domain` header. No access to the app's `api_secret_key`, access tokens, or any victim credentials is required.

### Recommendation
Bind the `shop` identity into what is actually authenticated. Concretely:
- Do not trust `request.shop` from the header alone as the tenant identity for dispatch; cross-check it against the shop found in `request.parsed_body` (Shopify webhook payloads for most resource topics include shop-scoped identifiers) where feasible, or
- Require host applications to correlate `request.shop` with an already-established, stored session for that shop before acting on the payload, and document this requirement prominently, or
- At minimum, expose a way to verify that the webhook's `shop` header matches the shop the webhook subscription was registered for, rather than implicitly trusting any header value once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers for any webhook topic (e.g. `orders/create`).
2. Attacker triggers that topic on their own store, capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent — this HMAC is valid because it's computed with the app's shared `api_secret_key` over the raw body only.
3. Attacker sends a new POST to the app's webhook endpoint, reusing the identical raw body and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and desired `x-shopify-topic` (already valid since unchanged).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the (unchanged) body against the (unchanged) hmac and returns `true`.
5. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, causing the host app to act as if the victim shop sent this webhook. [4](#0-3) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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
