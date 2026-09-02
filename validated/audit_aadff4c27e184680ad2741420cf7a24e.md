## Finding [1](#0-0) 

### Title
Webhook `shop`/`topic`/`webhook_id` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `x-shopify-shop-domain` (and `topic`/`webhook-id`/`api-version`) headers to build the `WebhookMetadata` object passed to the app's handler. Because the same `api_secret_key` (the app's client secret) is shared across every merchant that installs the app, any merchant can generate a genuinely-signed `(raw_body, hmac)` pair for their own shop and replay it with a forged `shop` header pointing at a victim shop.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`. For webhooks, that is defined as just the raw body: [2](#0-1) 

None of `shop`, `topic`, `webhook_id`, or `api_version` — all sourced from headers — are part of the signed material: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then forwards the unauthenticated `request.shop` (and `topic`/`webhook_id`/`api_version`) straight to the handler: [4](#0-3) 

The identity binding that should hold is: `shop that was actually charged/verified by Shopify == shop the handler attributes the payload to`. Because the `shop` header is not part of the HMAC-signed bytes, this equality is not enforced by the gem — verified bytes (body) ≠ bytes used for tenant attribution (header `shop`).

### Impact Explanation
Since `api_secret_key` is one shared secret for the whole app (not per-merchant), an attacker who is a legitimate, unprivileged merchant of the app can:
1. Install the app on their own shop (`attacker-shop.myshopify.com`) and receive a genuine webhook, e.g. `orders/create`, with body `B` and a valid `hmac(B, api_secret_key)`.
2. Replay that exact `(B, hmac)` pair to the app's webhook endpoint, but swap the `x-shopify-shop-domain` header to `victim-shop.myshopify.com` (and optionally the topic).
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `hmac`, both of which are unchanged and valid.
4. `Registry.process` builds `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: B, ...)` and invokes the app's handler as if the data belongs to the victim shop.

Any host application that uses `data.shop` from `WebhookMetadata` to select which merchant's records to update (a standard and encouraged usage pattern) will apply attacker-supplied data to a different tenant's account — a cross-tenant data injection/corruption primitive rooted entirely in this gem's webhook verification logic.

### Likelihood Explanation
Requires only: (a) the attacker be a normal (unprivileged) merchant who has installed the target app — no access to `api_secret_key`, access tokens, or TLS interception — and (b) the ability to POST directly to the app's public webhook endpoint. Both conditions are trivially satisfiable by anyone who installs the app on their own store and calls the webhook URL directly, since the endpoint is designed to be internet-reachable.

### Recommendation
Bind the identity headers into the signed material, or otherwise cryptographically verify that `shop`, `topic`, and `webhook_id` correspond to a session/registration the app actually owns, rather than trusting the header verbatim. At minimum, document and enforce that `WebhookMetadata#shop` must never be used to select a shop's session/access token without a secondary check (e.g., cross-referencing against the app's own registered shop list from an authenticated source), and/or fold the headers into the HMAC computation before validation.

### Proof of Concept
```ruby
# 1. Attacker installs the app on attacker-shop.myshopify.com and receives a real webhook.
raw_body = '{"id": 123, "note": "hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# 2. Attacker replays the same (body, hmac) pair but swaps the shop-domain header.
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by hmac
  "x-shopify-webhook-id" => "attacker-chosen-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds (only raw_body is checked),
# and the handler receives WebhookMetadata with shop: "victim-shop.myshopify.com".
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-43)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class Request
      extend T::Sig
      include Utils::VerifiableQuery

      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
