Found a valid analog. The bug-class match: like `ClearingHouse._execute()` acting on stale/unbound state, here `ShopifyAPI::Webhooks::Request` computes its HMAC over `@raw_body` only, while the `shop` (and `topic`/`api_version`/`webhook_id`) fields that the webhook handler actually acts on are read straight from unauthenticated HTTP headers that are never included in the signed bytes.### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-shop webhook spoofing via HMAC replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` only proves the integrity of the JSON body. The `shop` field (along with `topic`, `api_version`, `webhook_id`) is read directly from unauthenticated HTTP headers and is never part of the signed bytes, yet `Registry.process` trusts `request.shop` as the tenant identity passed to the app's webhook handler.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` supplied by the caller [1](#0-0) . For `Webhooks::Request`, `to_signable_string` is defined as simply `@raw_body` [2](#0-1) , meaning the HMAC binds only the request body — never the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers.

However, `shop`, `topic`, `api_version`, and `webhook_id` are all derived purely from headers with no cryptographic binding to the signature: `shop` reads `shopify_header("shop-domain")` [3](#0-2) .

`Registry.process` validates the HMAC over the body only, then immediately trusts `request.shop` (and `request.topic`) to route to a handler and construct `WebhookMetadata` used by the host application to attribute the event to a tenant: [4](#0-3) .

The identity binding that should hold is: `shop_header == shop_bound_by_hmac`. Instead, the gem only guarantees `body == body_bound_by_hmac`; `shop_header` is fully attacker-controlled and independent of the signature.

### Impact Explanation
Because the app's `client_secret`/`api_secret_key` is shared across **all shops** that install the app, and Shopify computes the HMAC using that single shared secret for every tenant's webhook deliveries, any shop that has installed the app can observe a legitimately-signed `(raw_body, hmac)` pair delivered to its own webhook endpoint. Since the `shop-domain` header is not covered by the signature, that same `(raw_body, hmac)` pair remains valid when replayed to the exact same public webhook endpoint with the `shop-domain` header changed to a different, victim shop's domain. `Utils::HmacValidator.validate` will still return `true` (body untouched), and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` field is the attacker-chosen victim domain, alongside a `topic`/`body` that the attacker fully controls the pairing of. This lets an unprivileged attacker (any merchant with an install of the target app) inject fabricated webhook events cross-tenant, misattributed to a shop they do not own — a cross-tenant integrity/confusion issue for any app relying on `request.shop` from this gem to authorize or scope side effects (e.g. `app/uninstalled`, order or customer webhooks that trigger data writes/deletes keyed by `shop`).

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint and possession of one legitimately-signed webhook body from the attacker's own (or any) shop — both of which are available to any ordinary, unprivileged installer of the app, with no access to `api_secret_key` needed. The library performs no additional binding of `shop` to the signed payload, so the check always passes as long as the body is unmodified.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable string used for HMAC verification, or otherwise cryptographically bind `shop` to the signature (e.g., derive/verify it via a separate trusted channel such as re-fetching shop context from a previously-established session) rather than trusting the raw header value once body-only HMAC validation succeeds.

### Proof of Concept
1. App `X` is installed on attacker's shop `attacker.myshopify.com` and victim's shop `victim.myshopify.com`, both delivering webhooks to `https://app-x.example.com/webhooks`.
2. Attacker receives (or triggers) a legitimate webhook to their own endpoint instance: `raw_body = B`, header `x-shopify-hmac-sha256 = H` (valid because Shopify signed `B` with the shared `api_secret_key`), and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker replays the exact same POST to the app's webhook endpoint, keeping `raw_body = B` and `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) — still matches `H` [2](#0-1) .
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` [5](#0-4) , causing the host app to process an attacker-controlled webhook body as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
