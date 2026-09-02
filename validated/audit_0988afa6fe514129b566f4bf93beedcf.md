### Title
Webhook shop, topic, and webhook_id fields are not covered by HMAC signature verification, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches to a handler using the `shop`, `topic`, and `webhook_id` values taken directly from unauthenticated HTTP headers. Because those fields are never included in the signed payload, an attacker who can obtain any one valid `(body, hmac)` pair can replay it with forged `shop-domain`/`topic`/`webhook-id` headers and have the app treat the request as an authenticated webhook for an arbitrary shop and topic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw body, excluding `shop`, `topic`, `api_version`, and `webhook_id`: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the signature strictly against `to_signable_string`, so it can only ever attest to the integrity of the body, never to the headers: [2](#0-1) 

`Registry.process` treats a passing HMAC check as full authentication of the request and then forwards the unauthenticated `shop`, `topic`, and `webhook_id` header values to the handler as trusted metadata, with no cross-check that they correspond to the shop/topic the body was actually signed for: [3](#0-2) 

This is the same bug class as the reference report: fields that are acted upon (here, the tenant identifier `shop`, plus `topic`/`webhook_id` used for routing and business logic) are excluded from the payload used for signature validation. Just as the Solidity contract let an attacker reuse a signature while altering `name`/`resolver`/`data`, this gem lets an attacker reuse a valid `(body, hmac)` pair while altering the `shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` headers — breaking the intended binding `shop_claimed_by_header == shop_the_hmac_was_actually_issued_for`.

### Impact Explanation
Any party capable of producing (or capturing) one legitimately-signed webhook body/HMAC pair for the app's `client_secret`-derived key (e.g., a merchant installing the app who receives their own legitimate webhook deliveries) can replay that exact body with a different `shop-domain` header. `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` object claiming the forged shop, topic, and webhook id — all values the handler is documented to trust once `Registry.process` succeeds. This crosses a tenant boundary: an app relying on `data.shop` to scope database writes/reads (the documented and expected usage) can be made to apply another merchant's request/forged content to a victim shop's records, i.e., cross-tenant data injection/impersonation.

### Likelihood Explanation
Exploitation requires possession of one valid `(raw_body, hmac)` pair signed with the app's secret. This is realistically obtainable by any installed/unprivileged merchant of a multi-tenant app (they legitimately receive their own webhook deliveries), or by anyone who can intercept/replay a webhook payload before header rewriting is blocked. No access token, `client_secret`, or privileged account is required — only observation of one webhook delivery which the gem's own design permits an unprivileged tenant to receive.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the value that is HMAC-verified (or otherwise cryptographically bind them to the body/signature), so that altering any of these header fields invalidates the signature — mirroring the remediation applied to `RegisterRequest` in the referenced report (include all fields relevant to the trust decision in the signed payload).

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com`, topic `orders/create`, with body `B` and valid `X-Shopify-Hmac-Sha256` header `H` (computed as `HMAC-SHA256(secret, B)`).
2. Attacker (e.g., merchant of `shop-a`, or anyone who captured the delivery) replays the exact same `B` and `H` to the app's webhook endpoint, but sets:
   - `X-Shopify-Shop-Domain: shop-b.myshopify.com`
   - `X-Shopify-Topic: orders/create` (or any registered topic)
3. `ShopifyAPI::Webhooks::Request.new` builds the request from these headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, B) == H`, per `lib/shopify_api/utils/hmac_validator.rb:27-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "shop-b.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled body content under the victim shop's identity — despite the payload never having been signed for `shop-b`.

### Citations

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
