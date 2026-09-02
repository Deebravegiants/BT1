### Title
Webhook `shop-domain` header trusted without HMAC binding, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw body bytes, then hands the handler a `WebhookMetadata` struct whose `shop` field is taken directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header. The header is never included in the signed material, so the identity binding "HMAC-verified bytes == the shop attributed to this webhook" does not hold.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, and `Request#shop` is read straight from a header: [1](#0-0) [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC-SHA256(client_secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — it never incorporates `shop`: [3](#0-2) 

`Registry.process` validates the HMAC and then constructs `WebhookMetadata` using `request.shop` as the tenant identifier passed to the app's handler, with no cross-check that the shop is the one that actually produced/owns the signed body: [4](#0-3) 

Because the `client_secret`-based HMAC secret is shared across every shop that installs a given app (it is not per-shop), any unprivileged attacker who legitimately installs the target app on their own shop will receive genuinely-signed webhook deliveries for their own shop. The HMAC only proves "this body byte-string was signed by Shopify/this app's secret" — it says nothing about which shop the payload belongs to. An attacker can therefore replay that same signed body to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` will call the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled content>, ...)`. This breaks the equality the gem implicitly promises to consumers: `HMAC-authenticated payload == payload legitimately produced for WebhookMetadata#shop`.

### Impact Explanation
Any application logic that uses `WebhookMetadata#shop` to select which merchant's data to update, invalidate, or act upon (a standard and expected usage pattern, since this is the only shop-scoping field the gem exposes to webhook handlers) can be tricked into applying attacker-controlled webhook content under a victim tenant's identity. Depending on the handler (e.g., `app/uninstalled`, `orders/create`, `customers/data_request` handling), this can lead to cross-tenant data corruption, false uninstall/redact triggers against a victim shop, or state confusion between tenants — meeting the "cross-tenant access" bar.

### Likelihood Explanation
Requires only an unprivileged attacker who can install the target Shopify app onto their own (attacker-owned) store — a normal, low-privilege action — after which they can capture legitimately-signed webhook traffic for their own shop and replay it directly to the app's public webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or victim credentials are needed.

### Recommendation
Have `Utils::HmacValidator`/`Webhooks::Request` incorporate the shop domain (and/or other trust-relevant headers) into the signed material check, or otherwise have `Registry.process` cross-validate that the `shop-domain` header corresponds to a shop with an active, known installation/session before trusting it, rather than passing the raw header value straight into `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is not itself HMAC-authenticated and must not be used as a sole tenant-authorization key without additional verification (e.g., confirming a stored session exists for that shop before acting).

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com`, so the app's HMAC secret is shared and valid for their traffic.
2. Attacker triggers/receives a legitimate webhook delivery (e.g. `orders/create`) — captures the raw body and its valid `x-shopify-hmac-sha256` signature.
3. Attacker POSTs this exact body + valid HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) passes because it only checks body bytes against the shared secret.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's own order data>, ...)`, causing the app to process attacker-supplied content as if it originated from the victim shop. [5](#0-4) [4](#0-3) [6](#0-5)

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
