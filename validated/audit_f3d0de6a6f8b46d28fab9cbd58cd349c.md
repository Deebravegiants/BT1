### Title
Shopify webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the caller-supplied `shop-domain` header straight through to the app's handler as the tenant identifier, without that header ever being part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` accessor, however, is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header with no cryptographic binding to that header value: [2](#0-1) .

`Registry.process` verifies the HMAC via `Utils::HmacValidator.validate(request)` — which only checks `request.to_signable_string` (the body) against the shared `api_secret_key` — and, once that passes, immediately trusts `request.shop` to build the `WebhookMetadata` that is forwarded to the app-provided handler: [3](#0-2) . `HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` and the app's `api_secret_key`: [4](#0-3) .

Because `api_secret_key` is a single per-app secret shared across every shop that installs the app (not a per-shop secret), a valid `(body, hmac)` pair only proves "this body was produced by an entity holding the app's secret" — it proves nothing about which shop the event belongs to. The `WebhookMetadata.shop` field the gem hands to `WebhookHandler#handle` is documented as "The shop domain of the webhook" and is expected by consuming apps to be a trustworthy tenant key: [5](#0-4) , [6](#0-5) .

This is the same bug class as the reported `proposeUpdateTransmitters` issue: an identity/tenant-scoping field (`shop`) is acted upon by privileged downstream logic (the handler dispatch/tenant lookup) without being covered by the authentication mechanism (the HMAC) that is supposed to bind the request to its true origin. The broken equality is:
`shop header value used to select tenant data` ≠ `shop bound inside the HMAC-signed payload`.

### Impact Explanation
Any party capable of producing one legitimately-signed webhook body/HMAC pair for the app (e.g., a merchant who has installed the app on their own store and can trigger a webhook event, such as `orders/create`) can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary value in the `shop-domain` header. Because `Registry.process` never cross-checks the header against anything covered by the signature, the app's handler will receive `WebhookMetadata` claiming the event came from a different, victim shop. If the app uses `data.shop` to select which tenant's records to update/create (a very common pattern, exactly as shown in the gem's own webhooks documentation example `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), this enables cross-tenant data injection/corruption — writing attacker-controlled webhook payloads into another merchant's tenant context. This satisfies the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation only requires being an app user (or otherwise obtaining one valid signed webhook body for any topic the app processes) plus the ability to send an arbitrary HTTP request with a forged `shop-domain` header to the app's public webhook callback URL — no access to `api_secret_key`, tokens, or the target shop is needed. The HMAC validation logic in this gem provides no protection against this because it was never designed to authenticate the header, only the body.

### Recommendation
The gem should not treat the `shop-domain` header as trusted tenant-identifying data based on HMAC validation of the body alone. At minimum, the library should document prominently (and ideally enforce via an optional API) that consuming applications must independently verify that the reported `shop` is one of their installed/authorized shops (e.g., look up a stored session/access token for that shop) before acting on `WebhookMetadata.shop`, since the HMAC in Shopify's webhook design binds only the payload, not the sender's claimed shop.

### Proof of Concept
1. Install the target app on an attacker-controlled dev store `attacker.myshopify.com` and subscribe to a webhook topic the app handles (e.g., `orders/create`).
2. Trigger the event to receive a legitimately Shopify-signed webhook: capture `raw_body` and the `X-Shopify-Hmac-Sha256` header value.
3. Replay the exact same `raw_body` and `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds (it only checks the body against the shared `api_secret_key`), and `Registry.process` dispatches the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the payload never originated from that shop. [3](#0-2) [7](#0-6)

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
