### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` values are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates nothing but the body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` values that `Registry.process` extracts from HTTP headers and forwards to the app's handler as trusted `WebhookMetadata` are never part of the signed content.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

which returns only `@raw_body`. Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then trusts these header-derived values to build the `WebhookMetadata` object that is handed to the app's registered handler for that topic: [3](#0-2) 

`WebhookMetadata` treats `shop`, `topic`, `webhook_id`, and `api_version` as trusted struct fields consumed by host-app handler logic (e.g., tenant lookup, per-topic business logic): [4](#0-3) 

The identity binding that should hold is:
`HMAC(client_secret, raw_body) == received_hmac` AND `(shop, topic, webhook_id) are cryptographically bound to that same HMAC`.

In this implementation only the first half holds. `HmacValidator.validate` recomputes `HMAC(client_secret, verifiable_query.to_signable_string)` and compares to the received signature: [5](#0-4) 

Because `client_secret` is shared across every shop that has installed the app (it is not per-shop), any webhook body + HMAC pair that is valid for one shop's webhook delivery remains a mathematically valid pair for the *same secret* regardless of which `shop-domain`/`topic`/`webhook-id` header accompanies it. An attacker who can install the app themselves (an ordinary/unprivileged merchant, i.e., "unprivileged internet user" relative to other tenants of the same app) receives real webhook deliveries with valid `(body, hmac)` pairs to their own endpoint. They can replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim shop) and/or `shopify-topic` header. `Utils::HmacValidator.validate` will still return `true` because it only checks the body, and `Registry.process` will route/execute the victim-shop-labeled handler using this forged identity, e.g. an `orders/create` payload replayed under an `app/uninstalled` topic, or a payload attributed to a different shop than the one that actually sent it.

### Impact Explanation
This breaks the identity binding between the cryptographically-verified content (raw body) and the routing/identity fields (`shop`, `topic`, `webhook_id`) that host applications rely on via `WebhookMetadata` to determine which tenant and which business logic to execute. This enables cross-tenant confusion: an app built on this gem that uses `WebhookMetadata#shop` to look up per-shop state (a very common pattern, and the documented purpose of this field) can be made to act on a request labeled with a shop it did not originate from, or under a topic that does not match the actual payload's provenance. This matches the in-scope "cross-tenant access" impact category, since the merchant sending the replay does not need any secret, access token, or privileged account — only a webhook body/HMAC pair captured from their own legitimate installation.

### Likelihood Explanation
Likelihood is meaningful but requires the attacker to already run the app on at least one shop of their own (any developer/merchant can install a public app), so they can legitimately capture one valid `(raw_body, hmac)` pair from a live webhook delivery. From there, replaying with modified `shop-domain`/`topic` headers is trivial (a single crafted HTTP POST) since nothing in this gem's `HmacValidator`/`Registry` binds those header values to the signature.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified content, or otherwise cryptographically bind them to the payload before trusting them in `WebhookMetadata`. At minimum, document that host apps must not treat webhook `shop`/`topic`/`webhook_id` values as trusted independent of an out-of-band, per-shop verification (e.g., confirming the shop is a known, installed tenant and that the topic/webhook_id pairing is consistent with what was registered), since the current HMAC only vouches for body integrity, not for the header-derived routing identity.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` (unprivileged, self-service install).
2. A legitimate webhook fires to the app's public webhook endpoint with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)` — attacker observes this pair via their own endpoint/logs.
3. Attacker crafts a new POST to the same public webhook endpoint, reusing body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: <different topic>`.
4. `ShopifyAPI::Utils::HmacValidator.validate` (via `Request#to_signable_string` returning only `@raw_body`) recomputes the same `HMAC-SHA256(client_secret, B)` and it matches `H`, so validation succeeds: [3](#0-2) 
5. `Registry.process` dispatches to the handler registered for the attacker-chosen topic with `WebhookMetadata#shop == "victim-shop.myshopify.com"`, even though that shop never sent this webhook — the host application's handler (looking up tenant state by `data.shop`) now acts under a forged tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
