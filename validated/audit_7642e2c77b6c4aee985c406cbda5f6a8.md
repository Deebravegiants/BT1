### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body [1](#0-0) , then dispatches to the handler using the `shop` value read from the `X-Shopify-Shop-Domain` header, which is never part of the signed material [2](#0-1) . The tenant identity (`shop`) used by application code is therefore unauthenticated relative to the cryptographic check that is supposed to prove the request is legitimate.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against the `hmac` field [3](#0-2) . For webhooks, `Request#to_signable_string` returns only `@raw_body` [4](#0-3) , while `Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no cryptographic tie to the HMAC [2](#0-1) .

`Registry.process` uses exactly this unauthenticated `shop` value to build the `WebhookMetadata` passed to the app's handler:
```
raise Errors::InvalidWebhookError, ... unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [5](#0-4) 

The equality the gem implicitly promises is: `hmac_valid(body) == true` implies `shop == the tenant that owns this body`. In reality the check only proves `HMAC(secret, body)` matches — it says nothing about which shop the header claims. Any party who can obtain one genuine `(body, hmac)` pair signed with the app's shared secret (e.g., by installing/using the app on their own store and capturing a webhook delivery to a logging proxy, browser dev tools on a locally forwarded tunnel, or any request-inspection tooling around the webhook endpoint) can replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary value in `X-Shopify-Shop-Domain`. `HmacValidator.validate` will still return `true` (it never inspects the shop header), and the handler will be invoked believing the payload originated from the spoofed shop.

### Impact Explanation
This breaks the identity binding `authenticated_bytes (body+hmac) == claimed_tenant (shop header)` and lets an unprivileged user who has ever received one legitimate webhook from their own store to make the app process fabricated (shop, body) pairs for a shop of their choosing (e.g., `victim-shop.myshopify.com`). Any app whose webhook handler trusts `shop` for tenant-scoped side effects (writing to per-shop tables, triggering per-shop billing/inventory/customer-redaction actions such as the `customers/redact`/`shop/redact` mandatory topics) will act cross-tenant on behalf of an attacker-chosen shop identifier. This matches the Critical "cross-tenant access" category defined for this exercise.

### Likelihood Explanation
Medium-to-high for apps that log raw webhook requests, use debugging proxies, or run tunnelling tools during development/production against the shared webhook endpoint: the attacker only needs one authentic `(body, hmac)` sample from their own store (which they legitimately control) and the ability to send an arbitrary HTTP request to the app's public webhook endpoint with a modified header — no access to `api_secret_key` or any privileged credential is required, only ordinary knowledge of the app's public webhook URL and one legitimately-received webhook of their own.

### Recommendation
Bind the shop identity into the authenticated material rather than trusting an unauthenticated header:
- Cross-check `request.shop` against the shop already associated with the webhook subscription/session stored in the app's own state before invoking the handler, rather than trusting the header value as-is.
- Where possible, extend `to_signable_string` verification context (or add an explicit post-HMAC step) so the `shop-domain` header is confirmed to match a shop that is expected/registered by the app for that specific webhook `topic`/`webhook_id`, closing the gap between "cryptographically valid body" and "claimed tenant."
- Document clearly to consumers of `WebhookMetadata` that `shop` is not covered by the HMAC and must be independently validated by the host application before being used for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers a webhook subscription (e.g., `orders/create`).
2. Attacker triggers an event and captures the resulting legitimate delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify using the app's real `api_secret_key`), plus `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays an HTTP POST to the app's public webhook endpoint with the same body `B` and the same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, B)` and finds it equals `H` → returns `true` [3](#0-2) .
5. `Registry.process` proceeds and calls `handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))` [5](#0-4) , causing the app to act as if the (attacker-controlled) payload came from `victim-shop.myshopify.com`.

### Citations

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
