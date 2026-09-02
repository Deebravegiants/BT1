### Title
Webhook `shop-domain` header spoofing enables cross-tenant webhook injection — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` treats the `X-Shopify-Shop-Domain` header as authenticated tenant identity, but the HMAC signature the gem verifies only covers the raw request body, not this header. This lets a party who can obtain a validly-signed webhook payload (e.g., a merchant who has installed the app on their own shop and receives their own genuinely-signed webhooks) replay that payload to the app's webhook endpoint with an arbitrary `shop` header, causing the host application to process attacker-chosen data as if it belongs to a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely via: [1](#0-0) 

The HMAC check calls `Utils::HmacValidator.validate(request)`, which validates `request.to_signable_string` against the HMAC: [2](#0-1) 

But `Request#to_signable_string` returns only `@raw_body` — it excludes every header, including `shop`: [3](#0-2) 

Meanwhile `Request#shop` is read directly from the (unsigned) `shopify-shop-domain`/`x-shopify-shop-domain` header: [4](#0-3) 

That unverified value is then passed straight through to the host application's webhook handler as trusted tenant identity: [5](#0-4) 

This is exactly the identity-binding break called out in the analog class: **the field acted on (`shop`, used to select the tenant whose data the handler will read/write) is not covered by the HMAC that is supposed to authenticate the request.** The equality that should hold — `shop-authenticated-by-HMAC == shop-used-by-handler` — does not hold, because only the body is bound to the signature.

### Impact Explanation
Because the app's `api_secret_key` is shared across all shops that install the app, a merchant who legitimately installs the app on **their own** shop will receive genuinely HMAC-signed webhooks for their own shop's events (the same secret signs webhooks for every tenant of a multi-tenant app). That merchant can capture one such valid `(body, hmac)` pair and resend it to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. Since the header is outside the signed payload, `HmacValidator.validate` still returns `true`, and `Registry.process` forwards `shop: <victim-shop>` to the app's `WebhookHandler`. If the host application uses this `shop` value to look up per-tenant records, credentials, or to trigger tenant-scoped side effects (a documented, expected usage pattern of this API, per `WebhookMetadata`/`WebhookHandler#handle`), this results in cross-tenant data injection/access — writing or triggering actions against a shop the attacker does not control. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires: (1) the ability to install the vulnerable app on an attacker-owned/attacker-controlled shop (trivial for any public or unlisted Shopify app), (2) capturing one legitimately delivered webhook for that shop, and (3) POSTing the same body with a forged shop header to the app's public webhook URL. No access token, `client_secret`, or privileged account is required — this is reachable by any unprivileged internet user who can install the app once. Likelihood is high.

### Recommendation
Bind the shop identity into the authenticated payload before trusting it:
- Include the `shop` (and ideally `topic`, `webhook-id`) values in the HMAC-signable string (`VerifiableQuery#to_signable_string`) so any tampering invalidates the signature, or
- Cross-check the header-derived `shop` against an out-of-band trusted source (e.g., verify the shop is one the app has an active session/install record for) before dispatching to the handler, and
- Document/require host applications to independently verify `shop` is a known installed tenant rather than trusting the gem's `Request#shop` as authenticated.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any subscribed webhook topic (e.g., `orders/create`), receiving a request with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's shared `api_secret_key`.
2. Attacker replays the exact same raw body and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` computes `HmacValidator.validate(request)` over `raw_body` only — the check passes because the body/hmac pair is genuinely valid.
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` even though the payload never actually originated from Shopify for that shop, demonstrating the unauthenticated identity binding. [6](#0-5) [1](#0-0)

### Citations

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
