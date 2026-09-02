### Title
Webhook shop identity is not bound to the HMAC signature, allowing shop spoofing on replayed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC signature computed by `Utils::HmacValidator` only covers the raw request body, never the shop header. `Registry.process` trusts `request.shop` to build the `WebhookMetadata` passed to the host app's handler once `Utils::HmacValidator.validate(request)` succeeds. Since the shop identity is not part of what is authenticated, a request whose body+HMAC pair is valid for one shop can be replayed with an arbitrary `shop-domain` header value and will still pass validation, letting the caller dictate which tenant the payload is attributed to.

### Finding Description
- `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `Request#shop` is derived purely from an unauthenticated header, independent of the signed payload: [2](#0-1) 
- `HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e. the body) and compares it to the received HMAC — no shop or header data is part of the signed material: [3](#0-2) 
- `Registry.process` gates entirely on this HMAC check and then forwards `request.shop` (the unauthenticated header value) directly into `WebhookMetadata`, which the host application's handler uses to determine which merchant/tenant the webhook belongs to: [4](#0-3) 

The identity binding that should hold is: `shop-that-Shopify-signed-for == shop-attributed-to-the-processed-webhook`. Because the shop header is outside the HMAC's scope, this equality is not enforced by the gem — the HMAC only proves "the body bytes were signed by someone holding `api_secret_key`", not "this body belongs to shop X".

### Impact Explanation
This crosses a tenant boundary (cross-tenant confusion), which is explicitly in-scope as a Critical-class impact: an attacker who can obtain any single legitimately-signed `(raw_body, hmac)` pair (e.g. by owning their own trial/dev shop and installing the same app, thereby receiving genuinely-signed webhook deliveries from Shopify) can replay that exact body to the app's webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `Utils::HmacValidator.validate` still returns `true` (the body/HMAC pair is untouched), and `Registry.process` will hand the host app a `WebhookMetadata` claiming the payload originated from the victim shop. Any host application logic that keys off `data.shop` (e.g. to look up per-shop state, load a session/access token for that shop, or attribute the payload to that merchant) can be manipulated into acting on attacker-controlled data under the guise of a different tenant.

### Likelihood Explanation
The prerequisite is only possession of one valid `(body, hmac)` pair, which is trivially obtainable by any developer/attacker who installs the app on their own (even free/trial) shop — no privileged credentials, access tokens, or `api_secret_key` are required. The rest is a straightforward header-spoofed HTTP replay against the app's public webhook endpoint.

### Recommendation
Bind the shop identity into the signed material, or otherwise independently verify that the `shop-domain` header corresponds to the same tenant the payload was generated for — e.g. include the shop domain (and ideally topic/webhook-id) in `to_signable_string`, or require host applications to cross-check `request.shop` against an out-of-band trusted value (such as the session's shop) before trusting `WebhookMetadata#shop`. At minimum, document prominently that `request.shop` is unauthenticated and must not be used as a sole tenant-identification mechanism.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery from Shopify: raw body `B` with header `x-shopify-hmac-sha256: H` (valid because `HMAC-SHA256(api_secret_key, B) == H`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker crafts a new HTTP POST to the app's webhook endpoint reusing the identical body `B` and HMAC header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`; `Utils::HmacValidator.validate(request)` succeeds because it only checks `B`/`H` against `to_signable_string` (which is just `B`) — the shop header is never part of the check.
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and body `B`, even though `B` was never generated for `victim`, allowing the attacker to inject attacker-controlled webhook content attributed to an arbitrary tenant. [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
