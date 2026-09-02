Confirmed. The `shop` field passed to webhook handlers is sourced purely from the `x-shopify-shop-domain` header and is never included in the HMAC-signed material (`to_signable_string` returns only `@raw_body`).### Title
Webhook shop identity spoofing — `x-shopify-shop-domain` header is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop`, `topic`, `api_version`, and `webhook_id` values used by webhook handlers entirely from unauthenticated HTTP headers, while `ShopifyAPI::Utils::HmacValidator` only verifies the raw request body (`to_signable_string` returns `@raw_body`). This breaks the intended identity binding: `hmac_signed_bytes == bytes_the_handler_trusts_as_shop_identity`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers, none of which participate in the signature: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then trusts `request.shop` (and the other header-derived fields) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`WebhookMetadata` exposes `shop` as a plain `String` field with no additional integrity guarantee: [4](#0-3) 

Because Shopify webhook HMACs are computed with the app's single `client_secret` (`Context.api_secret_key`) shared across every shop that has installed the app — not a per-shop secret — any legitimate webhook body received by one installed shop produces a valid HMAC regardless of which shop's domain is claimed in the header: [5](#0-4) 

An attacker who operates their own store that has the target app installed will legitimately receive real, validly-signed webhook deliveries (body + valid HMAC) for their own shop. Since the HMAC only binds the body, the attacker can resend that exact same body with an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value naming a victim shop. `HmacValidator.validate` will still succeed because it recomputes the signature over `@raw_body` only, and the forged `shop` value flows unchecked into `WebhookMetadata#shop`, which the host application's handler uses to identify the tenant the event pertains to (e.g., to look up a session/store record and act on that shop's data).

This is the exact bug class described in the prompt: **"a field acted on but not covered by the HMAC."** The equality that should hold — `verified_bytes == bytes_used_for_shop_identity` — does not, because `verified_bytes = raw_body` while `bytes_used_for_shop_identity = header["shopify-shop-domain"]`.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` (as documented and demonstrated in this gem's own webhook usage docs) to select which tenant/session/store record to act upon, an attacker with any shop that has the app installed can forge webhook deliveries that appear to originate from a different, victim shop. This is a cross-tenant confusion vector, since a value normally used to select tenant-scoped data or trigger tenant-scoped side effects is attacker-controlled despite being delivered through a channel presented as "verified" (`Registry.process` only raises `InvalidWebhookError` when the HMAC check fails — implying everything else, including `shop`, is trustworthy). Depending on what the handler does with `shop` (e.g. writing data under the wrong shop, triggering GraphQL/REST calls using a mismatched session, or bypassing per-shop authorization checks based on webhook shop), this can lead to cross-tenant access to data/state, meeting the "Critical – cross-tenant access" bar defined in scope.

### Likelihood Explanation
Requires only that the attacker control one legitimate installation of the target app (freely obtainable, since Shopify apps are installable by any store owner) and be able to replay an HTTP POST with modified headers to the app's webhook endpoint — no privileged credentials, no `api_secret_key`, and no interception are needed. The captured raw body and HMAC from the attacker's own real webhook deliveries are all that's required; the header can trivially be swapped in the replayed request.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the value that is cryptographically verified, or otherwise cryptographically bind the header-derived `shop` to the signed payload before exposing it via `WebhookMetadata`. At minimum, the gem should not present `shop` on `WebhookMetadata` as if it were verified without documenting that host apps must independently confirm shop identity (e.g. by cross-checking against a known list of shops that registered that specific topic/webhook id, or by only trusting `shop` in combination with a stored per-shop webhook id returned at registration time in `Registry.register`).

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Attacker triggers a genuine event (e.g. `orders/create`) on their own shop, causing Shopify to deliver a webhook with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the identical body `B` and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `B`) and matches, since headers are not part of the signed content: [6](#0-5) 
5. `request.shop` returns `"victim-shop.myshopify.com"` (from the header), and this value is passed into `WebhookMetadata` and on to the host app's handler as the shop the event pertains to: [7](#0-6) 
6. Any handler logic keyed off `data.shop` now operates under the wrong tenant identity, chosen entirely by the attacker.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
