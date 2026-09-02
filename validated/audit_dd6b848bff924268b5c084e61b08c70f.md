### Title
Webhook `shop` (and `topic`/`webhook-id`/`api-version`) identity fields are trusted from unauthenticated headers, while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute that identifies which merchant a webhook belongs to purely from the `x-shopify-shop-domain` (or `shopify-shop-domain`) HTTP header, but `Utils::HmacValidator.validate` only verifies the HMAC over the raw request body via `to_signable_string`. The `shop` field is never part of the signed payload, so the binding "HMAC-authenticated bytes == shop that the handler acts on" does not hold.

### Finding Description
`Registry.process` validates the webhook solely via:
```ruby
# lib/shopify_api/webhooks/registry.rb:189-199
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [1](#0-0) 

`HmacValidator.validate` computes and compares the HMAC only against `verifiable_query.to_signable_string`: [2](#0-1) 

And `Request#to_signable_string` returns only the raw body, while `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled straight from HTTP headers that are never hashed:
```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [3](#0-2) 

Because a single app's `api_secret_key` (`Context.api_secret_key`) is shared across every merchant/tenant that installs the app, an attacker who is themselves a legitimate merchant (an unprivileged internet user, requiring no special credential beyond installing the app on their own store) can:
1. Install the target app on their own shop, triggering a real webhook delivery with a body and correctly computed HMAC signed by the app's shared secret.
2. Capture that `(raw_body, hmac)` pair.
3. Replay the exact same body+HMAC directly to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain (and/or forge `x-shopify-topic`, `x-shopify-webhook-id`).

`HmacValidator.validate` will pass, because the HMAC only checks the (unmodified) body against the shared secret — it says nothing about which shop or topic the body belongs to. `Registry.process` then hands the handler a `WebhookMetadata` object whose `shop` is the attacker-forged value, not the shop that actually produced the signed body. This breaks the identity equality `hmac_verified_bytes == (body, shop)` down to `hmac_verified_bytes == body` only, letting an attacker impersonate an arbitrary shop identity for any webhook body they can legitimately obtain a signature for.

### Impact Explanation
This is a cross-tenant identity-binding bypass at the gem level: the library hands host applications a `shop` value that has no cryptographic relationship to the signed payload. Any host app that uses `WebhookMetadata#shop` to key persistence, trigger uninstall/GDPR flows (`shop/redact`, `customers/redact`, `customers/data_request` are exactly the mandatory topics this gem special-cases), or otherwise act "on behalf of" the named shop is exposed to forged webhooks purportedly from a victim tenant. This matches the Critical category "cross-tenant access" since the attacker crosses a tenant boundary using only their own legitimately obtained signature material — no access token, secret, or privileged account is needed.

### Likelihood Explanation
Likelihood is high for any host application that (a) installs the app across multiple merchants (normal SaaS model) and (b) trusts `WebhookMetadata#shop` for tenant-scoped side effects, which is the documented intended use of this API. The attack only requires the attacker to be a merchant who can install the app (any internet user with a Shopify dev/store account) and to send a raw HTTP POST with modified headers to the app's public webhook endpoint — no interception, no leaked secrets, and no host-app misuse of a documented API contract; the gem itself never authenticates the header fields it exposes as trusted identity.

### Recommendation
Bind the identity headers into the HMAC-verified signable string, or otherwise cryptographically or out-of-band verify that `shop`/`topic`/`webhook_id` correspond to the body that was actually signed (e.g., cross-check against Shopify's IP allowlist, or require the host app to correlate `shop` with a known, previously-registered webhook subscription id before trusting it). At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
```ruby
# Attacker installs the target app on their own shop "attacker.myshopify.com"
# and receives a legitimate webhook POST with:
raw_body = '{"id":123,"note":"hi"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body) # computed by Shopify for attacker's shop

# Attacker replays the same body+hmac to the app's public webhook endpoint,
# but swaps the shop-domain header to a victim's shop:
headers = {
  "x-shopify-topic" => "customers/data_request",   # or shop/redact, orders/create, etc.
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # forged, no relation to the signed body
  "x-shopify-webhook-id" => "forged-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (it only checks raw_body against app_secret)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The host application now believes this data/event genuinely originated from "victim-shop.myshopify.com".
``` [4](#0-3) [1](#0-0)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L1-63)
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

      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
      end
```
