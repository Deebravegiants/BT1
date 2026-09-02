The docs explicitly state (`docs/usage/webhooks.md:125`) that `Registry.process` "will verify the request did indeed come from Shopify" — i.e., the gem documents `shop` in `WebhookMetadata` as a trusted, verified field the host app can key its per-tenant logic on. That confirms this is a genuine gem-level guarantee failure, not a host-app misuse of an undocumented API.

### Title
Webhook HMAC does not bind the `shop-domain` header, enabling cross-tenant webhook forgery/replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity solely via `Utils::HmacValidator.validate(request)`, which validates the HMAC over the raw body only. The `shop` (and `topic`) values used to route and authorize per-tenant handling are taken directly from unauthenticated HTTP headers and are never included in the signed bytes.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) are pulled from HTTP headers, not from the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` passed to the app's handler, with no additional binding check between the signed body and these header fields: [3](#0-2) 

`HmacValidator.validate_signature` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — again, only over the body: [4](#0-3) 

The identity binding that should hold is:
`HMAC-verified bytes == bytes that determine tenant (shop) and event semantics (topic) acted upon by the handler`

Here that equality is broken: the HMAC only covers `raw_body`, while `shop`/`topic`, the values the host app uses to attribute the event to a specific merchant/tenant (as the gem's own documentation states — `docs/usage/webhooks.md:125` — "This will verify the request did indeed come from Shopify"), come from headers outside the signed scope.

Because a single app's `client_secret` is shared across every shop that installs it, any two webhook deliveries for the same app produce HMACs keyed with the same secret, differing only by body content. This means the HMAC signature does **not** bind a delivery to a particular shop. A party who legitimately receives a real, validly-signed webhook for their own shop (e.g. an `orders/create` webhook from their own store) can capture that exact `raw_body` + `x-shopify-hmac-sha256` pair and replay it against the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop that also uses the same app. `HmacValidator.validate` will still pass (body and signature are unmodified and mutually valid), and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: <victim-shop>` together with the attacker's own body content.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged user of the same third-party app (a legitimate merchant on their own store) can forge webhook deliveries that the app implicitly attributes to a different merchant/tenant, injecting attacker-controlled body data under another shop's identity. Any host application that follows the gem's documented pattern (using `data.shop` from `WebhookMetadata` to select the tenant record to update/act on) is vulnerable to cross-tenant data injection/corruption purely through crafted HTTP headers, without ever needing the app's `client_secret` or any shop's access token.

### Likelihood Explanation
Exploitation requires: (1) the attacker installs/uses the vulnerable app on at least one shop they control (to obtain one legitimately signed `(body, hmac)` pair, or, more simply, to observe that HMAC only covers body and craft/replay accordingly), and (2) sends an HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header. No credentials, tokens, or `client_secret` access are needed — only network access to the endpoint and one genuine webhook capture. This is realistically reachable by any unprivileged internet user who is also a customer/merchant of the same multi-tenant app.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`/`api_version`) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop domain to the signed body before it is trusted for tenant attribution — e.g., include the shop domain in `to_signable_string`, or require the host app to independently confirm the shop against a session/webhook-id record before acting. At minimum, update `ShopifyAPI::Webhooks::Request` so `Registry.process`/`HmacValidator.validate` fail if the tenant-identifying header cannot be shown to correspond to the specific signed delivery, rather than only asserting the body was signed by *some* holder of the shared app secret.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the exact `raw_body` and the `x-shopify-hmac-sha256` header Shopify sends.
2. Attacker sends a POST to the same app's webhook endpoint with:
   - Body: the captured `raw_body` (unmodified)
   - `x-shopify-hmac-sha256`: the captured, valid signature (unmodified)
   - `x-shopify-shop-domain`: `victim-shop.myshopify.com` (rewritten)
   - `x-shopify-topic`: unchanged or attacker-chosen registered topic
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, raw_body)` and finds it matches the (unmodified, still-valid) signature — validation succeeds.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's original body>, ...)`, causing the host app to act on attacker-controlled data as if it were emitted by `victim-shop.myshopify.com`. [3](#0-2) [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
