### Title
Webhook `shop` domain is trusted from an unsigned header while the HMAC only covers the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` attribute (the tenant identifier passed to app webhook handlers) that is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. This breaks the identity binding `shop signed by HMAC == shop trusted by handler`: the `shop` field is acted upon (passed to every webhook handler as the tenant context) without being covered by the HMAC that authenticates the request.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `Request#shop` is derived purely from a header that is not part of the signed material: [2](#0-1) 

`Utils::HmacValidator.validate` verifies `compute_signature(verifiable_query.to_signable_string, secret)` against the received `hmac`, i.e. it only authenticates the bytes of the body: [3](#0-2) 

`Registry.process` performs this HMAC check and then immediately forwards `request.shop` (the unauthenticated header value) to the app's webhook handler as the tenant identity, with no additional cross-check that the shop belongs to the signed body or to any known/expected shop: [4](#0-3) 

Because the HMAC is computed only over the body, the header (topic, shop-domain, webhook-id, api-version) can be freely modified without invalidating the signature, as long as the body bytes are unchanged. An unprivileged internet user who installs the app on their own store receives genuinely signed webhooks for that store (a valid HMAC over a body they fully control/observe). They can then replay that exact body with the same valid HMAC to the app's webhook endpoint while swapping the `x-shopify-shop-domain` header to a victim shop's domain. `Registry.process` will accept the request (`Utils::HmacValidator.validate` only checks the body/HMAC pair, which is unchanged) and hand the attacker-controlled body to the handler tagged with the victim's shop, breaking the equality `shop authenticated by HMAC == shop the handler trusts`.

### Impact Explanation
This is a cross-tenant identity confusion: the webhook handler receives attacker-supplied body content attributed to an arbitrary victim shop domain, without Shopify or the gem ever validating that the shop and the signed payload belong together. Any host application that uses `WebhookMetadata#shop` to key persistence, trigger per-tenant side effects, or select which merchant's access token/session to act with is exposed to cross-tenant data or action injection purely from a request whose only cryptographic guarantee is "the body wasn't tampered with by someone without the secret" — not "this body belongs to this shop."

### Likelihood Explanation
Requires an attacker to control at least one shop that has legitimately installed the app (a normal, unprivileged action) to obtain one validly-signed webhook body/HMAC pair, then replay it against the app's public webhook endpoint with a different `shop-domain` header. No access to `client_secret`, access tokens, or any privileged account is needed.

### Recommendation
Bind the shop domain into the signed material or otherwise verify it independently of the header, e.g. include the `shop-domain` header in the HMAC computation, or require the caller to reconcile `request.shop` against the destination endpoint/shop context (e.g. per-shop webhook endpoints) rather than trusting the header value outright before invoking handlers in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-shop-domain: attacker.myshopify.com`, valid `x-shopify-hmac-sha256` computed over `B`.
2. Attacker resends the identical body `B` and identical HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the new headers/body successfully.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` which recomputes the HMAC over `@raw_body` (unchanged) and matches the unchanged HMAC header — validation passes.
5. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop == "victim.myshopify.com"`, even though nothing about `victim.myshopify.com` was ever verified by the signature. [4](#0-3) [5](#0-4) [6](#0-5)

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
