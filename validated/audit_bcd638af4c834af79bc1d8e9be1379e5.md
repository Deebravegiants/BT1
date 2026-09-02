### Title
Webhook `shop` is taken unauthenticated from `X-Shopify-Shop-Domain` header, never covered by HMAC verification - (File: lib/shopify_api/webhooks/registry.rb)

### Summary
`Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) validates a webhook solely via `Utils::HmacValidator.validate(request)`, which only checks the HMAC over the raw request body (`to_signable_string`/`@raw_body`). It never inspects `request.shop`. The `shop` value passed into `WebhookMetadata.new` at line 198 comes straight from the unsigned `X-Shopify-Shop-Domain` header, so the binding "shop authenticated by `HmacValidator.validate` == shop passed to `WebhookMetadata`" does not hold.

### Finding Description
Binding claimed: `HmacValidator.validate(request) authenticates request.shop`. In fact:

- `Utils::HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb:13-22) only calls `verifiable_query.hmac` and `verifiable_query.to_signable_string`.
- `Webhooks::Request#to_signable_string` returns `@raw_body` only (lib/shopify_api/webhooks/request.rb:36-38); `#hmac` reads the `X-Shopify-Hmac-Sha256` header (lib/shopify_api/webhooks/request.rb:10-13).
- `Webhooks::Request#shop` is read independently from the `X-Shopify-Shop-Domain` / `x-shopify-shop-domain` header (lib/shopify_api/webhooks/request.rb:20-23) and is **not** part of the signable string, so it is never covered by the HMAC computed over `@raw_body`.
- `Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) does: `raise ... unless Utils::HmacValidator.validate(request)`, then unconditionally builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` and hands it to the app's `handler.handle`. There is no lookup that ties the shop-domain header to the specific `webhook_id`, to the signing secret, or to any Shopify-side registration record.

Because the app's `api_secret_key` (and `old_api_secret_key`) is a single shared secret for the whole app across all installed shops, a valid HMAC only proves "this body+hmac pair was produced by someone holding the app's client secret" (i.e., genuinely by Shopify for *some* installation of the app) — it proves nothing about *which* shop the request is for. The shop attribution rides entirely on an attacker-controlled, unsigned HTTP header.

Exploit flow (no TLS interception, no secrets needed):
1. Attacker creates their own development shop, installs the app, and registers a webhook (e.g., `products/update`) pointing at their own server, exactly as permitted by the threat model.
2. Shopify delivers a legitimately HMAC-signed webhook to the attacker's server: body = attacker-controlled shop data, `X-Shopify-Hmac-Sha256` = valid signature over that body computed with the app's real (shared) secret, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker takes that exact `body` + `X-Shopify-Hmac-Sha256` value (unchanged, so HMAC still validates) and replays it directly to the app's public webhook endpoint, but rewrites only `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Webhook-Id`) to a victim shop's domain.
4. `Registry.process` calls `HmacValidator.validate`, which passes (body+hmac untouched), then constructs `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-crafted body, and invokes the app's registered handler as if this were an authentic event for the victim shop.

No existing guard prevents this: `HmacValidator.validate` never touches `shop`; `Registry.process` performs no additional per-shop check against `webhook_id`, a session, or a Shopify API confirmation; there is no Sorbet runtime check enforcing the binding (types only constrain that `shop` is a `String`, not that it matches an authenticated value).

### Impact Explanation
Any app handler that trusts `WebhookMetadata#shop` as an authenticated tenant identifier (the documented/expected use, e.g. to look up a per-shop session/access token or to write/delete tenant data keyed by shop) can be made to act on attacker-supplied body content while believing it originates from an arbitrary victim shop. This is cross-tenant access/data confusion: an unprivileged attacker can inject fabricated events (or trigger `shop/redact`/`customers/redact`-style handlers, since `process` does not exclude mandatory topics) attributed to any shop domain of their choosing, repeatable against arbitrary victim shop domains with no rate limiting on shop value guessing (shop domains are often public/discoverable via the storefront). This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
- Precondition: the app must, per the gem's own documented design, use `WebhookMetadata#shop` to identify the tenant for the webhook (this is the intended/only way the gem communicates shop identity to handlers).
- Attacker cost is low: register a webhook on their own dev shop (or observe the shape of any topic's payload/HMAC scheme, which is fixed and public), capture one legitimate delivery, replay it with a modified header to the app's fixed, single webhook endpoint URL.
- No secret, token, or privileged access is required; only the ability to receive one's own valid webhook and re-send an HTTP request with a different header value.

### Recommendation
Do not trust `request.shop` as authenticated identity data. Either:
1. Include the shop domain (and webhook id) inside the HMAC-signed signable string/body verification scope, or
2. Cross-validate `request.shop` against an independently-verified source (e.g., look up the webhook by `request.webhook_id` via the Admin API using a session already known to belong to that shop, or maintain a persisted mapping from `webhook_id`/subscription to shop established at registration time via `Registry.register`), before passing `shop` into `WebhookMetadata`.

### Proof of Concept
```ruby
# test/webhooks/registry_shop_spoof_test.rb
require "test_helper"

class RegistryShopSpoofTest < Minitest::Test
  def test_hmac_validator_never_reads_shop
    request = ShopifyAPI::Webhooks::Request.new(
      raw_body: '{"id":1}',
      headers: {
        "x-shopify-topic" => "products/update",
        "x-shopify-hmac-sha256" => "irrelevant",
        "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
      },
    )

    # Instrument the request object: if #shop is ever called during validate, fail the test.
    request.define_singleton_method(:shop) { raise "shop must never be read by HmacValidator" }

    ShopifyAPI::Utils::HmacValidator.stub(:validate_signature, true) do
      ShopifyAPI::Utils::HmacValidator.validate(request) # must not raise
    end
  end

  def test_process_trusts_unsigned_shop_header
    handled = nil
    handler = Class.new do
      define_method(:handle) { |data:| handled = data }
    end.new

    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "products/update", delivery_method: :http, path: "/wh", handler: handler,
    )

    request = ShopifyAPI::Webhooks::Request.new(
      raw_body: '{"attacker":"controlled"}',
      headers: {
        "x-shopify-topic" => "products/update",
        "x-shopify-hmac-sha256" => "sig",
        "x-shopify-shop-domain" => "victim-shop.myshopify.com", # spoofed, unsigned
        "x-shopify-webhook-id" => "123",
        "x-shopify-api-version" => "2024-01",
      },
    )

    ShopifyAPI::Utils::HmacValidator.stub(:validate, true) do
      ShopifyAPI::Webhooks::Registry.process(request)
    end

    assert_equal "victim-shop.myshopify.com", handled.shop # attacker fully controls this
  ensure
    ShopifyAPI::Webhooks::Registry.clear
  end
end
```
Both sides of the claimed binding — `HmacValidator.validate` result and `request.shop` used in `WebhookMetadata` — are shown to be independent: the validator never inspects `shop`, and `process` still forwards whatever `shop` header value was supplied. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
