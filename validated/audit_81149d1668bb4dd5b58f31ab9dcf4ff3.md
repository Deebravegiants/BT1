This confirms the finding: `Webhooks::Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) returns only `@raw_body`, and the `shop` accessor (line 21-23) reads the `shopify-shop-domain`/`x-shopify-shop-domain` header directly, with no cryptographic binding between the two. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-190, 198-199`) validates the HMAC over the body only, then passes `request.shop` (the unauthenticated header) straight into `WebhookMetadata` for the handler to act on.

### Title
Webhook shop-domain header is not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body alone, excluding the `X-Shopify-Shop-Domain` header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then trusts `request.shop` (derived solely from that unauthenticated header) to identify which merchant the webhook belongs to.

### Finding Description
The HMAC validation binding is: `HMAC(api_secret_key, raw_body) == received_hmac`. The `shop` field used by every webhook handler is read independently from the header and never enters that computation: [1](#0-0) 

`Registry.process` validates only this body-scoped HMAC, then forwards the unauthenticated `shop` header value to the handler: [2](#0-1) 

Because the HMAC secret (`api_secret_key`) is shared by the app across *all* installed shops (it is the app's own secret, not per-shop), any shop that has legitimately installed the app can receive genuine, validly-signed webhooks for itself. An attacker who installs the app on their own store (an ordinary, unprivileged action requiring no special access) can capture one of these legitimately-signed `(raw_body, hmac)` pairs and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. Since the shop header is not part of the signed content, `Utils::HmacValidator.validate(request)` still succeeds, and the handler receives `WebhookMetadata` claiming the payload originated from the victim shop.

This breaks the identity binding "shop attributed to the webhook == shop that produced/authorized the signed bytes," which is exactly the "field acted on but not covered by the HMAC" analog called out for this class of bug.

### Impact Explanation
Depending on how the host application's webhook handler uses `WebhookMetadata#shop` (e.g., to look up the merchant's stored access token/session, update per-shop data, or trigger shop-scoped side effects), this allows an attacker-controlled shop to inject forged events attributed to an arbitrary victim shop — a cross-tenant data/action integrity break. This matches the "High: cross-tenant access" impact category, since the attacker crosses a tenant boundary using only their own legitimate app installation, without needing the victim's or the app's credentials.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-owned store (self-service, no privilege needed), (2) triggering any webhook topic to capture a valid `(raw_body, hmac)` pair, and (3) replaying that exact request to the app's public webhook endpoint with a modified shop-domain header. No knowledge of `api_secret_key` or any victim credential is required, making this readily reachable by any unprivileged internet user who can install the app once.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signable content used by `to_signable_string`, or otherwise cryptographically bind the shop identity to the verified payload (e.g., require handlers to independently validate `shop` against an app-side allowlist of installed/authorized shop domains before trusting `WebhookMetadata#shop`), rather than relying solely on an unauthenticated header value passed through from `Registry.process`.

### Proof of Concept
1. Install the target Shopify app on attacker-owned store `attacker-shop.myshopify.com`.
2. Trigger a webhook (e.g., `orders/create`) and capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends — this HMAC is valid for that body under the app's shared `api_secret_key`.
3. Replay the identical raw body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` instead of the attacker's own domain.
4. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/webhooks/registry.rb:190` succeeds (it only checks the body against the HMAC), and the handler in `Registry.process` receives `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, causing the app to process/act on data as if it came from `victim-shop.myshopify.com`. [3](#0-2) [2](#0-1)

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
