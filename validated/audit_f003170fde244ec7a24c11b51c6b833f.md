### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw HTTP body, while the `shop` identity used downstream by `Registry.process` is read from an HTTP header that is completely outside the signed payload. This breaks the intended binding "shop authenticated == shop attributed to the webhook event," analogous to the reported bug class where a field acted upon (the unlock date) was not actually protected by the check that was supposed to cover it (the safe addition/overflow guard).

### Finding Description
`Utils::HmacValidator.validate` signs/verifies only whatever `to_signable_string` returns for a `VerifiableQuery`. For webhooks, `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

The `shop` attribute used to attribute the webhook event to a tenant is derived from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, not from any HMAC-covered field: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then trusts `request.shop` (the unauthenticated header) when building the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The `VerifiableQuery` interface only requires `hmac` and `to_signable_string`, so nothing in the abstraction enforces that every field consumed by the caller be part of the signed string: [4](#0-3) 

Equality being asserted (as in the report's overflow example) is: `shop attributed to event == shop that was HMAC-authenticated`. Here that equality does not hold — the HMAC authenticates only the body bytes, not the shop identity, so any request with a valid `(body, hmac)` pair can carry an arbitrary `shop-domain` header and still pass `Utils::HmacValidator.validate`.

### Impact Explanation
Because `api_secret_key` is shared across all shops/tenants that install the same app, a merchant that has legitimately installed the app (or anyone who can capture one valid `(raw_body, hmac)` pair emitted by Shopify for any shop using this app) can present that same body+HMAC to the app's webhook endpoint while altering the `shopify-shop-domain` header to name a different, victim shop. `Registry.process` will pass HMAC validation and route the payload to the handler tagged with the attacker-chosen `shop`, causing the host application to process/store data under the wrong tenant. This is a cross-tenant identity-binding break reachable by any user with the ability to send HTTP requests to the app's public webhook endpoint (given knowledge of one legitimate body/HMAC pair), matching the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Exploitation requires only (a) the ability to send a raw POST to the app's webhook route with attacker-controlled headers, and (b) one previously observed valid `(raw_body, hmac)` pair from Shopify (trivially obtainable by any merchant with the app installed, since the merchant can trigger their own store's webhooks and capture them). No access token, `client_secret`, or privileged credentials are needed. Likelihood is high for apps that key any behavior (data isolation, authorization, side effects) off the webhook `shop` value.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) as part of the HMAC-signed content, or otherwise cryptographically bind the `shop` header to the payload before trusting it. At minimum, `Request#to_signable_string` should not be the sole basis for identity — the library should require the host application to cross-check `request.shop` against a shop it independently expects (e.g., a shop with an active/known session), and document that the `shop-domain` header is unauthenticated by the HMAC.

### Proof of Concept
```ruby
# Attacker legitimately installs the app on "attacker-shop.myshopify.com"
# and captures one real webhook delivery (raw_body, valid hmac) from Shopify,
# e.g. for the products/update topic.

raw_body = '{"id":123,"title":"legit-captured-body"}'
valid_hmac_base64 = "<captured from the real Shopify webhook delivery>"

headers = {
  "x-shopify-topic" => "products/update",
  "x-shopify-hmac-sha256" => valid_hmac_base64,   # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged — not covered by HMAC
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# Passes because HmacValidator only checks raw_body against the secret,
# and request.shop is read straight from the (forged) header.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```

Note: I was not able to fully verify how downstream host applications (e.g. `shopify_app`) additionally cross-check the webhook `shop` against known installed shops before trusting it; that cross-check, if present in a wrapping application, could reduce real-world exploitability. Within this gem's own code (`lib/shopify_api/webhooks/**`), no such binding exists.

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L1-17)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Utils
    module VerifiableQuery
      extend T::Sig
      extend T::Helpers
      interface!

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
    end
  end
```
