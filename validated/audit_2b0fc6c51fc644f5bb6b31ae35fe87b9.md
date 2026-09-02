This confirms the finding: `Webhooks::Request#to_signable_string` returns only `@raw_body`, excluding `shop`, `topic`, and `webhook_id` from the HMAC-signed content, while `Registry.process` trusts `request.shop` (from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) to attribute the webhook to a tenant.### Title
Webhook shop-domain identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` authenticates a webhook by validating the `X-Shopify-Hmac-Sha256` header against `@raw_body` only, but the `shop` (and `topic`/`webhook_id`) values used to attribute the webhook to a specific merchant are read from separate, unsigned HTTP headers. This breaks the intended binding `hmac == HMAC(secret, body ‖ shop)`; in this gem it is actually `hmac == HMAC(secret, body)`, with `shop` outside the signed material entirely, analogous to the primary/secondary debt inconsistency in the referenced report (one identity-relevant field is protected, a semantically equivalent one is not).

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `Request#shop`, `#topic`, and `#webhook_id` are pulled straight from attacker-controllable HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `to_signable_string`, i.e. the body — it never incorporates `shop`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then unconditionally trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) [5](#0-4) 

Because the same app-wide `client_secret` is used to sign every merchant's webhooks, and the shop identity is not part of the signed payload, a party who legitimately receives one valid `(raw_body, hmac)` pair (e.g., by installing the app on a shop they control, or by intercepting/replaying any webhook delivery) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary value in the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen shop instead of the shop the payload was actually generated for.

This is the direct analog of M-19: `updateAccountDebt` truncates the primary debt field but the parallel `_updateTotalSecondaryDebt` does not truncate the equivalent secondary debt field — here, the webhook signature covers the body but not the equivalent "shop" identity field, even though both should be bound together to preserve per-tenant integrity.

### Impact Explanation
This breaks the identity binding "shop authenticated == shop the app acts on" for every webhook handler built with this gem's documented pattern (`WebhookHandler#handle(data:)` trusting `data.shop`). An application that stores/updates per-shop state keyed by `data.shop` (the pattern explicitly shown in `docs/usage/webhooks.md`) can be made to apply a payload intended for shop A under the identity of shop B — a cross-tenant data-integrity/access issue, which maps to the "cross-tenant access" Critical impact category in scope.

### Likelihood Explanation
The attacker only needs to be able to obtain one valid `(body, hmac)` pair for the shared app secret — trivially achievable by installing/using the app on any shop they control (a legitimate, unprivileged action) — and then replay it against the same webhook endpoint with a forged `shop-domain` header. No access to `client_secret`, access tokens, or victim credentials is required, satisfying the "unprivileged internet user" constraint.

### Recommendation
Include the shop domain (and ideally topic and webhook id) in the signed material verified against the HMAC, or otherwise cryptographically bind the header-derived identity fields to the verified body (e.g., require the app layer to cross-check `request.shop` against a shop it independently expects for that delivery, or have `to_signable_string` incorporate the shop/topic headers consistent with how Shopify actually computes/validates them). At minimum, document that `Request#shop`/`#topic` are not covered by the HMAC and must not be trusted as the sole tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`, receiving a legitimately signed webhook: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for the app's shared `client_secret`), plus `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the exact same `B`/`H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` constructs `Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` and calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-computes HMAC over `B` [6](#0-5) 
4. The registered handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` and performs shop-scoped actions attributing attacker-controlled data to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
