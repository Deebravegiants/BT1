### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` validates a webhook's authenticity using `Utils::HmacValidator.validate`, which recomputes the HMAC only over `to_signable_string`, which returns the raw body only. The `shop` (tenant identifier) exposed via `request.shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header and is never part of the signed material, so it can be swapped by anyone relaying a validly-signed body while the HMAC check still passes.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements the `Utils::VerifiableQuery` interface, which requires `hmac` and `to_signable_string`. Its `to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` accessor, however, is derived independently from the `shop-domain` header and is not part of that signable string: [2](#0-1) .

`Utils::HmacValidator.validate` verifies the request purely by recomputing `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and comparing it with the `hmac` header: [3](#0-2) . Since `to_signable_string` never includes `shop`, the equality the code is actually proving is `HMAC(secret, raw_body) == received_hmac`, not `HMAC(secret, raw_body ++ shop) == received_hmac`. `Webhooks::Registry.process` treats a passing HMAC check as sufficient proof of the request's tenant and forwards `request.shop` straight into the handler payload: [4](#0-3) .

Because the header carrying the tenant identity (`shop`) is decoupled from the field that is cryptographically bound (`raw_body`), any party who can obtain one genuinely-signed `(raw_body, hmac)` pair — e.g. by installing the public app on their own store and receiving a legitimate webhook for it — can resend that exact body/hmac pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a different shop's domain. `HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` hands the forged `shop` value to the handler as if the event genuinely originated from that other shop.

### Impact Explanation
This breaks the binding "shop authenticated == shop the event is attributed to." A host application that keys tenant-scoped side effects (e.g., updating shop-specific records, granting entitlements, triggering `shop/redact` style mandatory compliance flows) off `WebhookMetadata#shop` can be made to act on behalf of, or against, a shop the caller does not control — a cross-tenant integrity issue rooted entirely in this gem's webhook verification logic, since consumers are given no documented way to independently re-verify `shop` against the signed payload.

### Likelihood Explanation
Medium: exploitation requires the attacker to first obtain at least one legitimately-signed webhook body (trivial for an attacker who installs the target public app on their own store, since app installation by any merchant is a normal, unprivileged action) and a webhook endpoint that accepts arbitrary `shop` values without external re-validation, which is exactly what this gem provides.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signable string used for verification, or have `Webhooks::Registry.process`/the consuming application cross-check the `shop` header against an independently trusted source (e.g., an installed session for that shop) before dispatching to handlers, so that a replayed body cannot be reattributed to an arbitrary tenant.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers an event so Shopify sends a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H`, header `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only [1](#0-0)  and succeeds because `B` and `H` are unchanged.
4. `handler.handle` is invoked with `WebhookMetadata` carrying `shop: "victim.myshopify.com"` [5](#0-4) , even though the payload actually originated from `attacker.myshopify.com`.

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
