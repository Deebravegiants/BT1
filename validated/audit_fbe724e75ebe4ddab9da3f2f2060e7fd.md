### Title
Webhook shop identity spoofing via HMAC that only covers the request body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable string from the raw body only, while the `shop` (and `topic`/`webhook_id`) values used downstream to attribute a webhook to a tenant come from unauthenticated HTTP headers. The identity binding `verified_bytes == attributed_shop` does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cross-check against the HMAC-signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the body via `HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e., the raw body) and compares it against `verifiable_query.hmac` computed with `Context.api_secret_key`: [3](#0-2) [4](#0-3) 

After this HMAC check passes, `Registry.process` forwards `request.shop` — a value never covered by the signature — directly to the consuming application's handler as the authenticated tenant identifier: [5](#0-4) 

Because the HMAC is computed only over the raw JSON body, any request carrying a body+HMAC pair that is valid for the app's secret (e.g., a webhook payload legitimately delivered to the attacker's own shop, since any merchant can install the app on their own store and receive real webhook deliveries with valid HMACs) will still pass `HmacValidator.validate` even if the `shop-domain` header is changed to name a different (victim) shop. The equality the code should enforce — "the shop this webhook is attributed to" == "the shop whose data produced the HMAC-covered bytes" — is never checked; only "the body bytes are unmodified" is checked.

### Impact Explanation
This breaks the tenant/shop identity binding for webhook processing: an attacker who legitimately installs the app on their own shop (an unprivileged step, no special credentials) can capture a real, validly-signed webhook body from their own store and replay it against the app's webhook endpoint with an altered `shop-domain` header pointing at a victim shop. Since `WebhookMetadata.shop` is set from the unauthenticated header, the host application's webhook handler will process attacker-controlled data as if it originated from and pertains to the victim shop — this is a cross-tenant data-attribution issue at the library level, satisfying the "cross-tenant access" impact class, since the shop-scoping decision (which tenant's records to read/write/delete based on the webhook) is made using data this gem asserts is verified but is not.

### Likelihood Explanation
Requires only network access to the app's publicly exposed webhook endpoint and possession of one validly-HMAC-signed body (trivially obtainable by installing the app on one's own store and receiving any real webhook, or, for topics/shapes that are attacker-influenceable such as `app/uninstalled`, `customers/data_request`, product/order events on the attacker's own shop, etc.). No access to `api_secret_key`, tokens, or the victim's credentials is needed. The header can be freely set by any HTTP client since headers are attacker-controlled input to the endpoint the gem parses.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the HMAC-covered signable content, or otherwise cryptographically bind the header-derived identity fields to the verified payload before they are trusted (e.g., require the `shop` used for routing/handler dispatch to be re-derived only from data covered by the signature, or document/enforce that consuming apps must independently confirm the shop is one with an active installation/session before trusting `WebhookMetadata#shop`). At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header so replay against a different tenant invalidates the signature.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":1,...}` with header `x-shopify-hmac-sha256: <valid HMAC of body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker replays the identical body and HMAC header to the app's webhook endpoint but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL.secure_compare(computed_signature, received_signature)` against the raw body — this succeeds because the body is unchanged.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` and invokes the app's handler, which now believes this attacker-supplied payload legitimately belongs to `victim-shop.myshopify.com`. [3](#0-2) [6](#0-5)

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
