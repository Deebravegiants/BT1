I have enough evidence to finalize the analysis.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking that `Utils::HmacValidator.validate` succeeds against the raw request body. The `shop` value that is handed to the app's webhook handler as the authoritative tenant identifier is read from the `x-shopify-shop-domain` header, which is never included in the signed bytes. This breaks the intended binding `hmac_verified(body) == shop_trusted(header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived independently from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header, with no cryptographic tie to the signed body: [2](#0-1) 

`Registry.process` verifies the HMAC and then, if valid, immediately trusts `request.shop` to build the `WebhookMetadata` object passed to the app's handler: [3](#0-2) 

The HMAC computation itself uses only the body bytes as the signable string, with the secret being the app's `api_secret_key` (or `old_api_secret_key`): [4](#0-3) 

Because the signature covers only the body, any request with a body+HMAC pair that is valid for *some* shop (e.g. one legitimately generated for the attacker's own connected shop) remains valid if replayed with a different `x-shopify-shop-domain` header. The gem's own documentation states the `process` call "will verify the request did indeed come from Shopify," implying full authenticity of the request, but in fact only the body is authenticated — the shop attribution is not.

### Impact Explanation
This crosses a tenant boundary: an attacker who controls a shop connected to the app (or who otherwise obtains one valid body/HMAC pair, e.g. by triggering webhooks on their own shop) can cause the host application to process that body as if it originated from an arbitrary victim shop, simply by changing the `shop-domain` header. Since `data.shop` is the field host applications use to select per-tenant session/state (as shown in the gem's own webhook usage documentation, `docs/usage/webhooks.md`, where `shop_domain: data.shop` is used to route/queue work), this enables cross-tenant data injection/impersonation — writing or triggering actions attributed to a shop the attacker does not control. This matches the "cross-tenant access" criterion for a Critical-impact finding.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one legitimately-signed webhook body (trivial for any merchant/developer that installs the app on their own shop and observes webhook traffic to their own endpoint, since Shopify sends real webhooks signed with the app's shared secret for actions the attacker fully controls). Replaying that body with a modified shop header requires no secret knowledge, no privileged access to Shopify, and no interaction with the app owner. This is straightforward for anyone who has connected the app to a shop they control — an "unprivileged internet user" relative to other tenants' data.

### Recommendation
Bind the shop domain into what is cryptographically verified. Either:
- Include the `x-shopify-shop-domain` header value in `to_signable_string` so it is covered by the HMAC (this deviates from Shopify's actual webhook signing scheme, so likely not viable), or
- Require the gem/host application to independently validate `request.shop` against known/registered shops for the app before trusting it, and document clearly that `Registry.process` only authenticates the body, not the shop attribution, so integrators do not conflate "HMAC valid" with "shop value trustworthy."
- At minimum, update `docs/usage/webhooks.md` and the `Registry.process` contract to explicitly state that the `shop` field is unauthenticated and must not be used for tenant/session selection without additional verification (e.g., matching against a session that was independently established via OAuth/token exchange).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they control) and legitimately triggers a webhook, e.g. `orders/create`. Shopify sends a POST to the app's webhook endpoint with:
   - `x-shopify-hmac-sha256: <valid HMAC of RAW_BODY using the app's api_secret_key>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `RAW_BODY` (attacker-controlled contents, since it's their own shop's order).
2. Attacker captures `RAW_BODY` and the valid `x-shopify-hmac-sha256` value.
3. Attacker (or anyone who can reach the app's public webhook endpoint) resends the exact same `RAW_BODY` and HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers/body, `HmacValidator.validate` succeeds because it only checks `RAW_BODY` against the HMAC, and `Registry.process` invokes the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` and attacker-controlled `body`, even though this data never legitimately came from `victim-shop`. [3](#0-2) [5](#0-4)

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
