## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (tenant identity), `topic`, `webhook-id`, and `api-version` values are read directly from HTTP headers and never included in the signed material. `ShopifyAPI::Webhooks::Registry.process` validates only that the raw body's HMAC is correct, then hands the unauthenticated `shop` header straight to the app's handler as the tenant identifier.

## Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight off an attacker-controllable header with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the HMAC of the body, then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler as the tenant context: [3](#0-2) 

The identity binding the gem should enforce is: `shop attributed to this HMAC == shop that produced this body`. Because `HmacValidator.validate` only checks `computed_signature(raw_body, secret) == received_signature`, the equality actually enforced is just `body == body`, with `shop` free to be anything the attacker sets in the header while the signature stays valid.

Any Shopify merchant who installs the app (an "unprivileged internet user" relative to other tenants) legitimately receives real webhooks from Shopify addressed to their own shop, each with a valid `x-shopify-hmac-sha256` computed from the app's real `client_secret`. That attacker-merchant can capture one such request (`raw_body` + valid `hmac`) and replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and `x-shopify-topic`/`webhook-id`) header for a different, victim shop. `HmacValidator.validate` still succeeds because it only checks the body against the secret, and `Registry.process` dispatches the handler with `shop: request.shop` set to the attacker-chosen victim domain, along with the topic and webhook id.

## Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook authenticity: an app relying on `WebhookMetadata#shop` to route data ("save this payload for `data.shop`") can be made to attribute one tenant's webhook payload to another tenant, or to replay a shop's own webhook to itself repeatedly (or under different topics if the body happens to be topic-agnostic), corrupting per-shop data linkage. This falls under cross-tenant access/data confusion since the identity used for authorization/storage decisions downstream is not the identity the request is really from.

## Likelihood Explanation
Likelihood requires only: (1) attacker access to at least one legitimate webhook (trivial — any shop owner installing the app receives these), and (2) the ability to POST arbitrary headers/body to the app's public webhook endpoint (also trivial, no auth required to reach it). No secret, TLS interception, or privileged access is needed — only capturing one legitimate, previously-delivered webhook.

## Recommendation
Include `shop`, `topic`, and `webhook_id`/`api_version` in the signable material verified against the HMAC (or otherwise cryptographically bind them, e.g., by having the gem verify the shop belongs to a known/registered session before dispatch), rather than trusting header values that sit outside the HMAC-protected body.

## Proof of Concept
```ruby
# Attacker (a legitimate merchant on ShopA) captures a real webhook Shopify sent them:
raw_body = '{"id":123,"note":"legit ShopA order"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), APP_SECRET, raw_body) # computed by Shopify, valid

captured_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "shop-a.myshopify.com",
}

# Attacker replays it, only swapping the shop-domain header:
forged_headers = captured_headers.merge("x-shopify-shop-domain" => "shop-b.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HMAC validation passes (body unchanged); handler receives
#    WebhookMetadata(shop: "shop-b.myshopify.com", body: ...) even though
#    the payload actually originated from shop-a, and shop-b never sent it.
``` [3](#0-2) [4](#0-3)

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
