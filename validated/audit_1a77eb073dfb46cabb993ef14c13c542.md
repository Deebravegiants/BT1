### Title
Webhook `Request.to_signable_string` signs only the raw body, letting an attacker replay their own valid HMAC with forged `shop`/`topic` headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`HmacValidator.validate_signature` (`lib/shopify_api/utils/hmac_validator.rb:27-31`) only ever checks `OpenSSL.secure_compare` over the value returned by `verifiable_query.to_signable_string`. For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns `@raw_body` alone [1](#0-0) , while `Registry.process` dispatches the handler using `request.topic` and `request.shop`, both parsed straight from attacker-controlled HTTP headers and never covered by the signature [2](#0-1) [3](#0-2) . The `old_api_secret_key` fallback in `HmacValidator.validate` is a documented, intended secret-rotation feature and does not change or worsen this coverage gap — the same divergence exists whether the current or old secret is used.

### Finding Description
The invariant "every value acted on downstream is inside the string handed to `HmacValidator`" is broken for webhooks. The equality that should hold is:
`to_signable_string(request) ⊇ {request.shop, request.topic, request.webhook_id, request.api_version}`
but in fact `to_signable_string` for `Webhooks::Request` equals only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from HTTP headers via `shopify_header` [4](#0-3)  and are never part of the HMAC computation.

`compute_signature`/`validate_signature` compute `HMAC(secret, raw_body)` and compare it against the `hmac-sha256` header [5](#0-4) . This means the signature authenticates the body bytes only — it says nothing about which shop or which topic that body was originally sent for. `api_secret_key` (and `old_api_secret_key`) are single, app-wide secrets, not per-shop secrets, so any legitimately-received webhook (for the attacker's own development shop, obtained per the threat model's explicit "receive their own validly signed webhooks" allowance) yields a `(raw_body, hmac)` pair that is valid under the app's secret regardless of which shop it was originally addressed to.

Exploit flow:
1. Attacker installs the app on their own shop and registers a webhook, receiving a legitimate `(raw_body=B, x-shopify-hmac-sha256=H, x-shopify-shop-domain=attacker-shop, x-shopify-topic=T)` request, where `H = HMAC(api_secret_key, B)`.
2. Attacker replays this exact `B` and `H` to the app's public webhook endpoint, but with the `x-shopify-shop-domain` header changed to `victim-shop.myshopify.com` and/or `x-shopify-topic` changed to another registered topic (e.g. `shop/redact`).
3. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares it to `H` via `to_signable_string` — this still matches because `B` and `H` are unchanged [6](#0-5) .
4. The check passes, and the handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` using the forged header values [7](#0-6) .

No guard in this gem catches the divergence: `HmacValidator.validate` only checks the raw body [8](#0-7) ; there is no `ShopValidator.sanitize!` call anywhere in `Registry.process` or `Request`; there is no comparison of `request.shop` against any session or cookie state; Sorbet typing only enforces `String` type, not provenance or integrity.

By contrast, `AuthQuery#to_signable_string` (used for OAuth callback validation) does include every field acted upon — `code`, `host`, `shop`, `state`, `timestamp` — so the OAuth path does not exhibit this gap [9](#0-8) .

### Impact Explanation
An attacker who owns a legitimate development-shop install can forge the `shop-domain` and `topic` headers on a webhook delivery to the shared app endpoint and have the app process it as if it came from an arbitrary victim shop and topic, while the HMAC check still reports success. This is a cross-tenant authentication bypass: the app's webhook handler is invoked with attacker-chosen `shop` and `topic` values (and attacker-chosen body content), potentially triggering shop-scoped side effects (data changes, mandatory compliance webhooks like `shop/redact`/`customers/redact`, business logic keyed off shop identity) attributed to a shop the attacker does not control. This is repeatable at will for any victim shop domain the attacker can guess/know (shop domains are not secret) and matches the "cross-tenant access" / "authentication bypass" Critical category.

### Likelihood Explanation
Preconditions: the app must process webhooks through `ShopifyAPI::Webhooks::Registry.process` / `Request`, which is the documented usage pattern for this gem. Attacker cost is low — install the app on a self-owned dev shop (a normal, permitted action), capture one legitimate webhook delivery, then replay it with modified headers directly against the app's publicly reachable webhook endpoint. This requires no possession of `api_secret_key`/`old_api_secret_key`, no TLS interception, and no privileged access — fully within the stated attacker model. The `old_api_secret_key` fallback window itself does not add or reduce likelihood; it is orthogonal to this specific header/body coverage gap.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, and ideally `webhook_id`) in the value passed to the HMAC comparison, or independently authenticate/bind them (e.g., verify `shop-domain` against a known/registered shop list per topic before dispatch), so that `to_signable_string` (or an equivalent check) covers every field that `Registry.process`/`WebhookMetadata` acts upon.

### Proof of Concept
```ruby
# test/webhooks/request_forged_headers_test.rb (minitest, no live shop)
require_relative "../test_helper"

class ForgedWebhookHeaderTest < Test::Unit::TestCase
  def setup
    super
    @body = '{"id":1}'
    @secret = ShopifyAPI::Context.api_secret_key
    @hmac_b64 = Base64.strict_encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), @secret, @body)
    )
  end

  def test_signature_ignores_shop_and_topic_headers
    request_own_shop = ShopifyAPI::Webhooks::Request.new(
      raw_body: @body,
      headers: {
        "x-shopify-hmac-sha256" => @hmac_b64,
        "x-shopify-topic" => "orders/create",
        "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
      },
    )
    request_forged_victim = ShopifyAPI::Webhooks::Request.new(
      raw_body: @body,
      headers: {
        "x-shopify-hmac-sha256" => @hmac_b64, # same H, same B
        "x-shopify-topic" => "shop/redact",         # forged
        "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
      },
    )

    # Binding under test: to_signable_string is identical for both,
    # so both validate identically, even though shop/topic differ.
    assert_equal(request_own_shop.to_signable_string, request_forged_victim.to_signable_string)
    assert(ShopifyAPI::Utils::HmacValidator.validate(request_own_shop))
    assert(ShopifyAPI::Utils::HmacValidator.validate(request_forged_victim)) # passes despite forged shop/topic

    assert_equal("victim-shop.myshopify.com", request_forged_victim.shop)
    assert_equal("shop/redact", request_forged_victim.topic)
  end

  def test_validate_false_for_empty_hmac_and_wrong_length_digest
    request_empty = ShopifyAPI::Webhooks::Request.new(
      raw_body: @body,
      headers: {
        "x-shopify-hmac-sha256" => "",
        "x-shopify-topic" => "orders/create",
        "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
      },
    )
    refute(ShopifyAPI::Utils::HmacValidator.validate(request_empty))

    request_wrong_length = ShopifyAPI::Webhooks::Request.new(
      raw_body: @body,
      headers: {
        "x-shopify-hmac-sha256" => Base64.strict_encode64("short"),
        "x-shopify-topic" => "orders/create",
        "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
      },
    )
    refute(ShopifyAPI::Utils::HmacValidator.validate(request_wrong_length))
  end
end
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
