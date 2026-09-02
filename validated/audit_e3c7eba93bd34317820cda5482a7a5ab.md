## Title
Webhook HMAC only covers `@raw_body`; `topic`/`shop`/`api_version`/`webhook_id` are read from unsigned headers and trusted by handlers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::HmacValidator.validate` verifies only that `raw_body` matches a signature computed with the app's shared `api_secret_key`; it never binds that signature to the `shopify-topic`, `shopify-shop-domain`, `shopify-api-version`, or `shopify-webhook-id` headers. `Webhooks::Registry.process` and `WebhookMetadata` then trust those headers verbatim to decide which handler runs and which shop's data it acts on.

### Finding Description
The claimed binding, stated as an equality, is: `bytes_passed_to_compute_signature == bytes_that_determine_topic_and_shop_used_by_the_handler`. Tracing the code shows this equality does not hold:

- `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes/compares the signature exclusively over that string with `Context.api_secret_key` (or `old_api_secret_key`) [2](#0-1) .
- `Request#topic`, `#shop`, `#api_version`, and `#webhook_id` are all read straight from `@headers` via `shopify_header`, with no cross-check against the body or the signature [3](#0-2) [4](#0-3) .
- `Registry.process` validates only the HMAC, then dispatches by `request.topic` and builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` directly from those unverified header values [5](#0-4) .
- `WebhookMetadata` is a plain `T::Struct` with `shop` as a `String`, carrying no provenance or verification flag [6](#0-5) .

Root cause: `api_secret_key` is the app's client secret, shared across every merchant that installs the app — it is not shop-specific. Any unprivileged attacker who installs the app on their own development shop will legitimately receive webhooks whose HMAC is valid under that same shared secret. Because the HMAC only signs `raw_body` and never the headers, the attacker can take a genuinely-signed `(raw_body, hmac)` pair from their own shop's webhook and POST it directly to the app's webhook endpoint with a different `shopify-shop-domain` header (e.g. the victim's domain) and/or a different `shopify-topic` header. `Request#hmac` yields the same value regardless of which header string carries the topic/shop, and `HmacValidator.validate` accepts the (unchanged) body+signature pair unconditionally of the header content — confirming the fast-validation check in the question. `Registry.process` then calls the handler registered for the attacker-chosen `topic` and hands it `WebhookMetadata#shop` equal to the attacker-chosen shop string, even though the actual signed content (`raw_body`) came from, and was only ever signed for, the attacker's own shop's event.

None of the existing guards prevent this: `HmacValidator.validate` only checks body-vs-signature identity, never headers; there is no `ShopValidator.sanitize!` or equivalent call anywhere in the webhook path; there is no comparison between a shop domain embedded in the body and the header-supplied `shop-domain`; Sorbet's `T.cast`/`String` typing only enforces type, not authenticity of the header value.

### Impact Explanation
A host app that uses `WebhookMetadata#shop` (as `Registry.process` explicitly hands it to `WebhookHandler#handle`) to decide which shop's records to read, update, or delete will act on attacker-supplied body content while attributing it to an attacker-chosen shop identifier. This is a cross-tenant data-integrity/read issue: the attacker's own genuinely-signed event data can be replayed with a forged `shopify-shop-domain` (or `shopify-topic`) header, causing the host application to write/process data under a victim merchant's shop key, or to route data through the handler for a topic it wasn't actually issued for. This matches the Critical "cross-tenant access" class: one shop's request (the attacker's own signed webhook) ends up mutating or being processed against another merchant's shop-keyed state.

### Likelihood Explanation
Preconditions: the attacker needs a genuinely signed `(raw_body, hmac)` pair, which they can trivially obtain by installing the app on their own (free) development shop and triggering any webhook-eligible event (e.g., placing a test order). They need network access to the app's webhook receiving endpoint (typically a public URL, since Shopify must reach it) — no secret, token, or credential is required. They then send an ordinary HTTP POST with attacker-chosen headers and the captured body/signature. This is trivially repeatable against any victim shop identifier the attacker chooses to type into the header, and against any topic the app has registered a handler for, as long as the attacker can obtain at least one valid `(body, hmac)` for that topic from their own shop.

### Recommendation
Bind the signed payload to the header values that are trusted downstream: either include `topic`, `shop-domain`, `api-version`, and `webhook-id` in the string passed to `compute_signature`/`to_signable_string` (matching what the host verifies), or independently verify `shop` against a per-shop-registered secret/session before constructing `WebhookMetadata`, and reject webhooks whose `topic` doesn't match the topic the handler was registered under an authenticated channel. At minimum, document and enforce that `WebhookMetadata#shop`/`#topic` must never be trusted for tenant-scoping decisions unless corroborated by a value that is itself covered by the HMAC.

### Proof of Concept
```ruby
# test/webhooks/request_topic_shop_forgery_test.rb
require "test_helper"

class WebhookHeaderForgeryTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", api_version: "2022-01",
      host_name: "app.example.com", scope: "read_products", is_private: false,
      is_embedded: true, session_storage: ShopifyAPI::Auth::FileSessionStorage.new,
    )
  end

  def test_same_body_different_shop_and_topic_headers_both_validate
    raw_body = '{"id":1,"note":"attacker-owned order"}'
    hmac = OpenSSL::HMAC.base64digest(OpenSSL::Digest.new("sha256"), "secret", raw_body)

    headers_attacker_shop = {
      "shopify-topic" => "orders/create",
      "shopify-hmac-sha256" => hmac,
      "shopify-shop-domain" => "attacker-shop.myshopify.com",
      "shopify-api-version" => "2022-01",
      "shopify-webhook-id" => "1",
    }
    headers_victim_shop = {
      "shopify-topic" => "customers/update", # different topic
      "shopify-hmac-sha256" => hmac,          # identical signature
      "shopify-shop-domain" => "victim-shop.myshopify.com", # forged shop
      "shopify-api-version" => "2022-01",
      "shopify-webhook-id" => "1",
    }

    req_attacker = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers_attacker_shop)
    req_victim = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers_victim_shop)

    # BYTE IDENTITY: same signed bytes -> same hmac value
    assert_equal req_attacker.hmac, req_victim.hmac

    # Both pass validation despite completely different topic/shop headers
    assert ShopifyAPI::Utils::HmacValidator.validate(req_attacker)
    assert ShopifyAPI::Utils::HmacValidator.validate(req_victim)

    # Divergence: shop/topic used by the handler differ even though signed bytes are identical
    assert_equal "attacker-shop.myshopify.com", req_attacker.shop
    assert_equal "victim-shop.myshopify.com", req_victim.shop
    assert_not_equal req_attacker.topic, req_victim.topic
  end
end
```
This demonstrates that `Request#hmac`/`HmacValidator.validate` cannot distinguish the two header sets, while `Request#topic` and `Request#shop` — consumed by `Registry.process` to select the handler and populate `WebhookMetadata#shop` — diverge freely, breaking the byte-identity binding claimed in the question.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
