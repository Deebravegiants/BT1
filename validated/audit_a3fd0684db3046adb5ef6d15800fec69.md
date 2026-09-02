### Title
Webhook HMAC does not bind the `shop-domain` header, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, while the `shop` value used by the webhook handler for tenant identification comes from an unauthenticated header. Any attacker who can obtain one valid `(body, HMAC)` pair from their own shop's legitimate webhook traffic can replay it with a different `shop-domain` header value and the HMAC check will still succeed, because that header is never part of the signed material.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that signature [2](#0-1) .

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string`, i.e. the body, and never inspects or incorporates the shop header [3](#0-2) .

`Webhooks::Registry.process` trusts `request.shop` as the tenant identity once the (body-only) HMAC check passes, and hands it directly to the application's webhook handler as the authoritative shop for that event [4](#0-3) .

This breaks the intended identity binding: `HMAC(secret, body) == received_hmac` is treated as proof that `(body, shop)` together originated from Shopify for `shop`, but the equality actually only proves `HMAC(secret, body) == received_hmac`; `shop` is unconstrained by that check. Any party who has ever received one legitimate webhook (e.g., the operator of their own installed shop, who legitimately receives webhooks with a correct HMAC for their own shop's body/topic) can re-send that exact `(body, hmac-sha256)` pair to the app's webhook endpoint while substituting a different `shop-domain` header (and optionally a different `topic`/`webhook-id`, also unsigned) naming a victim shop. `Registry.process` will validate the HMAC successfully (since it never depended on the header) and will invoke the handler with `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding break: the field the application acts on (`shop`, and also `topic`/`webhook-id`) is not covered by the HMAC that is supposed to authenticate the entire webhook. An attacker with only their own shop's install (an unprivileged actor relative to other merchants) can make the host application process attacker-chosen body content under a victim shop's identity, e.g. to fake `app/uninstalled`, `orders/create`, `customers/data_request`, or other topic-specific business logic being attributed to a shop they do not own. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up per-shop state, trigger emails, void data, or mark app status), this can lead to state corruption or actions performed against another tenant, which matches the "cross-tenant access" class of impact.

### Likelihood Explanation
Likelihood is moderate to high for any app that has multiple installs and logs/stores its own outbound-received webhook payloads (e.g., in job queues, logs, replay/retry infrastructure, or is simply able to capture packets for its own shop). No secret material is required: the attacker only needs a legitimately-signed webhook that Shopify already sent for their own store, which they can then relay with a spoofed header field. No TLS interception, credential leakage, or access token is needed, satisfying the "unprivileged internet user" constraint.

### Recommendation
Include the identity-relevant headers (at minimum `shop-domain`, and ideally `topic`/`webhook-id`) in the signed material used by `to_signable_string`, or otherwise cryptographically bind the shop to the payload before trusting `request.shop` in `Registry.process`. If Shopify's wire format does not allow changing what is HMAC-signed (since Shopify controls the signature), the library should, at minimum, document this limitation clearly and/or provide a way for consuming apps to further pin/verify the shop against their own trusted registration data rather than presenting `request.shop` as implicitly authenticated.

### Proof of Concept
1. Attacker installs the target app on their own shop, `attacker.myshopify.com`, and legitimately receives a webhook: body `B`, header `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends a request to the app's webhook endpoint with the same body `B` and same header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` [5](#0-4)  — validation passes.
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com", body: B ...)` [6](#0-5) , causing the host app to process attacker-controlled data as if it came from `victim.myshopify.com`.

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
