### Title
Webhook `shop-domain` (and `topic`/`webhook_id`/`api_version`) headers are not covered by the HMAC signature, breaking the binding between the authenticated payload and the shop it is attributed to - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` authenticates the JSON body bytes but never authenticates the `shop-domain`, `topic`, `webhook_id`, or `api_version` headers that `Registry.process` reads straight off the same `Request` object and hands to the app's webhook handler.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
only `@raw_body` is included. `Registry.process` verifies the HMAC and then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which participated in the signature: [2](#0-1) 

The equality that should hold is:
`hmac == HMAC(secret, raw_body ∥ shop ∥ topic ∥ webhook_id)`

but the actual check is only:
`hmac == HMAC(secret, raw_body)`

Since Shopify apps use a single `client_secret`/`api_secret_key` shared across every shop that installs the app (this is exactly the key `HmacValidator.validate` uses, via `Context.api_secret_key`), a valid `(raw_body, hmac)` pair obtained from one authentic webhook delivery (e.g. for the attacker's own installed shop) remains cryptographically valid for that same body under **any** `shop-domain`, `topic`, `webhook_id`, or `api_version` header value, because those headers are not part of the signed material. This is structurally the same bug class as the TWAP report cited: a value that is *acted upon* by downstream logic (mint/redeem decisions there; shop attribution here) is not bound/verified by the mechanism that is supposed to guarantee its integrity (fixed TWAP window there; HMAC coverage here).

### Impact Explanation
An attacker who is a legitimate (but unprivileged, low-trust) user of the app on any one shop can receive one authentic webhook delivery for that shop, then replay the identical signed body to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `topic`/`webhook_id`) to point at a different, victim shop. `HmacValidator.validate` still succeeds because the signature only covers `raw_body`. `Registry.process` then constructs `WebhookMetadata.new(topic:, shop:, body:, api_version:, webhook_id:)` from the attacker-controlled headers and invokes the host app's handler with that forged shop attribution — a cross-tenant integrity issue: data/events destined for the attacker's own shop can be attributed to and processed against another merchant's shop/session inside the host application.

### Likelihood Explanation
Moderate. It requires the attacker to have installed the app on at least one shop to obtain one authentic signed payload, but no access token, `client_secret`, or privileged Shopify credential is needed — only a normal app install, which is available to any internet user for public apps. The header rewrite and replay require nothing more than a basic HTTP client.

### Recommendation
Bind the identity fields into the signed material (or otherwise cryptographically tie them to the body), e.g. include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or independently verify that the shop the webhook claims to be from actually owns/expects the delivered `webhook_id`/`topic` before invoking the handler, rather than trusting unauthenticated headers alongside an HMAC that only covers the body.

### Proof of Concept
1. Install the target app on attacker-controlled Shop A; capture one legitimate webhook POST (raw body `B`, headers including `x-shopify-hmac-sha256: H`, `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: T`).
2. Replay the exact same body `B` and `H` to the app's webhook endpoint, but set `x-shopify-shop-domain: shop-b.myshopify.com` (victim shop).
3. `Utils::HmacValidator.validate` succeeds (`compute_signature(B, secret) == H`), since only `B` is signed.
4. `Registry.process` builds `WebhookMetadata` with `shop: "shop-b.myshopify.com"` and dispatches it to the host application's handler, which will process/store the attacker's data as if it originated from Shop B. [3](#0-2) [4](#0-3)

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
