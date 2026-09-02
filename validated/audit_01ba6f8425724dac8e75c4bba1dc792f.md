I have sufficient evidence to confirm the finding.

### Title
Webhook shop identity spoofing via unauthenticated `X-Shopify-Shop-Domain` header not covered by HMAC - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) fields entirely from HTTP headers, while the HMAC signature that `Registry.process` validates covers **only the raw request body**. Because the shop-domain field that the host app relies on for tenant identity is never part of the signed content, an attacker who can obtain one validly-signed webhook body (e.g. by triggering a webhook from their own shop, which has the app installed) can replay that same body with a forged `X-Shopify-Shop-Domain` header pointing at a different, victim shop, and the gem will accept it as authentic.

### Finding Description
`Registry.process` validates authenticity solely with `Utils::HmacValidator.validate(request)`, which for a `Webhooks::Request` computes the HMAC over `to_signable_string`, defined as just `@raw_body`: [1](#0-0) 

The `shop` accessor, by contrast, is read straight from the (fully attacker-controllable when replaying) HTTP headers and is never included in the signed string: [2](#0-1) 

`Registry.process` then trusts this unauthenticated `shop` value and forwards it straight into `WebhookMetadata`, which is handed to the app's handler as the tenant identity for the webhook payload: [3](#0-2) 

`HmacValidator.validate` confirms only that the secret-keyed HMAC matches the signable string (the body), with no binding to headers at all: [4](#0-3) 

This breaks the identity binding that the recommendation rule calls out: `shop authenticated == shop the app trusts as the tenant source of the payload`. In reality, `shop verified` (nothing, since it's outside the HMAC) != `shop acted on` (the header value handed to the app's handler).

Since the HMAC secret (`Context.api_secret_key`, i.e. the app's `client_secret`) is the same across all shops that install the app, any shop that installs the target app can generate a validly-signed webhook body for itself. Replaying that same body with a modified shop-domain header produces a request that passes `Registry.process`'s only authenticity check while claiming to originate from an arbitrary victim shop.

### Impact Explanation
This is a cross-tenant confusion vector: an unprivileged attacker (any merchant/shop that can install the target app) can cause the host application's webhook handler to process attacker-supplied data (topic, body, webhook_id) under the identity of a shop they do not own. Depending on how the host app uses `data.shop` (as documented in `docs/usage/webhooks.md` — used to look up the tenant/session and drive tenant-scoped side effects such as data sync, redaction, or state changes), this can lead to cross-tenant data corruption or spoofed lifecycle events (e.g., forged `app/uninstalled`, `shop/redact`) attributed to a shop the attacker doesn't control, satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is high for any attacker who can install the app on their own shop (a normal, unprivileged action for any Shopify merchant): they can trigger a real webhook for their own shop to obtain a validly-signed body/HMAC pair, then replay it against the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header. No credentials, access tokens, or `client_secret` knowledge are required — only observation of one legitimately delivered webhook.

### Recommendation
Bind the shop identity into the signed content, or otherwise cryptographically tie the header-derived `shop` value to the verified payload:
- Prefer deriving/validating the shop from data that Shopify signs (or use mTLS/allow-listed Shopify IPs as defense in depth), and/or
- Require the host app to independently verify that `data.shop` corresponds to a shop for which this specific webhook subscription was registered, rather than trusting the header verbatim in `Registry.process`.
- At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted as a tenant boundary without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers for a webhook topic (e.g., `orders/create`).
2. Attacker triggers the webhook (e.g., creates an order), and captures the raw POST: body `B`, and header `X-Shopify-Hmac-Sha256: H` (valid, since `H = HMAC-SHA256(client_secret, B)`), along with `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends the exact same request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com` (keeping body `B` and `X-Shopify-Hmac-Sha256: H` unchanged).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which only recomputes/compares the HMAC over `B` — it passes.
5. `WebhookMetadata.new(shop: "victim.myshopify.com", body: B, ...)` is delivered to the app's handler, which processes attacker-controlled data attributed to `victim.myshopify.com`.

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
