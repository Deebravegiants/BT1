### Title
Webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) header is not covered by the HMAC signature, allowing cross-tenant spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body HMAC and then forwards the unauthenticated `shop` value straight to the app's handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled directly from HTTP headers, none of which participate in the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `verifiable_query.hmac` against `verifiable_query.to_signable_string` (i.e., just the body): [3](#0-2) 

`Webhooks::Registry.process` checks only this body HMAC, then passes the unauthenticated `request.shop` on to the handler as the tenant/shop context: [4](#0-3) 

This breaks the identity binding that should hold: `hmac_signed_bytes == bytes_that_determine_the_tenant`. In reality, `hmac_signed_bytes = raw_body` while `bytes_that_determine_the_tenant = shop-domain header`, and the two are independent. Any request whose HMAC is valid for a given body can carry an arbitrary `shop-domain` (and `topic`/`api-version`/`webhook-id`) header value, because the signature never covers them.

### Impact Explanation
An attacker who operates their own shop with the app installed will legitimately receive real webhooks, each with a raw body and a valid HMAC for that body (computed with the app's `client_secret`, which the attacker never needs to know). By replaying that same body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and optionally `topic`/`webhook-id`) with a victim shop's domain, the attacker forges a webhook that the app will treat as authentic and originating from the victim's shop, since `Registry.process` only re-validates the body HMAC and unconditionally trusts `request.shop` for tenant selection when invoking `handler.handle`. Any host application that uses `WebhookMetadata#shop` to select session/tenant context, scope a database write, or otherwise disambiguate merchants without independent verification, will act on injected data attributed to the wrong tenant — a cross-tenant integrity issue.

### Likelihood Explanation
Any actor who can install the target app on their own store (a routine, unprivileged action for public/embedded Shopify apps) automatically obtains valid `(body, hmac)` pairs for their own shop. Forging the `shop-domain` header (and other identifying headers) requires only sending a normal HTTP POST with modified headers to the app's public webhook endpoint — no access to `client_secret`, tokens, or other credentials is needed. The only constraint is that the attacker-controlled body must be a byte-for-byte match to something they already legitimately received, which is trivial to satisfy for topics they can trigger on their own store (e.g., `orders/create`, `app/uninstalled`, etc.).

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` (or at minimum the shop identifier) as part of the material that is cryptographically bound to the request, or independently verify that the `shop-domain` header corresponds to a shop this app actually has an active session/installation for before acting on webhook data. At minimum, document prominently that `WebhookMetadata#shop` is derived from an unauthenticated header and must not be trusted for tenant selection without additional server-side verification (e.g., cross-checking against a known/installed shop list) prior to using it to load or mutate tenant-scoped state.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body `B` and the valid `x-shopify-hmac-sha256` header value `H` (computed by Shopify using the app's shared secret over `B`).
2. Attacker resends the identical HTTP request to the app's webhook endpoint, keeping the body `B` and header `H` unchanged, but replacing `x-shopify-shop-domain: attacker.myshopify.com` with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (= `B`) and compares it to `H` — this succeeds because `B` and `H` are unchanged.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, where `request.shop` now returns `"victim.myshopify.com"`.
5. Any handler logic that uses `data.shop` to select or mutate victim-shop-scoped state processes attacker-supplied data as if it originated from `victim.myshopify.com`. [5](#0-4) [4](#0-3)

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
