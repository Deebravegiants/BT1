### Title
Webhook HMAC covers only the raw body, not `shop-domain`/`topic` headers, letting a validly-signed webhook be replayed against arbitrary tenants/topics - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Utils::HmacValidator.validate` is the single authenticity check used for both OAuth callbacks and webhooks, and it only verifies that the HMAC matches the string returned by `to_signable_string`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0)  while `request.shop` and `request.topic` are read straight from attacker-suppliable HTTP headers [2](#0-1)  and are trusted downstream by `Registry.process` after only the HMAC-over-body check passes [3](#0-2) . This breaks the SIGNATURE COVERAGE invariant: `shop` and `topic` are acted on downstream but are outside the string that was actually verified.

### Finding Description
The binding that must hold is: `value_used_downstream ⊆ value_verified_by_HmacValidator`, i.e. every field passed to `handler.handle` must be contained inside `verifiable_query.to_signable_string`.

Trace:
1. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)` [4](#0-3) .
2. `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received `hmac` header [5](#0-4) .
3. For `Webhooks::Request`, `to_signable_string` is exactly `@raw_body` [1](#0-0) . The `hmac` itself is likewise derived only from the `shopify-hmac-sha256` header, decoupled from `shop`, `topic`, `api-version`, `webhook-id` [6](#0-5) .
4. After `validate` returns true, `Registry.process` immediately uses `request.topic` to look up a handler and `request.shop`/`request.topic` to build `WebhookMetadata` handed to the app's handler [7](#0-6) . Neither value was inside the signed string.

Because Shopify computes the webhook HMAC over the body only, any body that Shopify has ever signed for the attacker's own shop (which the attacker legitimately receives, since they can register their own webhook endpoint on their own dev shop) remains validly signed no matter what `shop-domain` or `topic` header value is attached to a later replayed HTTP request. The attacker's exact request: capture one genuine webhook (raw body + `X-Shopify-Hmac-Sha256` header) sent to their own endpoint, then POST that identical body and hmac header to the victim app's webhook endpoint with `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) rewritten to a value of the attacker's choosing. `HmacValidator.validate` still returns `true` because it never inspected those headers, and `Registry.process` dispatches to the handler with the forged `shop`/`topic`, i.e. authenticity (Shopify signed *this body*) is conflated with authorization (this body was destined for *this shop/topic*).

None of the existing guards catch this: `HmacValidator.validate` only checks the body hash; `Registry.process` has no separate check tying the header-derived `shop`/`topic` to the signed payload; there is no shop allowlist or session lookup gating webhook dispatch in this code path.

By contrast, `Auth::Oauth::AuthQuery#to_signable_string` does include `code`, `host`, `shop`, `state`, `timestamp` [8](#0-7) , so the OAuth callback path does not have this specific gap — the vulnerability is isolated to the webhook path.

Regarding the `old_api_secret_key` whitespace angle raised in the question: `Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?` does not treat a whitespace-only string as empty [9](#0-8) , so a whitespace secret triggers a second `validate_signature` attempt with that literal string as the HMAC key. This does not itself grant a forgery capability to an unprivileged attacker (the attacker still has no signing capability and `secure_compare` still requires an exact match) — it is a latent oddity, not a demonstrable bypass, and is not needed to exploit the header/body coverage gap described above.

### Impact Explanation
An unprivileged attacker who installs the app on their own development shop and registers a webhook receives one or more genuinely-signed webhook bodies. They can replay that exact body/hmac pair against the same app's webhook endpoint with a forged `shop-domain` header claiming to be any other merchant, or a forged `topic` header claiming a different event type. `Registry.process` will accept it as authentic and dispatch `WebhookMetadata` carrying the forged `shop`/`topic` to the app's handler [10](#0-9) . If the host app trusts `WebhookMetadata#shop`/`#topic` to select which tenant's data to update or which side effect to trigger (the documented and expected usage of this gem), this is a cross-tenant confusion / authentication-bypass primitive: data or actions intended for shop A can be triggered under an arbitrary spoofed shop identity, repeatable for every webhook the attacker has ever legitimately received. This matches "Critical - authentication bypass" and "cross-tenant access" categories.

### Likelihood Explanation
Preconditions are minimal and fully within the stated attacker capabilities: attacker needs only their own dev shop, their own registered webhook endpoint, and network access to the target app's public webhook endpoint. No secret material, access token, or victim cooperation is required. The attack is cheap (one captured request, replay with modified headers) and repeatable indefinitely and against any topic/shop string the attacker chooses.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the value that is cryptographically bound to the signature before trusting them, e.g. bind the request's HMAC verification to a canonicalized string containing both the header values and the body (or re-verify shop/topic against an out-of-band trusted registration, such as the shop associated with the session/install that Shopify's Admin API confirms), rather than trusting header values whose provenance was never covered by `to_signable_string`. At minimum, document and enforce that `Registry.process` cross-checks `request.shop` against a known/installed shop list before dispatching.

### Proof of Concept
```ruby
# test/webhooks/registry_signature_coverage_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Webhooks
    class RegistrySignatureCoverageTest < Test::Unit::TestCase
      def setup
        super
        @body = '{"id":1,"note":"hello"}'
        @hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, @body)
        @hmac_b64 = Base64.strict_encode64(@hmac)
      end

      def test_shop_and_topic_are_not_covered_by_signature
        genuine_headers = {
          "x-shopify-hmac-sha256" => @hmac_b64,
          "x-shopify-topic" => "orders/create",
          "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
          "x-shopify-api-version" => "2024-01",
          "x-shopify-webhook-id" => "1",
        }
        forged_headers = genuine_headers.merge(
          "x-shopify-shop-domain" => "victim-shop.myshopify.com",
          "x-shopify-topic" => "shop/redact", # different topic too
        )

        genuine = ShopifyAPI::Webhooks::Request.new(raw_body: @body, headers: genuine_headers)
        forged  = ShopifyAPI::Webhooks::Request.new(raw_body: @body, headers: forged_headers)

        # Binding under test: signable string must equal the value acted on.
        assert_equal(genuine.to_signable_string, forged.to_signable_string, "body unchanged")
        refute_equal(genuine.shop, forged.shop, "shop header differs")

        # Both pass authenticity because HMAC only covers @raw_body.
        assert(ShopifyAPI::Utils::HmacValidator.validate(genuine))
        assert(ShopifyAPI::Utils::HmacValidator.validate(forged))

        # forged.shop ("victim-shop...") is now trusted downstream despite
        # never having been part of the signed string.
        assert_equal("victim-shop.myshopify.com", forged.shop)
        refute(forged.to_signable_string.include?(forged.shop))
      end
    end
  end
end
```
This demonstrates that `HmacValidator.validate` accepts the forged request (`assert(... .validate(forged))`) while `forged.shop`/`forged.topic` — the values `Registry.process` hands to the app's webhook handler — are outside `to_signable_string` and freely attacker-controlled, proving the SIGNATURE COVERAGE break.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
```ruby
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L16-21)
```ruby
          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
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
