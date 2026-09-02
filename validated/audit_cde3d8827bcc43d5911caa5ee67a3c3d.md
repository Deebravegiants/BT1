### Title
Webhook `shop` (and `topic`/`webhook-id`) attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while the `shop` (and `topic`/`webhook_id`) values consumed by the app are read from HTTP headers that are excluded from that signature. `Registry.process` validates the HMAC and then hands the header-derived, unauthenticated `shop` value straight to the app's `WebhookHandler` as the tenant identity, breaking the binding between "bytes verified" and "shop acted on."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  and the HMAC is computed with `OpenSSL::HMAC.hexdigest(..., secret, signable_string)` in `Utils::HmacValidator.compute_signature`, which is exactly the body-only string for webhooks: [2](#0-1) .

However, `Request#shop`, `#topic`, and `#webhook_id` are all read directly from HTTP headers, not from the signed body: [3](#0-2) .

`Registry.process` validates only the HMAC of the request, then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) . The `WebhookMetadata` struct exposes `shop` as a first-class trusted field for the handler to act on (e.g., to select or scope tenant-specific data): [5](#0-4) .

The broken identity binding, stated as an equality that should hold but doesn't:
`shop authenticated by HMAC` ≠ `shop the handler acts on`.

Concretely: Shopify signs `HMAC(secret, raw_body)` and delivers it with headers `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, `X-Shopify-Webhook-Id` that are **not** part of the signed material. A user who legitimately receives (or, being an unprivileged internet user, can otherwise obtain/replay) a validly-signed webhook body for one shop/topic can resend that exact body to the app's webhook endpoint with a different `X-Shopify-Shop-Domain` (or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header. `Utils::HmacValidator.validate` still returns `true` because it only checks the raw body bytes, and `Registry.process` will dispatch the (attacker-chosen) `shop`/`topic` to the handler as if authenticated, since nothing re-derives or cross-checks these header values against the signed payload.

### Impact Explanation
This satisfies the "Cross-tenant access" impact category: the app's webhook handler operates on data believed to belong to `request.shop`, but that value carries no cryptographic binding to the HMAC that supposedly authenticates the whole request. An attacker can cause the host application to process/attribute genuine Shopify webhook payloads (e.g. `shop/redact`, `customers/data_request`, `orders/*`) under an arbitrary spoofed shop domain, topic, or webhook id, since the library provides no protection for these fields despite them being the primary identity/routing information passed to `WebhookHandler#handle`.

### Likelihood Explanation
Exploitation requires an attacker to possess at least one validly-signed webhook body (obtainable from their own store's genuine webhook deliveries, which every merchant/developer legitimately receives) and the ability to POST to the target app's public webhook endpoint with modified headers — both are within reach of an unprivileged internet user and require no access token, `api_secret_key`, or privileged account.

### Recommendation
Include the identity-critical headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise require the host application to authenticate the shop domain against a value derived from the signed payload/known valid tenant list before dispatching to `WebhookHandler`. At minimum, document that `request.shop`/`topic`/`webhook_id` are unauthenticated header values and must not be trusted for tenant-sensitive dispatch without additional verification in `Registry.process`.

### Proof of Concept
```ruby
# Attacker captures a legitimate, validly-HMAC-signed webhook body from their own store
raw_body = '{"id":123,"email":"victim-app-sees-this@example.com"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)

# Attacker replays it against the target app's webhook endpoint, spoofing the shop header
headers = {
  "x-shopify-topic" => "customers/data_request",       # attacker-chosen, unsigned
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac), # signs only raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-chosen, unsigned
  "x-shopify-webhook-id" => "spoofed-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (body matches),
#    handler.handle receives WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "customers/data_request", ...)
#    even though none of shop/topic/webhook_id were covered by the HMAC.
``` [6](#0-5) [4](#0-3) [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-40)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
