### Title
Webhook `shop` (and `topic`/`webhook-id`) identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC that `HmacValidator` checks binds *only* the payload bytes. The `shop` (and `topic`, `webhook-id`) values that `Registry.process` hands to the application's webhook handler come from unauthenticated HTTP headers that are completely outside the signed content.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

while `shop`, `topic`, and `webhook_id` are all pulled straight from request headers with no cryptographic tie to the body: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` only ever verifies `verifiable_query.to_signable_string` (i.e., the body) against the received `hmac`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust the whole `Request`, including its header-derived `shop`, and forwards that unauthenticated `shop` value straight into the handler's `WebhookMetadata`: [4](#0-3) 

This is the same bug class as the reported PSwapLib issue: an operation (`handler.handle`) is gated on a check (HMAC) that does not cover a field (`shop`) that the operation actually acts on. The binding that should hold is:

`shop asserted in header == shop actually covered by HMAC(secret, signed_content)`

but the implementation only guarantees `HMAC(secret, raw_body) == received_hmac`, with `shop` free to vary independently.

### Impact Explanation
Any user who can install the app on their own shop ("Shop A") is an unprivileged actor with respect to every other tenant of the app ("Shop B"). Shopify legitimately delivers Shop A webhooks with a body `B` and a valid `hmac = HMAC(secret, B)` (the secret is the app's shared `client_secret`, identical across all shops using this app — not something the attacker needs to know or leak). Because the signature covers only `B`, the attacker can replay that exact `(body=B, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with Shop B's domain. `HmacValidator.validate` still returns `true` (the body/hmac pair is untouched and valid), so `Registry.process` calls the handler with `WebhookMetadata#shop == "shop-b.myshopify.com"` even though the payload actually originated from Shop A. Any handler that keys per-tenant state, session lookup, or write actions off `WebhookMetadata#shop` (the documented and expected usage) will now execute Shop A's forged/attacker-controlled payload under Shop B's identity — a cross-tenant integrity violation reachable purely through this gem's own signature-verification and dispatch logic.

### Likelihood Explanation
No secrets, tokens, TLS interception, or privileged access are required — only the ability to install the app (an ordinary unprivileged tenant relationship) and knowledge of a target shop's domain (public information: `{shop}.myshopify.com`) to set as the spoofed header. This is a direct, low-effort exploit path entirely within code this gem owns (`Request`, `HmacValidator`, `Registry`).

### Recommendation
Bind the header-derived identity fields into the signed content that `HmacValidator` verifies (e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or require the host application to additionally verify `shop` against its own session/installation record before trusting `WebhookMetadata#shop`), and document clearly that `Registry.process`'s HMAC check does not, by itself, authenticate the `shop` header.

### Proof of Concept
1. App is installed on attacker's own shop `attacker.myshopify.com`. Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`, header `X-Shopify-Hmac-Sha256: HMAC(secret, B)`.
2. Attacker captures this request from their own traffic (no interception of anyone else's traffic needed).
3. Attacker resends the identical body `B` and identical valid `Hmac-Sha256` header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B)` against the unchanged body [5](#0-4) .
5. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` [6](#0-5) , causing the application to act on attacker-controlled data under the victim tenant's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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
