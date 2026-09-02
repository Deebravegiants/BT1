## Title
Webhook `shop` (and `topic`/`webhook-id`) identity is taken from unauthenticated headers while the HMAC only covers the raw body, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, never binding the `shop-domain`, `topic`, or `webhook-id` headers to the signature. `Registry.process` validates the body's HMAC and then trusts the unauthenticated `shop` header verbatim when dispatching to the merchant's webhook handler. This breaks the intended identity binding: **shop authenticated by the signature ≠ shop the handler is told to act on**.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `shop` is read straight out of an unauthenticated header with no cryptographic tie to the HMAC: [2](#0-1) 

`HmacValidator.validate` signs/compares exactly that `to_signable_string` value (i.e., only the body): [3](#0-2) 

`Registry.process` validates the HMAC and then forwards `request.shop` — the unauthenticated header value — directly to the app's webhook handler as the tenant identity, with no check that the signed body "belongs" to that shop: [4](#0-3) 

Because the signature is computed over the body alone, **any valid `(body, hmac)` pair obtained from a legitimately-signed webhook delivery (e.g., triggered on a shop the attacker controls/owns, where the app is installed) remains valid when replayed with a different `shopify-shop-domain` header**. The gem has no mechanism to detect this substitution — it will report `Utils::HmacValidator.validate(request)` as `true` and hand the handler a `WebhookMetadata` claiming a different shop than the one that actually produced the signed body.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged actor who merely has one legitimately signed webhook payload (obtainable by installing the app on a shop they control and capturing any webhook delivery) can forge the shop identity presented to the app's webhook handler for every subsequent replay of that body. Any host application that uses `WebhookMetadata#shop` (as documented/intended) to select which merchant's record to update, delete, or act upon will act on the wrong tenant's data — data corruption or cross-tenant access is the direct effect of trusting an HMAC-unbound field for tenant identification.

### Likelihood Explanation
Likelihood is limited by needing at least one legitimately signed webhook body first (trivial for anyone able to install a free/dev version of the app on their own store) and by the small number of body shapes/topics the attacker fully controls the effect of (they can only replay a body they already have signed, not an arbitrary body). Still, replay requires no secrets, no privileged account, and no interaction with `api_secret_key`, satisfying the unprivileged-internet-user bar.

### Recommendation
Bind the tenant identity into the signed material, or otherwise cryptographically tie `shop`/`topic`/`webhook-id` to the signature validation step — e.g., include the `shopify-shop-domain` (and other identifying headers) in `to_signable_string`, or independently verify that the shop asserted by the caller matches the shop for which the delivery was actually generated (for example, cross-checking against Shopify's webhook delivery metadata) before dispatching to the handler.

### Proof of Concept
1. Install the app (or otherwise operate it) on `attacker-shop.myshopify.com`; capture one legitimate webhook delivery, i.e. `(raw_body, X-Shopify-Hmac-Sha256)` for a topic the attacker cares about (e.g., `orders/create`).
2. Replay that exact `raw_body` and `hmac-sha256` value to the app's webhook endpoint, but set `shopify-shop-domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` — this passes because it only checks the raw body against the secret, which is unchanged.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` — the app now believes attacker-controlled data belongs to `victim-shop`, corrupting or leaking data across tenants depending on how the host app uses the `shop` field.

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
