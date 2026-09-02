### Title
Webhook HMAC signs only the raw body, leaving `X-Shopify-Shop-Domain` and `X-Shopify-Topic` unauthenticated and blindly trusted by the documented `WebhookHandler` pattern — cross-tenant webhook relabeling - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb], [File: lib/shopify_api/utils/hmac_validator.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the raw JSON body via HMAC and then builds `WebhookMetadata` directly from unauthenticated headers (`shop-domain`, `topic`, `webhook-id`, `api-version`). Any party who can obtain one validly-signed webhook body (e.g., by installing the app on their own development shop) can replay that exact body with forged `shop-domain`/`topic` headers, and `Registry.process` will accept it and hand the relabeled `data.shop`/`data.topic` to the handler exactly as documented in `docs/usage/webhooks.md`.

### Finding Description
The claimed binding: `WebhookMetadata.shop == the shop value the HMAC authenticates` and `WebhookMetadata.topic == the topic value the HMAC authenticates`.

Tracing the code:
- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, never the headers: [1](#0-0) 
- `shop`, `topic`, `webhook_id`, `api_version` are all read straight from HTTP headers with no cryptographic tie to the signature: [2](#0-1) 
- `HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — i.e., it only ever authenticates the raw body: [3](#0-2) 
- `Registry.process` validates the HMAC, then constructs `WebhookMetadata` from `request.topic` and `request.shop` (the unauthenticated headers) and passes it straight to the handler: [4](#0-3) 
- The documented handler contract explicitly instructs apps to trust and act on `data.shop`/`data.topic` (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`), with no instruction or gem-provided mechanism to cross-check them against anything authenticated: [5](#0-4) 

Root cause: the signable string used for HMAC verification is body-only, so `shop`/`topic` are never bound to the signature. Because `Registry.process` uses these same unauthenticated header values to build the `WebhookMetadata` passed to the handler — the exact object the documented usage pattern is built to consume — any concrete handler implemented per the docs (`docs/usage/webhooks.md`) unconditionally treats attacker-controlled `shop`/`topic` values as if Shopify had vouched for them.

Attacker's exact request: an attacker installs the app on their own development shop, waits for (or triggers) a legitimate webhook delivery to their own registered endpoint (or, more directly, since HMAC is computed with the app's single shared `client_secret`, only the raw body and its HMAC are needed), then re-sends an HTTP POST to the app's webhook endpoint with:
- Body: the untouched, validly-signed raw JSON body.
- `X-Shopify-Hmac-Sha256`: the untouched, valid HMAC for that body.
- `X-Shopify-Shop-Domain`: rewritten to the victim's shop domain.
- `X-Shopify-Topic`: optionally rewritten to any registered topic.

`HmacValidator.validate` passes (it never looks at the headers), `Registry.process` finds a handler for the (attacker-chosen) topic, and calls `handler.handle(data: WebhookMetadata.new(topic: <attacker-chosen>, shop: <victim-domain>, ...))`.

Existing guards checked and found insufficient: `HmacValidator.validate` only covers the body (confirmed above); there is no `ShopValidator.sanitize!`, `state` comparison, or JWT `aud`/`dest` check anywhere in the webhook path (those apply only to OAuth/session-token flows, not webhooks); `Context.setup?`/`private?`/`embedded?` and Sorbet runtime typing only assert presence/shape of the fields, not their authenticity.

### Impact Explanation
Any handler written exactly per the gem's documented pattern will act on a `shop`/`topic` pair the gem never authenticated, allowing a malicious app-installer to make the host application believe an event occurred for an arbitrary victim shop (cross-tenant confusion) while supplying a body from their own store. Depending on what the handler does with `data.shop` (e.g., look up per-shop session/access token to react to the "event," write to per-shop records, trigger data-request/redact jobs, or use the shop as a cache/tenant key), this can lead to actions being taken against, or data being associated with, a merchant tenant the attacker does not control — a cross-tenant impact. This is repeatable against arbitrary victim shop domains (any string satisfying `shopify-shop-domain`) for every future signed payload the attacker can obtain from their own shop.

### Likelihood Explanation
Preconditions are minimal and entirely within the described unprivileged attacker's capability: create a free/development Shopify store, install the target app on it (a normal, permitted action), and receive at least one genuine webhook delivery (or trigger one). No `api_secret_key`, access token, or any privileged credential is required — only the ability to capture one's own legitimate webhook body+signature and re-POST it with altered headers to the app's public webhook endpoint. This is cheap, fully attacker-controlled, and repeatable indefinitely.

### Recommendation
Bind `shop` and `topic` (and ideally `webhook_id`) into the signed material, or otherwise authenticate them independently of the raw body header values — e.g., verify the `shop-domain` header against a shop that is provably registered/known to the app (such as an existing session record) before constructing `WebhookMetadata`, and/or refuse to honor a `topic` header that doesn't match the actual registered callback path for that topic. At minimum, document prominently that `data.shop`/`data.topic` are NOT authenticated by the HMAC and must not be trusted as tenant identifiers without additional verification.

### Proof of Concept
```ruby
# test/webhooks/registry_shop_relabel_test.rb
require "test_helper"

class RegistryShopRelabelTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", host: "host",
      scope: "scope", is_embedded: false, api_version: "2024-01",
      is_private: false,
    )
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_documented_handler_receives_relabeled_metadata_after_valid_hmac
    received = nil

    # Handler implemented exactly per docs/usage/webhooks.md
    handler_module = Module.new do
      extend ShopifyAPI::Webhooks::WebhookHandler
      define_singleton_method(:handle) do |data:|
        received = data # e.g. perform_later(topic: data.topic, shop_domain: data.shop, ...)
      end
    end

    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", path: "callback/orders/create",
      delivery_method: :http, handler: handler_module,
    )

    raw_body = '{"id":1}' # attacker's own legitimately-received payload
    valid_hmac = Base64.encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", raw_body),
    ).strip

    forged_headers = {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => valid_hmac,       # still valid: HMAC only covers raw_body
      "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-forged
      "x-shopify-webhook-id" => "attacker-chosen-id",
      "x-shopify-api-version" => "2024-01",
    }

    request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

    # Binding check BEFORE: HMAC(secret, raw_body) authenticates only raw_body,
    # never "victim-shop.myshopify.com" or the topic string.
    ShopifyAPI::Webhooks::Registry.process(request) # does not raise InvalidWebhookError

    # Binding check AFTER: documented handler received the forged shop as if authenticated.
    assert_equal("victim-shop.myshopify.com", received.shop)
    assert_equal("orders/create", received.topic)
  end
end
```
Both assertions demonstrate that the gem accepts the header-forged request as validly signed and that the documented handler pattern (`data.shop`, `data.topic`) receives attacker-relabeled values, confirming the binding `shop/topic acted on == shop/topic authenticated (none)` is broken in the gem's own documented usage path, not caller misuse.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-23)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
```
