## Title
Webhook shop identity forgery via unauthenticated `shop-domain` header not covered by HMAC — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop` value taken from the `X-Shopify-Shop-Domain` header — a field that is never included in the signed payload — to identify which tenant the webhook belongs to.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` (and `topic`, `webhook_id`, `api_version`) accessors are read straight from HTTP headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then hands the unauthenticated `request.shop` header value directly to the app's handler as the trusted tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body), confirming the header is outside the signed scope: [4](#0-3) 

The binding that is broken is: **`shop` trusted by the app handler == `shop` covered by the HMAC**. In fact, `shop-domain` header value ≠ any HMAC-signed field, so the equality never holds and is never checked.

### Impact Explanation
An unprivileged internet user who controls any shop that has the target app installed will legitimately receive real webhooks from Shopify, each with a valid `X-Shopify-Hmac-Sha256` value computed only over the raw body. Because the signature never covers `X-Shopify-Shop-Domain`, the attacker can resend that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `shop-domain` header with any other shop domain served by the same app. `Utils::HmacValidator.validate` will still pass (it only checks the body signature), and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen value. Any host app that relies on this gem's documented `data.shop` (as instructed in `docs/usage/webhooks.md`) to scope side effects (e.g. GDPR `customers/redact` / `shop/redact` handling, applying an update against "the shop" context, looking up per-shop session/access-token) will act on the wrong tenant — a cross-tenant access/data-integrity break using only the attacker's own legitimately-received webhook material.

### Likelihood Explanation
High. Any merchant/developer who installs the target app on their own shop automatically receives correctly-HMAC-signed webhooks they can replay. No credentials, leaked secrets, or privileged access are required — only their own shop's legitimate webhook traffic and the ability to send an HTTP POST with modified headers to the app's public callback URL.

### Recommendation
Include `shop-domain` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed payload verification, or otherwise cryptographically bind the shop identity to the signed body (e.g., require the app to independently confirm the shop against a value derived from the signed content, not from a mutable header). At minimum, document/enforce that `Registry.process` must reject requests where the header-derived `shop` cannot be corroborated against signed data.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` with the app's `client_secret`), header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the identical `B`/`H` pair to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`.
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198`), causing the host app to process attacker-supplied webhook data under the victim shop's tenant context.

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
