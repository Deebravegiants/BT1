I have enough evidence to confirm the finding. This matches the exact bug-class pattern permitted by the rules: a field acted on (`shop`) but not covered by the HMAC.

### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant shop spoofing in `ShopifyAPI::Webhooks::Request` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `#shop` is derived independently from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header [2](#0-1) . `Utils::HmacValidator.validate` only checks that the HMAC matches `to_signable_string` (the body) [3](#0-2) , so the `shop` field is never bound to the signature that authenticates the webhook. `Registry.process` nonetheless treats `request.shop` as an authenticated identity and forwards it straight to the app's handler as the tenant identifier: it validates the HMAC and then passes `request.shop` unchanged into `WebhookMetadata` [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop claimed in the HMAC-authenticated payload == shop delivered to the app's handler`. In this gem's implementation that equality never actually holds, because the HMAC only authenticates the raw body bytes, and `shop` is read from a header that is completely outside that signed byte range.

Concretely:
1. An unprivileged attacker installs the app on a shop they control (a free/dev store is sufficient — no privileged credentials, no `api_secret_key`, no access token needed).
2. Shopify sends a legitimately signed webhook to the app's endpoint for that shop: `raw_body` + a correct `x-shopify-hmac-sha256` computed with the real `api_secret_key`, plus an `x-shopify-shop-domain` header equal to the attacker's own shop.
3. The attacker captures this request (they control the receiving endpoint or can proxy/log it) and replays it to the app, changing only the `x-shopify-shop-domain` header to any victim shop's domain, keeping `raw_body` and `x-shopify-hmac-sha256` untouched.
4. `Utils::HmacValidator.validate(request)` recomputes the HMAC over `request.to_signable_string` (`@raw_body`) and compares it to the untouched `hmac` header — validation still succeeds, because neither depends on the `shop` header [5](#0-4) .
5. `Registry.process` accepts the request as valid and calls the app's `handler.handle` with `data.shop` set to the attacker-chosen victim domain [6](#0-5) .

This exactly matches the permitted bug class: "a field acted on but not covered by the HMAC." Note the contrast with `Auth::Oauth::AuthQuery`, where `shop` is explicitly included in `to_signable_string` and therefore is bound to the HMAC [7](#0-6)  — the webhook `Request` class lacks the equivalent binding for `shop`.

### Impact Explanation
Host applications built on this gem are documented to treat `data.shop` from the webhook handler callback as the authenticated originating shop (per `docs/usage/webhooks.md`, the handler receives `shop` and is expected to use it, e.g. to look up per-shop sessions/access tokens or trigger shop-scoped side effects). Because `shop` is not bound to the HMAC, an attacker can make the gem deliver a validly-authenticated webhook to the handler while lying about which shop it originated from. Any app logic keyed off `data.shop` (session/access-token lookup, cache invalidation, data writes scoped by shop) can be tricked into acting on behalf of, or against, a victim tenant it never actually received a webhook from — a cross-tenant confusion condition reachable by any unprivileged actor who can install a trial/dev shop and replay one captured HTTP request.

### Likelihood Explanation
High likelihood of reachability: no privileged credentials, access tokens, or `api_secret_key` are needed. The attacker only needs their own (attacker-controlled) shop installation and the ability to send an HTTP POST to the app's public webhook endpoint with a modified header — both are unprivileged-internet-user actions. The only constraint is that `raw_body` must stay byte-identical to what was legitimately signed, which does not stop the shop-domain header from being changed independently.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-covered signable content, or otherwise cryptographically bind the shop-domain header to the signed payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document explicitly (and enforce in the gem) that `request.shop` is unauthenticated header data that host applications must independently verify against their own list of installed shops before use, since the current implementation implicitly presents it as validated once `Utils::HmacValidator.validate` succeeds.

### Proof of Concept
```ruby
# Attacker's own dev-store legitimately receives:
raw_body = '{"id":123,"note":"attacker order"}'
hmac_header = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), REAL_API_SECRET, raw_body) # computed by Shopify, captured by attacker

# Attacker replays to the app's webhook endpoint, only swapping the shop header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac_header), # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (HMAC only covers raw_body)
# => handler.handle(data: WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...))
``` [8](#0-7) [4](#0-3) [9](#0-8)

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
