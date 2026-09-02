### Title
Webhook HMAC only covers the raw body, not the `shop`, `topic`, `webhook-id`, or `api-version` headers, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw body, so `HmacValidator.validate` only proves the *body bytes* were signed by Shopify — it proves nothing about which shop, topic, or webhook-id the signature was intended for. `Registry.process` nevertheless trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` taken straight from attacker-controllable HTTP headers, and hands them to the app's webhook handler as authenticated facts.

### Finding Description
`Utils::VerifiableQuery` requires only `hmac` and `to_signable_string`. For webhooks, `to_signable_string` is defined as just the raw body: [1](#0-0) 

The HMAC comparison in `HmacValidator.validate_signature` computes `HMAC(secret, to_signable_string)` and secure-compares it to the `hmac` header: [2](#0-1) 

So the cryptographic guarantee is: `HMAC(secret, raw_body) == received_hmac`. Nothing binds `shop-domain`, `topic`, `webhook-id`, or `api-version` into that computation — those are read directly from headers with no covering signature: [3](#0-2) 

`Registry.process` validates only the HMAC-over-body, then trusts `request.topic` and `request.shop` (unsigned headers) as the identity of the event source when dispatching to the app's handler: [4](#0-3) 

**Equality that should hold but doesn't:** `bytes verified by HMAC == bytes acted on by the handler`. In reality, `bytes verified = raw_body` while `bytes acted on = raw_body + shop + topic + webhook_id + api_version`. The extra fields are unauthenticated.

**Attack path (no privileged credential needed):**
1. An unprivileged attacker installs the target app on their own (attacker-owned, unprivileged) development/trial shop `attacker-shop.myshopify.com`.
2. The attacker triggers any webhook event on their own shop that the app has registered for (e.g., updates a resource), causing Shopify to send a legitimately signed webhook `POST` to the app's webhook endpoint: raw body `B`, `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: <topic>`.
3. The attacker captures this request (it's just their own outbound webhook, requires no special access) and replays it to the same endpoint, changing only the `x-shopify-shop-domain` header to a victim shop (`victim-shop.myshopify.com`) and/or the `x-shopify-topic` header to a different topic the app also handles.
4. `HmacValidator.validate` still passes, because the HMAC only ever covered `B`, and `B` is unchanged. `Registry.process` then invokes the app's handler with `shop: "victim-shop.myshopify.com"` and/or a forged `topic`, even though Shopify never sent this event for that shop/topic.

### Impact Explanation
This breaks the tenant-identity binding that `HmacValidator.validate` is supposed to provide: any app built on this gem which trusts `WebhookMetadata#shop` (e.g., to look up per-shop tokens/state, gate multi-tenant data writes, or key a cache/DB row) can be made to process attacker-supplied `body` content under an arbitrary victim shop's identity, or under an arbitrary handled topic. This is a cross-tenant access vector: the attacker never needs the victim's or the app's credentials, only the ability to trigger one webhook against their own shop and replay it with modified headers.

### Likelihood Explanation
High likelihood: any developer/attacker can freely create a Shopify development store and install the target app, generate at least one legitimately signed webhook, then trivially replay it with modified headers using any HTTP client — no secrets, tokens, or social engineering required.

### Recommendation
Bind the shop/topic/webhook identity into the signed material, or otherwise re-derive/cross-check it from a trusted source (not raw headers) before dispatch:
- Prefer validating shop identity via the GraphQL Admin API/webhook-id lookup (already used elsewhere in `Registry`) rather than trusting `x-shopify-shop-domain` verbatim, or
- Include `topic`, `shop-domain`, `webhook-id`, and `api-version` in `to_signable_string` so the HMAC actually covers everything the handler acts on, matching Shopify's documented webhook verification guidance.

### Proof of Concept
```ruby
# 1. Attacker triggers a real webhook on their own shop, e.g. via test/webhooks fixtures:
raw_body = "{}"
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Genuine headers Shopify sent for attacker's own shop:
genuine_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
}

# 2. Attacker replays same body+hmac but swaps shop-domain (and/or topic):
forged_headers = genuine_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) still returns true (only raw_body is signed),
#    handler.handle is invoked with shop: "victim-shop.myshopify.com"
``` [4](#0-3) [5](#0-4)

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
