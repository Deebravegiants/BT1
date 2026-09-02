### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` identity that is subsequently handed to the host application's handler is read from an HTTP header that is never included in the signed bytes. This breaks the equality that the verification is supposed to establish: `bytes verified (raw_body) != bytes that determine tenant identity (shop-domain header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts the tenant identity from the `x-shopify-shop-domain` / `shopify-shop-domain` header: [1](#0-0) 

But `to_signable_string`, which is what `Utils::HmacValidator` uses to compute/verify the signature, returns only the raw body: [2](#0-1) 

`HmacValidator.validate` verifies `HMAC(api_secret_key, raw_body) == received_hmac`; it never touches the shop header: [3](#0-2) 

`Registry.process` uses this same validation and then constructs `WebhookMetadata` (passed to the host app's handler) using `request.shop`, which came from the unauthenticated header: [4](#0-3) 

`WebhookMetadata.shop` is documented as "The shop domain of the webhook" and the docs explicitly show host apps using it to key work by tenant (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`): [5](#0-4) 

Because `api_secret_key` is a single app-wide secret (not per-shop), and the HMAC only covers the body, **any valid `(raw_body, hmac)` pair obtained from a real webhook delivery for one shop remains valid for a request claiming to be from a different shop** — only the header is swapped. A malicious or unprivileged party who can install the app on their own store (a normal, unprivileged action) receives genuine webhook deliveries — each with a valid `X-Shopify-Hmac-Sha256` computed over the body using the app's shared secret. That attacker can then replay the same body+HMAC combination to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will accept it (it only checks the body against the secret), and `Registry.process` will invoke the handler with `data.shop` set to the victim's domain.

### Impact Explanation
This is a **cross-tenant identity-binding break**: the HMAC proves "this body was produced with knowledge of the app secret," but the gem lets an attacker attach that proof to an arbitrary tenant identity. Any host application that uses `WebhookMetadata#shop` to route/store data (which is the officially documented usage pattern) can be made to process attacker-supplied "verified" webhook data under another merchant's tenant context — e.g., writing forged order/product/app-uninstalled events into a victim shop's records, or triggering side effects (inventory sync, notification, data deletion on `app/uninstalled`) attributed to a shop the attacker does not own. This matches the Critical "cross-tenant access" impact category, since the attacker can only cross this boundary as a normal, unprivileged app installer rather than needing a leaked/privileged credential.

### Likelihood Explanation
Moderate-to-high: exploitation requires no special access — installing the target app on any shop (including a free/dev store) is standard, unprivileged behavior, and yields a legitimately signed webhook body/HMAC pair. The attacker then only needs to POST to the app's public webhook endpoint with a modified header, which any internet client can do; no interception of victim traffic or TLS access is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived identity to the signed body — e.g., include the shop domain in `to_signable_string`, or require the gem/host app to cross-check `request.shop` against the shop associated with the specific `webhook_id` via the Admin API before trusting it for tenant-sensitive operations. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be trusted for tenant identification without additional verification.

### Proof of Concept
1. App developer registers `WebhookHandler` that does `perform_later(shop_domain: data.shop, webhook: data.body)` (per the documented example).
2. Attacker installs the app on `attacker-shop.myshopify.com` and lets Shopify deliver a genuine webhook, capturing:
   - raw body `B`
   - header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's `api_secret_key`)
3. Attacker sends a POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this successfully (headers present) and `Utils::HmacValidator.validate` returns `true`, since it only checks `HMAC(secret, B) == H`, both unchanged.
5. `Registry.process` invokes the host handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: B, ...)`, causing the app to treat attacker-controlled data as though it originated from the victim's store. [6](#0-5) [7](#0-6)

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
