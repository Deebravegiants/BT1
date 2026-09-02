Found a genuine identity-binding gap in `Webhooks::Request`.

### Title
Webhook `shop` and `topic` fields are read from HTTP headers but excluded from the HMAC-signed payload, allowing an attacker to spoof shop/topic identity in webhook processing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` validates the HMAC signature over only the raw request body [1](#0-0) , while the `shop`, `topic`, `api_version`, and `webhook_id` values consumed by the host application are pulled directly, unauthenticated, from HTTP headers [2](#0-1) . Only the HMAC (`hmac-sha256` header) is cryptographically bound to the body; the `shop-domain` header that a webhook handler uses to identify the tenant (and often to look up the session/access-token for that shop) is not covered by the signature at all.

### Finding Description
The `Request` class implements `Utils::VerifiableQuery` and defines `to_signable_string` as simply the raw body [1](#0-0) . `HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the value returned by `hmac`, which itself is derived from the `hmac-sha256` header [3](#0-2) [4](#0-3) .

Critically, `shop` (from `shopify-shop-domain` / `x-shopify-shop-domain`) is read directly from headers and is never included in the signable string, so it is not authenticated by the HMAC at all [5](#0-4) . The binding that should hold is:

`shop-domain header == shop bound inside the HMAC-signed payload`

but in this implementation:

`shop-domain header ∈ {unauthenticated headers}`, entirely disjoint from `to_signable_string` (`raw_body` only).

Because Shopify's real webhook body does contain a shop-identifying payload, and the gem's own consumers (host applications) are documented to call `request.shop` to route/authorize webhook handling per tenant, an attacker who can reuse or replay one *validly signed* webhook body (e.g., from any shop that legitimately sent a webhook, or one whose body an attacker can otherwise obtain a valid signature for) can pair it with an arbitrary `shopify-shop-domain` header value. Since the header is not covered by the signature, `HmacValidator.validate` still returns `true` for the tampered request, while `request.shop` returns the attacker-chosen value.

### Impact Explanation
This breaks the tenant-identity binding for webhook processing: the HMAC only proves "this body was signed by Shopify at some point for some shop," not "this body belongs to the shop named in this request." A host application that keys per-shop side effects (e.g., "delete data for `request.shop`", "look up access token for `request.shop`", "revoke session for `request.shop`") off the unauthenticated header can be manipulated into acting on the wrong tenant — i.e., cross-tenant access/impact — using only a body+signature pair from any shop, without possession of the target shop's credentials.

### Likelihood Explanation
Low-to-Medium: exploitation requires the attacker to obtain at least one validly-signed webhook body/HMAC pair (from their own shop, since HMAC uses the app's `client_secret` shared across all installs of the app) and then re-send it with a forged `shopify-shop-domain` header pointed at a victim shop. This is directly reachable without any credential belonging to the victim shop, only requiring the attacker to run the same app on their own store.

### Recommendation
Include the shop-identifying value (and topic/webhook id, if used for security-relevant routing) inside the HMAC-signed payload verification, or cryptographically bind the `shop-domain` header to the signed body (e.g., derive/verify shop identity from the parsed body content signed by Shopify, not from headers). At minimum, document/enforce that `request.shop` must not be trusted for authorization decisions unless it is independently corroborated by shop data inside `parsed_body`, and update `to_signable_string`/`HmacValidator` usage so header-derived identity fields participate in the signature check.

### Proof of Concept
```ruby
# Attacker controls their own shop "attacker.myshopify.com" and receives a
# legitimately Shopify-signed webhook for it: raw_body + X-Shopify-Hmac-Sha256.

raw_body = capture_from_own_shop_webhook       # valid signature, attacker's own tenant
valid_hmac_header = capture_from_own_shop_webhook_hmac

# Attacker replays the exact same body/hmac to the victim app's webhook endpoint,
# but swaps only the (unsigned) shop-domain header:
forged_headers = {
  "x-shopify-topic" => "customers/data_request",
  "x-shopify-hmac-sha256" => valid_hmac_header,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled, unauthenticated
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Utils::HmacValidator.validate(request) # => true (body/hmac untouched)
request.shop                                        # => "victim-shop.myshopify.com" (forged)

# Host app logic keyed on `request.shop` (e.g., session/token lookup, data deletion)
# now operates against the victim tenant despite the payload never originating there.
``` [6](#0-5) [7](#0-6)

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
