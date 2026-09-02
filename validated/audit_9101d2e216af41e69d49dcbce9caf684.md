## Finding

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (tenant identifier) is read from an unauthenticated HTTP header and passed straight through to the host application's webhook handler. Any actor who can obtain one genuinely-signed `(raw_body, hmac)` pair for a topic can replay it to the app's public webhook endpoint with a forged `shop-domain`/`x-shopify-shop-domain` header pointing at a different, victim tenant, and `ShopifyAPI::Webhooks::Registry.process` will accept it as valid and dispatch it under the victim shop's identity.

### Finding Description
`Request#hmac` and `Request#to_signable_string` define what bytes are protected by the signature: [1](#0-0) 
`to_signable_string` returns only `@raw_body` — the `shop-domain` header used by `Request#shop` is never mixed into the signed material.

`Utils::HmacValidator.validate` verifies exactly that signable string against the app's secret: [2](#0-1) 

`Webhooks::Registry.process` then trusts `request.shop` — the unauthenticated header — as the tenant key handed to the app's own handler: [3](#0-2) 

This is the same class of bug as the referenced report: a field that is acted upon (here, the shop/tenant identity used to route webhook data) is not covered by the integrity check that is meant to authenticate the request (the HMAC), even though the check passes. Contrast this with the OAuth callback path, where `Auth::Oauth::AuthQuery#to_signable_string` explicitly folds `shop` into the signed parameters, correctly binding shop identity to the signature: [4](#0-3) 

The equality that should hold is:
`shop authenticated by HMAC == shop used as the tenant key for webhook dispatch`

In the webhook path this equality is broken: `shop authenticated by HMAC` is undefined (shop isn't part of the signed bytes at all), while `shop used as tenant key` = `request.shop` (raw header).

### Impact Explanation
Any merchant who has installed the app is a legitimate but unprivileged party with respect to other tenants of the same app. Such a merchant can trigger a real event in their own store (e.g., create an order) to receive a genuinely Shopify-signed webhook `(raw_body, hmac)` for their own shop. Because the signature never binds to the shop domain, that same `(raw_body, hmac)` pair remains valid when POSTed directly to the app's public webhook endpoint with the `shop-domain` header rewritten to any other shop that has installed the app (a "victim" tenant). `Registry.process` will pass HMAC validation and call the app's handler with `shop: <victim>` and the attacker-controlled body/topic. Any host-application logic that keys state changes, side effects, or access-token lookups off this `shop` value can be manipulated into acting on/for a shop the attacker does not control — i.e., cross-tenant access/data injection using another tenant's identity, without needing that tenant's access token, `client_secret`, or credentials.

### Likelihood Explanation
Exploitation requires no privileged access: the attacker only needs to be able to install the app in one shop (or otherwise obtain one valid webhook body/HMAC pair for any topic under the app) and know or guess a target shop's `myshopify.com` domain, which is often discoverable or guessable. No secrets need to be known or leaked. The only work is a header substitution and a direct HTTP POST to the publicly reachable webhook endpoint, making this practically exploitable by any unprivileged internet user who has app access to one tenant.

### Recommendation
Bind the tenant identity into the authenticated material for webhooks, e.g. by:
- Including the `shop-domain` (and `topic`/`webhook-id`) values in the bytes verified by `Utils::HmacValidator` for webhook requests (mirroring how `AuthQuery#to_signable_string` binds `shop` for OAuth), or
- Cross-checking `request.shop` against the shop associated with the currently registered/known session for that webhook subscription before dispatching to the handler, rejecting mismatches.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers any event delivering webhook topic `orders/create`, capturing the raw POST body and the `x-shopify-hmac-sha256` header value sent by Shopify (this pair is validly signed with the app's secret for the attacker's own body).
2. Attacker crafts a new POST to the app's webhook endpoint using the identical raw body and `x-shopify-hmac-sha256` value, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
3. `Webhooks::Request.new(raw_body:, headers:)` parses this; `Utils::HmacValidator.validate(request)` succeeds because it only checks `OpenSSL::HMAC.hexdigest(..., secret, raw_body)`, which is unchanged.
4. `Webhooks::Registry.process(request)` calls the registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, causing the app to process attacker-controlled data under the victim shop's tenant context. [5](#0-4) [3](#0-2)

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
