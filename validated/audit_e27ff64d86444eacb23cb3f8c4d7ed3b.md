Confirmed: the Shopify webhook HMAC binds only the raw request body, not the `shop-domain` header that identifies the tenant. This is a genuine analog of the reported bug class ("a field acted on but not covered by the HMAC").

### Title
Webhook `shop-domain` Header Not Bound to HMAC Signature Allows Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw request body alone, while the `shop` (tenant identity) is read from a separate, unsigned HTTP header. `ShopifyAPI::Webhooks::Registry.process` trusts this unauthenticated header value and forwards it to the host application's webhook handler as the tenant identity, without it ever being covered by the cryptographic signature check.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that body [2](#0-1) .

`HmacValidator.validate` verifies the request purely by recomputing `HMAC(api_secret_key, to_signable_string)` and comparing it to the `hmac` field [3](#0-2) . Because `to_signable_string` never includes the shop domain, the HMAC only proves "this body was signed by Shopify with this secret" — it proves nothing about which shop the body belongs to.

`Registry.process` performs exactly this check and then unconditionally forwards the unauthenticated `request.shop` value to the handler as the tenant identity: [4](#0-3) 

The broken identity binding, stated as an equality: `HMAC_valid(body) == true` is treated by the gem as implying `shop_header == originating_tenant(body)`, but the HMAC never covers `shop_header`, so this equality does not actually hold. Any party capable of obtaining one validly-signed webhook body/HMAC pair for topic T (e.g., by installing the app on their own store and receiving a legitimate webhook) can replay the identical body+HMAC to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` because the signature check is body-only, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the attacker-chosen shop [5](#0-4) .

### Impact Explanation
This crosses a tenant boundary: a shop that legitimately receives webhooks for itself can forge the appearance of a webhook "from" a different shop, since the app-side handler (built on top of this gem's guarantees) receives a `shop` value that was never authenticated. Any host application logic that trusts `WebhookMetadata#shop` for tenant-scoped side effects (looking up sessions, applying data changes, redacting/creating records) can be manipulated into acting against a victim tenant using attacker-supplied data — a cross-tenant access primitive stemming from a missing identity binding, matching the report's underlying bug class (field acted upon but not covered by the integrity check).

### Likelihood Explanation
Exploitation requires no possession of the `api_secret_key`: the attacker only needs to be a legitimate merchant/installer of the app (an "unprivileged internet user" relative to other tenants) to capture one valid `(body, hmac)` pair from their own installation, then replay it with a forged shop header directly at the app's public webhook endpoint. This is a straightforward HTTP replay with header substitution, no cryptography to break.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signable string that is HMAC-verified, or otherwise cryptographically bind the tenant identity to the signed payload before trusting `request.shop` in `Registry.process`. At minimum, document and encourage host applications to cross-check `request.shop` against an independently-known tenant identifier (e.g., the webhook subscription's registered destination) rather than trusting it outright.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com` and trigger a webhook of interest (e.g., `orders/create`) to capture a valid raw body `B` and its Shopify-computed header `X-Shopify-Hmac-Sha256: H`.
2. Send a POST to the app's webhook endpoint with body `B` unmodified, header `X-Shopify-Hmac-Sha256: H` unmodified, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request [6](#0-5) ; `HmacValidator.validate` returns `true` because it only hashes `B` [7](#0-6) .
4. `Registry.process` calls the registered handler with `WebhookMetadata` claiming `shop: "victim-shop.myshopify.com"` while the actual payload content is fully attacker-controlled [8](#0-7) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-20)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
```
