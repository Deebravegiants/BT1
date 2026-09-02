### Title
Webhook shop attribution is unauthenticated — `Webhooks::Request#shop` is not covered by the HMAC signature, unlike `Auth::Oauth::AuthQuery#shop` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in the signed string, so tampering the `shop` query param on an OAuth callback invalidates the HMAC. `Webhooks::Request#to_signable_string` returns only `@raw_body`, so the `shop-domain` header used for tenant routing is never covered by the signature, letting an attacker replay a validly-signed webhook body with a forged `shop-domain` header.

### Finding Description
The binding that should hold identically on both paths is: `HMAC_valid(request) == true` implies `shop_used_downstream == shop_that_was_actually_signed_for`.

- `AuthQuery#to_signable_string` builds `URI.encode_www_form({code:, host:, shop:, state:, timestamp:})` [1](#0-0)  — `shop` is part of the signed payload, so `HmacValidator.validate_signature` [2](#0-1)  will fail if `shop` is mutated.
- `Webhooks::Request#to_signable_string` returns `@raw_body` only, while `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header via `shopify_header` [3](#0-2) . The same `HmacValidator.validate` is reused for both `VerifiableQuery` implementers [4](#0-3) , but since `to_signable_string` never touches headers, the `shop-domain` header can be changed freely without breaking `OpenSSL.secure_compare(computed_signature, received_signature)`.
- `Webhooks::Registry.process` validates only the body HMAC, then immediately trusts `request.shop` to build `WebhookMetadata` and dispatch to the app's handler, with no secondary check against a known/installed shop list: [5](#0-4) .

Attacker exploit flow: the attacker creates their own development shop, installs the app, and registers their own webhook endpoint (per the stated preconditions). Shopify delivers a legitimately-signed webhook (`raw_body`, `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker-shop.myshopify.com`) to the attacker's server. The attacker then forwards the identical `raw_body`/HMAC pair to the target app's shared webhook endpoint, but rewrites the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to `victim-shop.myshopify.com`. Because `to_signable_string` never includes the header, `HmacValidator.validate` still returns `true`, and `Registry.process` calls the app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` carrying the attacker's payload/body — cross-tenant data injection.

Neither `ShopValidator.sanitize!`, `state` comparisons, `JwtPayload`'s `aud` check, nor `Context.setup?/private?/embedded?` intervene in this path; those guard OAuth/session-token flows, not `Webhooks::Registry.process`. Sorbet's `sig` typing only enforces that `shop` is a `String`, not that it is authenticated.

### Impact Explanation
The app's webhook processing pipeline (`Registry.process` → `handler.handle`) receives an attacker-chosen `shop` value alongside a real, signature-valid body. Any per-shop side effect the host app performs based on `WebhookMetadata#shop` (e.g., writing order/customer data keyed by shop, updating per-tenant state, invalidating another merchant's cache) can be attributed to a shop the attacker never controls. This is repeatable for every webhook topic the attacker's own shop can trigger, and the blast radius spans any shop the attacker chooses to spoof in the header, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Preconditions are fully met by an unprivileged attacker: creating a development shop, installing the app, and registering a webhook endpoint are all self-service actions requiring no secrets. The attacker doesn't need `api_secret_key`; they only need one real, validly-signed webhook delivered to their own endpoint, which they can trivially obtain by triggering events (e.g., placing a test order) in their own shop. Forging the header and replaying the request to the app's shared webhook URL costs a single HTTP request. This is directly and repeatably exploitable, assuming the host app trusts `request.shop`/`WebhookMetadata#shop` for tenant routing, as the gem's own `Registry.process` does with no additional check.

### Recommendation
Do not treat `shop-domain` (or any other webhook header) as authenticated. At minimum:
- Document prominently that `Webhooks::Request#shop` is unauthenticated and must be cross-checked by the host app against its own installed-shop registry before use.
- Optionally, extend `Registry.process` to require the caller to supply/verify an expected shop (e.g., matched via `webhook_id` registered per shop) rather than blindly trusting the header.
- Consider including relevant headers in a canonical signable representation if a future webhook delivery format supports it, to bring parity with `AuthQuery`.

### Proof of Concept
```ruby
# test/utils/hmac_validator_asymmetry_test.rb
require "test_helper"

module ShopifyAPITest
  module Utils
    class HmacAsymmetryTest < Test::Unit::TestCase
      def test_auth_query_hmac_breaks_when_shop_is_tampered
        query = { code: "c", host: "h", shop: "real-shop.myshopify.com", state: "s", timestamp: "t" }
        valid_hmac = OpenSSL::HMAC.hexdigest(
          OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, URI.encode_www_form(query),
        )

        tampered = ShopifyAPI::Auth::Oauth::AuthQuery.new(
          code: query[:code], shop: "attacker-shop.myshopify.com", timestamp: query[:timestamp],
          state: query[:state], host: query[:host], hmac: valid_hmac,
        )

        refute(ShopifyAPI::Utils::HmacValidator.validate(tampered))
      end

      def test_webhook_request_hmac_survives_shop_domain_tampering
        raw_body = '{"id":1}'
        hmac = Digest.hexencode(
          OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body),
        )

        forged_headers = {
          "x-shopify-topic" => "orders/create",
          "x-shopify-hmac-sha256" => Base64.encode64(
            OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body),
          ),
          # attacker rewrites the shop-domain header claiming a different shop
          "x-shopify-shop-domain" => "victim-shop.myshopify.com",
        }

        request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

        # HMAC still validates even though shop was changed post-signing
        assert(ShopifyAPI::Utils::HmacValidator.validate(request))
        assert_equal("victim-shop.myshopify.com", request.shop)
      end
    end
  end
end
```
This contrasts `AuthQuery` (HMAC breaks under `shop` tampering) with `Webhooks::Request` (HMAC survives `shop-domain` tampering), pinpointing `lib/shopify_api/webhooks/request.rb`'s `to_signable_string` as the vulnerable code.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
