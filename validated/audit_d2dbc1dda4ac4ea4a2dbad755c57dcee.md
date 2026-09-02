### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only covers the request body, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature it validates only covers the raw request body, never the headers. Any attacker who controls a genuine, installed shop (an ordinary, unprivileged merchant) can capture a real webhook delivery — complete with a body and a valid HMAC computed by Shopify using the app's shared `api_secret_key` — and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to point at a victim shop. `HmacValidator.validate` will still pass because the body (the only signed material) is untouched, and the forged `shop` value will flow straight into `WebhookMetadata`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop` is read directly from the unauthenticated `x-shopify-shop-domain` (or `shopify-shop-domain`) header, with no cryptographic tie to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then immediately trusts `request.shop` as the tenant identity for the handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and the app's shared `api_secret_key` — it is not shop-specific, since the same secret is used for every shop that installs the app: [4](#0-3) 

The identity binding that should hold is:
`shop_used_for_HMAC_signing == shop_passed_to_the_handler`

In this implementation that equality does not hold: the HMAC is computed over the body only (no `shop` claim inside it), while the `shop` value used to route/process the payload comes from a header field that carries zero authentication weight. Because the HMAC secret is shared across all shops of the same app, a webhook body/HMAC pair generated for shop A's own webhook is equally "valid" no matter what `x-shopify-shop-domain` header accompanies it.

### Impact Explanation
An unprivileged attacker who merely installs the target app on their own store (a normal, permitted action) can:
1. Receive a legitimate webhook from Shopify for their own store, capturing the raw body and its valid `x-shopify-hmac-sha256` value.
2. Replay that exact body/HMAC pair to the app's webhook endpoint, substituting `x-shopify-shop-domain` with a victim merchant's domain.
3. `HmacValidator.validate` still returns `true` (body unchanged), and `Registry.process` calls the registered `WebhookHandler` with `WebhookMetadata.new(shop: <victim shop>, body: <attacker-controlled data>, ...)`.

This lets the attacker inject data that the host application will treat as authentic data belonging to another tenant (e.g., triggering shop-scoped business logic, writes, or notifications keyed by `shop`), i.e., cross-tenant data injection/confusion — a violation of tenant isolation that this gem is expected to guarantee via HMAC verification.

### Likelihood Explanation
The prerequisite is only that the attacker be able to install the app on any shop they control (the normal, unprivileged onboarding flow for any Shopify app) and be able to send an HTTP POST to the app's public webhook endpoint with custom headers — both trivially available to any internet user, requiring no leaked secrets, no privileged account, and no access to the app's `client_secret` or any merchant's access/refresh token.

### Recommendation
Bind the shop identity into the material that is actually verified by the HMAC, or otherwise cryptographically tie the `x-shopify-shop-domain` header to the signed payload before trusting it. Concretely:
- Extend `VerifiableQuery#to_signable_string` for `Webhooks::Request` to include the shop-domain header (or otherwise validate that the header value matches a shop-scoped secret/session known to the app), so the HMAC check fails if the header is altered independently of the body, or
- Require callers to supply the expected shop (from their own session/subscription bookkeeping) and assert it equals `request.shop` before invoking any handler, rather than trusting the header value unconditionally.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook subscribed by the app (e.g. `orders/create`), receiving:
   - Body: `{"id":1,...attacker-controlled order fields...}`
   - Header: `x-shopify-hmac-sha256: <valid HMAC of body, computed with the app's shared api_secret_key>`
   - Header: `x-shopify-shop-domain: attacker-shop.myshopify.com`
2. Attacker resends the identical body and the identical `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets:
   - Header: `x-shopify-shop-domain: victim-shop.myshopify.com`
3. Inside the app, `Registry.process` runs:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
# passes, because HmacValidator only checks the (unchanged) body against the shared secret
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
# request.shop == "victim-shop.myshopify.com", attacker-controlled
```
4. The app's handler now processes attacker-controlled webhook data as if it belonged to `victim-shop.myshopify.com`. [5](#0-4) [3](#0-2) [6](#0-5)

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
