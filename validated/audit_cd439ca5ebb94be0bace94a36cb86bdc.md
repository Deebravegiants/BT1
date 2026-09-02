### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` value used to attribute the webhook to a tenant is read from an unauthenticated HTTP header. `Registry.process` validates the HMAC and then blindly forwards this unauthenticated header value to the host application's handler as the tenant identifier. This breaks the identity binding: `hmac_verified_bytes (raw_body) != shop_used_for_tenant_attribution (header)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` (the body) using the app's shared `Context.api_secret_key` — the same secret is valid for every shop that has this single app installed: [3](#0-2) 

`Registry.process` validates the HMAC over the body, and then constructs `WebhookMetadata` using `request.shop` — the unauthenticated header value — and hands it to the host app's handler as the trusted tenant identity: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no cryptographic binding to the verified payload: [5](#0-4) 

Because the same `api_secret_key` (the app's `client_secret`) is used to sign webhooks for every shop that installs the app, a valid `(raw_body, hmac)` pair generated for one shop remains cryptographically valid when replayed against the same endpoint with the `shop-domain` header swapped to a different shop string. The gem's HMAC check will pass (it only checks body integrity/authenticity against the shared secret) while the shop attribution used downstream for tenant routing is attacker-controlled.

### Impact Explanation
Any host application that relies on `WebhookMetadata.shop` (as returned by this gem) to select the tenant/session/store record to update — the intended and documented usage pattern — can be made to attribute a legitimately-signed webhook payload to an arbitrary shop domain string chosen by the attacker. An unprivileged party who has the app installed on any shop they control can capture a real signed webhook (body + hmac) that Shopify sent to the endpoint, then resend that exact body/hmac pair with a forged `x-shopify-shop-domain` header pointing at a victim shop. The gem reports the request as valid and forwards the forged shop identity to the handler, producing cross-tenant data confusion/misattribution without needing the `client_secret`, an access token, or any privileged access — satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is realistic but conditioned on the host application trusting `WebhookMetadata.shop` for record lookups without independently cross-checking the domain against the actual triggering install (a very common pattern, since this is exactly the field the gem exposes for that purpose). The attacker needs only their own installation of the target app (any real Shopify store, including a free development store) to generate one legitimately-signed webhook, then can replay the body/hmac with an altered shop header at will since nothing in the gem's own verification path binds the two together.

### Recommendation
Include the shop domain (and topic/webhook id, where applicable) in the HMAC-signed content, or otherwise cryptographically bind them, e.g. verify against a per-shop secret or include the header values in `to_signable_string`. At minimum, document that `Registry.process`/`WebhookMetadata.shop` is unauthenticated and must be revalidated by the host application against a shop-scoped access token/session it independently trusts before being used for tenant lookups; alternately, have `Registry.process` cross-check `request.shop` against a value obtained through an authenticated channel (e.g., the shop tied to the currently active session) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Shopify sends a legitimately signed webhook to the app's endpoint: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the shared `api_secret_key`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same request but rewrites the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` runs `Utils::HmacValidator.validate(request)` — this only checks `H` against `B`, which is unchanged, so validation succeeds: [6](#0-5) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)` even though `victim-shop` never sent this data, demonstrating the unbound identity field.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
