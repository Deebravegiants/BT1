### Title
Webhook HMAC only signs the request body, allowing the `shop`, `topic`, and `webhook_id` fields used for tenant identification to be forged - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook purely by checking that the HMAC signature matches the *raw body*. All other data forwarded to the app's handler — most importantly `shop` (the tenant identifier), `topic`, `webhook_id`, and `api_version` — are read directly from HTTP headers that are **not** part of the signed content. An unprivileged internet user who can obtain any single valid `(body, hmac)` pair for the app (trivial, since it is the same shared `client_secret` for every shop that installs the app) can replay that pair to the webhook endpoint with an arbitrary forged `shop-domain` header, and the library will report the webhook as HMAC-valid while attributing the body to a victim shop of the attacker's choosing.

### Finding Description
The equality that should hold is:
`shop value used by the app to select which tenant’s data/session the webhook affects == shop value that was cryptographically bound by Shopify when the webhook was signed.`

Instead, the library only enforces:
`hmac == HMAC(secret, raw_body)`

and separately, unauthenticated:
`shop = header["shopify-shop-domain"]`

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, `api_version` are pulled straight from headers with no binding to the HMAC: [2](#0-1) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (the raw body only) and secure-compares it to the received signature: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient to trust the whole `Request`, then hands the header-derived, unauthenticated `shop`/`topic`/`webhook_id`/`api_version` straight to the app's handler as `WebhookMetadata`: [4](#0-3) 

Because the HMAC never covers `shop-domain`, any request with a body/signature pair that is valid for the shared `api_secret_key` (e.g. one legitimately captured from the attacker's own shop installation, since every shop installing the same app shares the same `client_secret`) remains "valid" no matter what `shop-domain` header is sent alongside it. The library's only integrity guarantee ("Invalid webhook HMAC" error is *not* raised) gives the impression that the entire `Request`, including `shop`, is authenticated, when in fact `shop` is attacker-controlled.

### Impact Explanation
This breaks the tenant-authentication binding for webhook processing: an unprivileged internet user (any merchant who can install the app once to legitimately obtain a valid `(body, hmac)` pair) can cause the library to hand a host application data.shop belonging to any other shop, while still passing `HmacValidator.validate`. Any host app that follows the documented usage of `WebhookMetadata#shop` to select a tenant's session/access token (the intended and recommended usage pattern) will act on a victim shop's identity using attacker-supplied body content — a cross-tenant confusion primitive. This matches the Critical "cross-tenant access" impact category, since the tenant-selection value is not bound to the cryptographic proof the library exposes as its trust signal.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that has more than one installed shop: the attacker only needs to be able to install the target app themselves (or otherwise capture one legitimate webhook delivery, which happens automatically for every app install) and then replay that request with a different `shop-domain` (and/or `topic`/`webhook_id`) header value to the same public webhook endpoint. No secrets, tokens, or privileged access are required — only a normal Shopify merchant account.

### Recommendation
Include `shop`, `topic`, and `webhook_id`/`api_version` in the signable content used for HMAC verification (or otherwise cryptographically bind them, e.g. by having `HmacValidator` compute over a canonical string of headers+body rather than body alone), so that any header value used to select the tenant cannot be altered without invalidating the signature. At minimum, document prominently that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are **not** covered by the HMAC check and must not be trusted for tenant selection without an independent cross-check (e.g., verifying the shop against an existing, previously stored session for that specific webhook subscription/`webhook_id`).

### Proof of Concept
```ruby
# 1. Attacker installs the target app on their own shop "attacker.myshopify.com"
#    and receives (or triggers) one legitimate webhook delivery, capturing:
raw_body = '{"id":123,"note":"hello"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), shared_api_secret_key, raw_body)
valid_hmac_b64 = Base64.encode64(valid_hmac)

# 2. Attacker replays the exact same body+signature to the app's public webhook
#    endpoint, but swaps the shop-domain header to point at a victim shop.
forged_headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => valid_hmac_b64,
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # <-- not covered by HMAC
  "x-shopify-webhook-id"   => "any-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. This does NOT raise ShopifyAPI::Errors::InvalidWebhookError, because
#    HmacValidator only checks `raw_body`, not `shop-domain`.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(topic: "orders/create",
#                                              shop: "victim-shop.myshopify.com",  # forged
#                                              body: {...}, ...))
```
`Registry.process` accepts this forged request as HMAC-valid, and the handler receives `shop: "victim-shop.myshopify.com"` even though the request body and signature actually originated from the attacker's own shop. [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L1-73)
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

      private

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
    end
  end
end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L1-44)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Utils
    module HmacValidator
      extend T::Sig

      class << self
        extend T::Sig

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

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
      end
    end
  end
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
