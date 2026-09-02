### Title
Webhook shop identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, but the `shop` identity that is subsequently handed to the app's handler is read from an unauthenticated HTTP header and is never included in the signed payload. This breaks the binding `hmac_verified_bytes == identity_bytes_trusted`, letting a party who can obtain one validly-signed webhook body (e.g., for their own installed shop) replay it while forging the `X-Shopify-Shop-Domain` header to make the app process the event as if it came from a different (victim) merchant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is sourced purely from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of the signed string at all: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes and compares the signature purely over `to_signable_string`, i.e., over the body bytes, with no involvement of the shop header: [4](#0-3) 

The identity binding that should hold is: *the shop attributed to a verified webhook event* == *the shop whose data actually produced the signed bytes*. Because the shop header is excluded from the HMAC-signable string, this equality is not enforced by the gem. Any party who can capture one validly-signed webhook payload delivered by Shopify to their own app installation (for their own shop, which they legitimately control) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` will still return `true` (the body/HMAC pair is untouched and genuinely signed with `Context.api_secret_key`), and `Registry.process` will hand the handler a `WebhookMetadata` object whose `shop` field names a shop the attacker does not control.

### Impact Explanation
This is a cross-tenant identity-binding bypass reachable by an unprivileged actor who merely operates their own instance of the merchant's shop (no leaked credentials, access tokens, or `client_secret` required — they only need a body that was once legitimately HMAC-signed for their own tenant). If the host app uses `WebhookMetadata#shop` to key persisted data (as the gem's design implies, since it is the only per-tenant identity exposed by webhook processing), the attacker can cause the app to write, delete, or otherwise process data under a victim shop's identity that they never actually own or install the app on — a cross-tenant access/integrity violation, matching the Critical severity bar ("cross-tenant access").

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker needs at least one genuine signed webhook body (trivially obtainable by installing the app on their own store and triggering any webhook-eligible event) and the ability to send an HTTP request to the app's public webhook endpoint with a custom header — both of which are available to any unprivileged internet user with a Shopify Partner/dev store account, no special access needed.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is cryptographically verified, e.g., by having `Request#to_signable_string` incorporate the shop-domain header (or, at minimum, have `Registry.process`/`HmacValidator` explicitly cross-check that the header-derived shop matches an expected/registered shop for the given HMAC before constructing `WebhookMetadata`). At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant-scoping without separate verification.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers a webhook event; Shopify POSTs a body `B` with header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's `api_secret_key`) and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures `B` and `H`.
3. Attacker sends `POST /webhooks` to the app with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), and `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` calls `validate_signature`, which recomputes the signature over `request.to_signable_string == B` and compares to `H` — it matches because header changes are irrelevant to the signed string: [5](#0-4) 
5. `Registry.process` proceeds and calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, even though the payload actually originated from the attacker's own shop: [6](#0-5)

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
