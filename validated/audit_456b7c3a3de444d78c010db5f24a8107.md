Confirmed: `Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) validates the HMAC via `Utils::HmacValidator.validate(request)`, but that validation only covers `request.to_signable_string`, which in `Webhooks::Request#to_signable_string` (lib/shopify_api/webhooks/request.rb:36-38) returns only `@raw_body`. The `shop` (line 21-23) and `topic` (line 16-18) values are read straight from HTTP headers and are never included in the HMAC computation, yet `Registry.process` forwards `request.shop` and `request.topic` directly into `WebhookMetadata` for the handler to act on (registry.rb:198-199) without any additional cross-check.

### Title
Webhook `shop` and `topic` fields are trusted from unauthenticated headers while only the body is HMAC-verified - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook request's authenticity solely via `Utils::HmacValidator.validate(request)`, which computes the signature over `request.to_signable_string` — defined in `ShopifyAPI::Webhooks::Request#to_signable_string` as `@raw_body` only. The `shop-domain` and `topic` header values consumed by `Request#shop` and `Request#topic` are never part of the signed material, yet they are passed unmodified into `WebhookMetadata` and used by the registered handler to decide "which tenant/topic this event is for."

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `hmac`, and other identifying fields purely from HTTP headers: [1](#0-0) 
The HMAC signable string used for verification is defined as only the raw body: [2](#0-1) 
`Utils::HmacValidator.validate` recomputes the HMAC over that signable string (the body) and compares it to the `hmac` value, again taken from a header: [3](#0-2) 
`Registry.process` treats a passing HMAC check as proof that the entire request — including `shop` and `topic` — is authentic, and hands those header-derived values straight to the app's handler: [4](#0-3) 

The equality the code implicitly assumes is: `hmac_valid(raw_body) == request_is_authentically_from_shop_X_about_topic_Y`. That equality does not hold, because `shop` and `topic` are bytes that are read but never verified — they are outside the HMAC-covered surface. An attacker who can capture (or legitimately obtain, e.g. via their own installed test shop) any one valid `(raw_body, hmac)` pair can replay it to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` and/or `x-shopify-topic` headers with values naming a different tenant/topic. `Utils::HmacValidator.validate` will still return `true`, because it only checks the body against the HMAC. `Registry.process` will then invoke the handler with an attacker-chosen `shop` and/or `topic`, since `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` places these unauthenticated values directly into the trusted-looking metadata object passed to the app.

### Impact Explanation
This breaks the tenant/topic identity binding that host applications rely on when processing webhooks. A concrete cross-tenant scenario:
1. Attacker installs the app on their own (attacker-owned) shop and triggers a webhook — e.g. `app/uninstalled` or any topic whose body content is generic/predictable — obtaining a genuinely valid `(raw_body, hmac)` pair signed with the app's `api_secret_key`.
2. Attacker POSTs this exact body+hmac to the app's public webhook endpoint, but sets `x-shopify-shop-domain` to a victim shop's domain (and/or `x-shopify-topic` to a different registered topic).
3. `Utils::HmacValidator.validate` passes because it never inspected `shop`/`topic`.
4. The handler receives `data.shop == "victim-shop.myshopify.com"` and acts on it (e.g., deletes/invalidates the victim's stored session on `app/uninstalled`, or misattributes/mismatches other tenant data), even though nothing about the request was actually verified as originating from, or pertaining to, that shop.

This is a cross-tenant identity-binding break reachable by any unprivileged actor able to send HTTP requests to the app's public webhook endpoint — no access token, TLS interception, or leaked secret is required beyond a webhook payload the attacker can legitimately generate for themselves.

### Likelihood Explanation
The webhook endpoint is, by design, a public, unauthenticated HTTP endpoint (this is inherent to how Shopify delivers webhooks). Getting a valid `(body, hmac)` pair only requires installing the app on any shop the attacker controls (trivial, e.g. a free development store) and receiving any webhook with reasonably predictable/generic body content. No privileged credentials of the target app or victim shop are needed.

### Recommendation
Bind `shop` and `topic` (and ideally `webhook_id`/`api_version`) into the HMAC-signed material, or otherwise cryptographically tie them to the verified body (e.g., include them in `to_signable_string`, or require the host app to independently confirm the asserted `shop` is one that actually has this app installed and that the `topic` matches an expected registration before trusting `data.shop`/`data.topic`). At minimum, document prominently that `data.shop` and `data.topic` are not covered by the HMAC and must not be trusted for tenant-scoping decisions without additional verification.

### Proof of Concept
```ruby
require "openssl"
require "shopify_api"

ShopifyAPI::Context.setup(
  api_key: "key", api_secret_key: "secret", api_version: "2024-01",
  host_name: "example.com", scope: [], is_private: false, is_embedded: true
)

body = "{}" # generic body obtained from a webhook legitimately delivered to attacker's own shop
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)

# Attacker forges headers claiming a different (victim) shop/topic while reusing the valid body+hmac
forged_headers = {
  "x-shopify-topic" => "app/uninstalled",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

# Passes because HmacValidator only checks body:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Handler receives forged shop/topic as if authenticated:
ShopifyAPI::Webhooks::Registry.process(request)
``` [4](#0-3) [5](#0-4)

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
