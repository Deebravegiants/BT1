### Title
Webhook `shop` identity is trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` extracts the tenant identity (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature verified by `ShopifyAPI::Webhooks::Registry.process` only covers the raw request body, never the header. Any actor who can produce one genuine, signature-valid `(raw_body, hmac)` pair for *any* shop (trivially obtainable by installing the target app on an attacker-owned store and receiving a real webhook) can replay that exact body/HMAC pair while swapping the `x-shopify-shop-domain` header to a victim shop. The signature check still passes, and the host application receives a `WebhookMetadata` claiming the body belongs to the victim shop.

### Finding Description
`Request#hmac` and `Request#to_signable_string` define the data that is HMAC-validated: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body` — no header, including `shop-domain`, participates in the signed content. Yet `Request#shop` (the tenant identity used downstream) is read straight from the unauthenticated header: [3](#0-2) 

`Registry.process` verifies the HMAC and then immediately trusts `request.shop` as the tenant for the handler callback, with no additional binding check between the verified body and the header-derived shop: [4](#0-3) 

The `HmacValidator.validate` call only proves `hmac == HMAC(secret, raw_body)`; it says nothing about which shop that body came from: [5](#0-4) 

This breaks the intended identity binding:
`HMAC-valid(raw_body) ⇏ shop-domain header == shop that actually produced raw_body`

Because Shopify computes the webhook HMAC using the app's shared `client_secret` over the body alone (this is Shopify's own documented behavior and is correctly replicated here), the header is the only carrier of tenant identity, and this gem does not bind it to anything cryptographically.

### Impact Explanation
An unprivileged internet user can install the vulnerable app on their own Shopify store (or trial/development store) — an action requiring no special privileges, tokens, or leaked secrets. By triggering a real event (e.g., `orders/create`) on their own store, they legitimately receive a `(raw_body, x-shopify-hmac-sha256)` pair that is valid under the app's `client_secret`. Replaying that exact body+HMAC to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain passes `Registry.process`'s HMAC check unchanged, and the host application's registered handler is invoked with `WebhookMetadata#shop` pointing at the victim tenant while the body content is attacker-controlled (from the attacker's own store's event). Any host application that uses `WebhookMetadata#shop` to select which tenant's data to create/update/delete (the documented purpose of that field) will apply attacker-influenced data under the victim's tenant — i.e., cross-tenant access, listed as a Critical impact in scope.

### Likelihood Explanation
Likelihood is high: no credentials, access tokens, or `client_secret` knowledge are required. The only prerequisite is the ability to install the target app on an attacker-controlled shop (a completely standard, self-service action) and the ability to send an arbitrary HTTP POST to the app's public webhook endpoint (which by design must be internet-reachable to receive Shopify's webhooks). No timing constraints or race conditions are needed — the captured `(body, hmac)` pair remains valid indefinitely for the life of the client secret.

### Recommendation
Bind the verified request body to the claimed shop, e.g.:
- Require the host application to independently verify that the `shop` in `WebhookMetadata` corresponds to a shop that has an active session/installation and is expected to send this specific webhook (defense already recommended in Shopify's docs but not enforced here), and/or
- Include the shop domain as part of the value verified by `HmacValidator` for webhooks (e.g., derive/verify shop from body payload fields where Shopify includes them, or require the host framework to cross-check `request.shop` against its own installation records before trusting `WebhookMetadata#shop`), and
- Document explicitly in this gem that `Request#shop` is **not** cryptographically bound by the HMAC check and must not be treated as authenticated on its own.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the vulnerable app.
# 1. Attacker triggers e.g. an orders/create event on their own store and captures the
#    raw POST body and the "x-shopify-hmac-sha256" header sent by Shopify to the app's
#    webhook endpoint. This HMAC is valid because it is computed over raw_body with the
#    app's shared client_secret (Shopify-side behavior, faithfully replicated here).

raw_body = captured_raw_body        # from attacker's own store's genuine webhook
hmac     = captured_hmac_header      # valid HMAC over raw_body

# 2. Attacker POSTs the exact same body+HMAC to the app's public webhook endpoint,
#    but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic"       => "orders/create",
  "x-shopify-hmac-sha256" => hmac,                       # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com" # attacker-controlled, unsigned
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)

# 3. Registry.process succeeds because HmacValidator only checks raw_body:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_body, ...))
# The host app's handler now believes attacker-controlled data belongs to the victim shop.
``` [6](#0-5) [4](#0-3)

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
