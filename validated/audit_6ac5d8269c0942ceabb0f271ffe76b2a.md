### Title
Webhook cross-tenant spoofing: `shop` header is not covered by HMAC validation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating the HMAC over the raw request body only, yet the `shop` (and `topic`/`webhook_id`) values that are handed to the application's webhook handler — and that the host app uses to attribute the payload to a specific merchant/tenant — come from unauthenticated HTTP headers that are never part of the signed material. An attacker who is themselves a legitimate installer of the app (and therefore receives genuinely-signed webhooks for their own shop) can capture one such request and replay it with a forged `shopify-shop-domain` header, causing the app to process a real, validly-signed payload under a different, spoofed tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to them: [2](#0-1) 

`Registry.process` validates the request solely via `Utils::HmacValidator.validate(request)`, which — because `to_signable_string` only returns the body — only proves the body bytes are intact; it proves nothing about the `shop` header. It then forwards the *unauthenticated* `shop` value straight into `WebhookMetadata`, which is what the application handler uses to know which tenant the payload belongs to: [3](#0-2) 

`HmacValidator.validate_signature` confirms this — it recomputes the HMAC purely from `verifiable_query.to_signable_string` (the body) and the shared `api_secret_key`, with no reference to the shop header at all: [4](#0-3) 

The equality that should hold but is broken is:

`shop_authenticated_by_HMAC == shop_delivered_to_handler`

In reality the gem only enforces `HMAC(raw_body) == received_hmac`; the `shop` field acted upon by the handler is a completely separate, unauthenticated header. Any party capable of sending an HTTP request to the app's webhook endpoint carrying a *previously-observed, validly-signed* `raw_body` + `hmac` pair can attach an arbitrary `shopify-shop-domain` (or `x-shopify-shop-domain`) header value. Since a merchant who installs the app legitimately receives real signed webhooks for their own shop, that merchant (an "unprivileged" tenant of the multi-tenant app, not a privileged operator) can capture one of their own webhooks and replay it against the same endpoint with the `shop` header rewritten to another merchant's domain. `Registry.process` will accept it (HMAC still matches the untouched body) and dispatch it to the handler labeled as belonging to the victim shop.

### Impact Explanation
This breaks the tenant isolation boundary the gem is expected to provide via HMAC verification of webhooks. A host application that (reasonably, per the gem's documented contract) trusts `WebhookMetadata#shop` to select which merchant's record to update will process attacker-supplied data under another tenant's identity — a cross-tenant data injection/corruption primitive reachable by any shop that has installed the app, without needing the app's `client_secret` or any privileged credential. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any multi-tenant app built on this gem's webhook registry: capturing one's own legitimately delivered webhook (body + `hmac-sha256` header) requires no special access, and replaying it with a modified `shop-domain` header against the app's public webhook endpoint is trivial HTTP tooling. No secret material, TLS interception, or social engineering is required — only that the attacker is (or was) an installed, unprivileged tenant of the app.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-verified material, or otherwise cryptographically tie the header-derived shop identity to the payload before constructing `WebhookMetadata` in `Registry.process`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the host app against its own record of which shop the webhook subscription belongs to (e.g., via the `webhook_id` looked up server-side) rather than trusted at face value.

### Proof of Concept
1. App installs webhooks for `shop-a.myshopify.com`; a legitimate order-update webhook arrives at the app's endpoint with body `B`, header `shopify-shop-domain: shop-a.myshopify.com`, and a correctly computed `shopify-hmac-sha256` header over `B`.
2. The merchant of `shop-a` (an unprivileged party from the app's perspective, but who legitimately receives their own webhooks) intercepts/records this raw request.
3. They resend the exact same body `B` and `hmac-sha256` header to the app's webhook endpoint, but change `shopify-shop-domain` to `shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`= B`) and finds it matches — validation passes.
5. The handler receives `WebhookMetadata.new(topic:, shop: "shop-b.myshopify.com", body: parsed(B), ...)` and, if it uses `shop` to select the tenant record, updates/creates data for `shop-b` using data that Shopify never sent for `shop-b`. [3](#0-2) [5](#0-4)

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
