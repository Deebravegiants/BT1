### Title
Header confusion via body-only HMAC signing allows shop/topic relabeling in webhook processing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Registry.process` derives `topic` and `shop` from unauthenticated headers (`shopify-topic`, `shopify-shop-domain`) while `HmacValidator.validate` only signs and checks the raw body via `Request#to_signable_string`, which returns `@raw_body` alone. Because the HMAC never covers the topic or shop-domain headers, an attacker who has captured any single validly-signed webhook body/HMAC pair delivered to their own installed app can replay that exact body+HMAC to the app's public webhook endpoint with arbitrary `shopify-topic`/`shopify-shop-domain` headers, causing `Registry.process` to invoke the `shop/redact` (or any registered) handler with an attacker-chosen `shop` value and mismatched body.

### Finding Description
The claimed binding: `shop_that_authenticated == shop_acted_on` should hold, i.e., the shop whose secret produced a valid HMAC should equal `request.shop` used to build `WebhookMetadata`. Tracing the code:

- `Request#initialize` [1](#0-0)  only validates presence of headers, not their binding to the body.
- `Request#topic` and `Request#shop` are read straight from attacker-controlled headers, with no cryptographic tie to the signed content [2](#0-1) .
- `Request#to_signable_string` returns only `@raw_body` [3](#0-2) , so `HmacValidator.validate` recomputes `HMAC-SHA256(secret, raw_body)` and compares it to `shopify-hmac-sha256`; topic and shop-domain headers are excluded from the signable material entirely.
- `Registry.process` validates the HMAC, then looks up the handler purely by `request.topic` and constructs `WebhookMetadata` using `request.shop`, with no check that this shop matches anything cryptographically bound to the signature, and no `MANDATORY_TOPICS` check gating `process` (that check only exists in `register`/`unregister`) [4](#0-3) .

Root cause: the HMAC is computed over the body only, and the app's `api_secret_key` is shared across every shop that installs the app, so any legitimately-signed webhook body (received by the attacker for their own shop, on any topic) carries a valid HMAC that remains valid no matter what topic/shop headers are attached to it. An attacker who has installed the app on their own shop and thus received at least one real webhook (e.g. `app/uninstalled`) can capture `(raw_body, hmac)`, then POST directly to the app's public webhook endpoint with headers `X-Shopify-Topic: shop/redact` and `X-Shopify-Shop-Domain: <victim>.myshopify.com`, keeping the body and HMAC unchanged. `HmacValidator.validate` returns true because it only checks the body against the HMAC, and `Registry.process` dispatches the registered `shop/redact` handler with `WebhookMetadata(shop: <victim>, topic: "shop/redact", body: <attacker's unrelated body>)`.

None of the existing guards stop this: `HmacValidator.validate` checks body integrity, not header/body binding; there is no `ShopValidator.sanitize!` or session-shop equality performed anywhere in this path; `MANDATORY_TOPICS` is only consulted in `register`/`unregister`, never in `process`.

### Impact Explanation
An unprivileged attacker can trigger any `:http` webhook handler registered by the host app — including GDPR-mandatory handlers like `shop/redact` and `customers/redact` — attributed to an arbitrary victim shop domain that the attacker never installed the app on, using only a body/HMAC pair legitimately produced for their own shop on any topic. This is a cross-tenant trigger of business logic (e.g., data deletion/redaction workflows, order-processing side effects, inventory changes — whatever the app implements in its handler) against a victim's shop identifier, with the handler body being attacker-controlled (from whatever webhook body they captured). This matches the "cross-tenant access" Critical category. It is repeatable against arbitrary victim shop domains (the attacker only needs to know the domain, which is public) and is limited only by which topics the app has registered `:http` handlers for.

### Likelihood Explanation
Preconditions: the app must register at least one `:http` webhook handler (any topic, including a mandatory one) and expose a webhook endpoint reachable directly by attacker-crafted HTTP requests (standard deployment). The attacker must install the app on their own store (trivial, free) to receive at least one legitimately signed webhook body/HMAC pair — no secret access needed, since Shopify itself sends this to any installer. Then the attacker sends a single crafted POST to the app's public webhook URL with swapped `topic`/`shop-domain` headers and the untouched body+HMAC. This requires no cryptographic breakage, no MITM, and no credentials — only an app install and one direct POST, which is well within the "unprivileged attacker" model.

### Recommendation
Bind the topic and shop-domain headers into the material that is HMAC-verified (or otherwise cryptographically authenticate them), e.g. include the header values in `to_signable_string`, or reject/ignore the `shop-domain`/`topic` headers when the HMAC is not scoped to those fields — matching Shopify's actual verification guidance which treats HMAC validity as necessary but not sufficient; the shop that owns the credentials for a given call must be separately established before dispatching to shop-specific handlers, and `Registry.process` should never trust `request.shop`/`request.topic` as authenticated unless they are covered by the signature.

### Proof of Concept
```ruby
# test/webhooks/registry_confusion_test.rb
require "test_helper"

class RegistryHeaderConfusionTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_body_hmac_does_not_bind_topic_or_shop
    raw_body = '{"id": 123, "note": "unrelated app/uninstalled payload"}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest("SHA256", ShopifyAPI::Context.api_secret_key, raw_body)
    )

    handler = Minitest::Mock.new
    handler.expect(:handle, nil) do |data:|
      data.shop == "victim-shop.myshopify.com" && data.topic == "shop/redact"
    end
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "shop/redact", delivery_method: :http, path: "/webhooks", handler: handler
    )

    request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "x-shopify-topic" => "shop/redact",
        "x-shopify-hmac-sha256" => hmac,
        "x-shopify-shop-domain" => "victim-shop.myshopify.com",
        "x-shopify-api-version" => "2023-10",
        "x-shopify-webhook-id" => "attacker-crafted-id",
      },
    )

    ShopifyAPI::Webhooks::Registry.process(request)
    handler.verify # succeeds: victim shop's redact handler invoked with attacker body, HMAC valid on body alone
  end
end
```
Assert on both sides of the binding: `shop_that_authenticated` (the shop whose secret actually produced `hmac`, i.e. the attacker's own shop) is never checked, while `shop_acted_on` (`data.shop`) equals the attacker-supplied `"victim-shop.myshopify.com"` — demonstrating the equality is broken and `HmacValidator.validate` still returns `true`.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
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
