### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the HMAC signature over the raw request body only, while the `shop` attribute (taken from the unauthenticated `x-shopify-shop-domain` / `shopify-shop-domain` header) is passed unverified to the handler as tenant identity. Since a single app's `api_secret_key` is shared across every shop that installs the app, any merchant who receives a genuine webhook for their own store can replay that body+HMAC pair to the app's webhook endpoint while substituting a victim shop's domain in the `shop-domain` header, and `HmacValidator` will still accept it.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the request header without any cryptographic binding to the signature: [2](#0-1) 

`Registry.process` verifies only `Utils::HmacValidator.validate(request)`, which internally calls `compute_signature(verifiable_query.to_signable_string, secret)` — i.e. it HMACs the raw body, never the shop header — before handing `request.shop` straight into `WebhookMetadata` and the caller's handler: [3](#0-2) [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`HMAC-verified(raw_body)` == `shop attribute trusted by the handler as the tenant identity`

In reality, only `raw_body` is authenticated; `shop` (and `topic`, `webhook_id`, `api_version`) are attacker-controllable header values that are never part of the signed bytes. Because Shopify signs every merchant's webhooks for a given app with the *same* `api_secret_key`, this is not merely "the request came from Shopify" — it's "the request came from Shopify for *some* shop that has this app installed." Any such shop's operator can capture a legitimate webhook delivered to their own endpoint (valid body + valid HMAC) and re-POST it to the app's webhook controller with `x-shopify-shop-domain` rewritten to a different, victim shop. `HmacValidator.validate` will return `true` because it only checks that the body bytes were signed by the shared secret; it has no way to detect that the `shop` header was swapped.

The resulting `WebhookMetadata` (built in `Registry.process`) will carry `shop: request.shop` — the attacker-chosen value — for data that was never actually about that shop: [5](#0-4) 

Any host application that follows the gem's own documented pattern of using `data.shop` to key lookups/writes (e.g. to load the correct merchant's offline session before acting on the payload) will act as if the forged victim shop sent that body — a cross-tenant data-confusion primitive fully caused by this gem's signature computation not covering the header it hands out as authenticated tenant identity.

### Impact Explanation
This is a scope/identity-binding bypass that lets one authenticated tenant (a shop with an app installed) forge a webhook body appearing to originate "for" another arbitrary shop, while still passing this gem's HMAC validation. Depending on what the host app does with `WebhookMetadata#shop` (commonly used to fetch that shop's offline access token/session and to write/update store-scoped records), this enables cross-tenant confusion or state corruption without ever needing the victim's credentials — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation only requires the attacker to control a shop that has the target app installed (a normal, unprivileged merchant capability), capture one of their own legitimate webhook deliveries (body + valid `x-shopify-hmac-sha256`), and replay it to the app's public webhook endpoint with a modified `x-shopify-shop-domain` header. No secrets, tokens, or privileged access are required, and the gem provides no mechanism (nonce, per-shop binding, timestamp+shop signed together) to prevent it.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) to the verified bytes, or otherwise cryptographically tie the header claims to the signature, e.g.:
- Include `shop-domain` (and `topic`) in the signable string used by `HmacValidator`, or
- Require host apps to independently confirm that `request.shop` corresponds to a shop with a currently valid installation/session before trusting it, and document this requirement prominently, or
- Reject/flag replay by tracking `webhook_id` uniqueness per shop combined with signature validation.

At minimum, `ShopifyAPI::Webhooks::Request#to_signable_string` should not present an interface where `hmac` "validates" a request whose `shop` field is entirely uncovered by that same HMAC.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint for `attacker.myshopify.com`:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of raw body under shared api_secret_key>
   x-shopify-shop-domain: attacker.myshopify.com
   { "id": 1, ... order payload ... }
   ```
3. Attacker replays the exact same raw body and `x-shopify-hmac-sha256` value, but changes the header:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only (per `Request#to_signable_string`) and it matches, so `Registry.process` proceeds and invokes the app's handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, even though Shopify never sent that payload for `victim.myshopify.com`. [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
