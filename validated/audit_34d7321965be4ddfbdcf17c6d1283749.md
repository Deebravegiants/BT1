### Title
Webhook Shop Domain Header Not Covered by HMAC Signature Enables Cross-Tenant Webhook Forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The webhook HMAC verification in this gem only signs and validates the raw request body. The `shop-domain` (and `topic`, `webhook-id`, `api-version`) headers are read directly from unauthenticated HTTP headers and are never included in the signed payload. An attacker who can obtain one genuine, HMAC-signed webhook payload for the shared app secret (e.g., by triggering a webhook on their own installed shop) can replay that exact `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header for a victim shop. The signature check still passes, and the webhook handler is invoked believing the data belongs to the victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` — i.e. `HMAC(secret, raw_body)` — and compares it to the `hmac` header. It never binds `shop`, `topic`, or `webhook_id` into that computation: [3](#0-2) [4](#0-3) 

Once the HMAC on the body passes, `request.shop` (an unauthenticated header value) is forwarded verbatim into `WebhookMetadata` and handed to the app's registered handler as the authoritative shop identity for that webhook: [5](#0-4) 

The identity binding broken is: `shop authenticated (implied by valid HMAC over body, shared secret across all shops of the app) != shop consumed by application code (request.shop header, unauthenticated)`. Because a single app's `api_secret_key` is shared across every shop that installs the app, any merchant that installs the app can generate a body+HMAC pair that is valid for the app secret (e.g., by causing their own shop to emit an `orders/create` webhook and capturing the exact bytes Shopify sent). That pair remains valid no matter what `shop-domain` header accompanies it, because the header is never part of the signed content. This is a direct instance of "a field acted on but not covered by the HMAC" that breaks a shop-tenant identity boundary, since the app's webhook endpoint is a single public HTTP endpoint shared by all installed shops.

### Impact Explanation
This enables cross-tenant access/confusion: a malicious merchant who has installed the app on their own store can forge webhook deliveries that the host application will process as though they originated from any other shop (a competitor's shop, or a target for data corruption), by supplying an arbitrary `shop-domain`/`x-shopify-shop-domain` header alongside a body+HMAC pair that is valid because it was legitimately generated for the attacker's own shop. Depending on how the host application's webhook handlers act on `WebhookMetadata#shop` (e.g., updating shop-scoped data, triggering uninstall cleanup, mutating records keyed by shop), this can result in cross-tenant data corruption or unauthorized actions performed against a different merchant's data — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is High for any app that has more than one shop installed (the norm for a multi-tenant app), since:
1. The `api_secret_key` is shared across every shop using the app.
2. Any installed merchant fully controls when/how their own shop triggers webhook-eligible events and can capture the exact `raw_body` and computed `hmac` Shopify sends to the app's single public endpoint.
3. Replaying that captured body+HMAC to the same public endpoint with a different `shop-domain` header requires no credentials, no TLS interception, and no access to the app's secret — only a normal HTTP client.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the HMAC verification, not just the raw body — e.g., include the `shop-domain` header value (and topic) as part of the signed/verified content, or cross-check the header shop against an out-of-band trusted source (such as a shop that is known to be installed with a valid, previously-issued access token) before trusting `WebhookMetadata#shop`. At minimum, document and enforce that host applications must verify the `shop` value in `WebhookMetadata` against their own session/install records before acting on it, and consider rejecting webhooks whose header-declared shop cannot be independently corroborated.

### Proof of Concept
1. App AttackerCo installs the target Shopify app on `attacker.myshopify.com`, sharing the same `client_secret`/`api_secret_key` as every other shop using this app.
2. AttackerCo triggers an event (e.g. creates an order) causing Shopify to POST a webhook to the app's single public webhook endpoint with headers:
   - `x-shopify-topic: orders/create`
   - `x-shopify-hmac-sha256: <valid HMAC of raw body under shared secret>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - body: `{"id": ...}`
3. AttackerCo (or a network-observing party at the receiving end, using nothing but a normal HTTP client) resends this exact captured raw body and `x-shopify-hmac-sha256` value to the same public endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` — unaffected by the changed shop header — and the check passes.
5. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's order payload, and the host application processes it as data for `victim.myshopify.com`, corrupting or misdirecting shop-scoped state for a tenant the attacker never controls. [6](#0-5) [7](#0-6) [8](#0-7)

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
