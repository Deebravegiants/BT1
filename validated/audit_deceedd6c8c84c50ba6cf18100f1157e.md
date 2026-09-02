### Title
Webhook HMAC covers only the body, not the `shop-domain` header — cross-tenant webhook replay via header spoofing - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`Registry.process` verifies webhook authenticity purely with `Utils::HmacValidator.validate(request)`, which HMACs the raw body only [1](#0-0) . The `shop-domain` and `webhook-id` headers are never included in the signed content [2](#0-1) , so an attacker who legitimately received one signed webhook for their own shop can replay it with the `shop-domain` header rewritten to a victim shop and pass validation, causing `WebhookMetadata.shop` to be attributed to the victim.

### Finding Description
The intended binding is: `HMAC_valid(request) == true` should imply `request.shop == shop_that_generated(request.body)`. In this codebase that binding does not hold.

- `Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler with `request.shop` taken directly from the unsigned header: [3](#0-2) 
- `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` using the app's single `api_secret_key` (shared across every shop that installed the app): [4](#0-3) 
- `Request#to_signable_string` returns only `@raw_body`; none of `shop`, `topic`, or `webhook_id` (all read from unsigned HTTP headers) are part of the signed string: [5](#0-4) 

Because the API secret is shared across all shops of the app, any valid `(body, hmac)` pair the attacker legitimately receives for their own shop remains a valid `(body, hmac)` pair regardless of which `shop-domain`/`webhook-id` header accompanies it — those headers are never hashed. An attacker (who owns/installed their own dev shop) can:
1. Install the app on their own shop, trigger a webhook topic supported by the target app (e.g. `orders/create`), and capture the raw POST body plus the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Replay that exact body + HMAC to the app's webhook endpoint, but substitute `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Webhook-Id`) with the victim shop's domain.
3. `HmacValidator.validate` recomputes HMAC over the (unchanged) body and it matches, so `Registry.process` proceeds and calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop` == victim's domain [6](#0-5) .

No code path anywhere in `Registry`, `HmacValidator`, or `Request` cross-checks that the webhook's originating shop matches the `shop-domain` header, or that `webhook_id` is scoped to the shop asserted in the header — the "ownership" of `webhook_id`/`shop` is entirely attacker-controlled and unauthenticated.

### Impact Explanation
The host application receives a webhook body containing genuine Shopify-signed data (attacker's own shop's order/customer/etc. payload) but is told, via `WebhookMetadata.shop`, that it belongs to an arbitrary victim shop domain the attacker names. Any host app logic keyed off `WebhookMetadata.shop` (e.g., "look up tenant by shop, then upsert this order/customer/product data for that tenant", or GDPR `shop/redact` / `customers/redact` handling) will write, associate, or delete data under the wrong, victim tenant. This is a cross-tenant integrity/confidentiality break: repeatable against arbitrary victim shop domains (any known `*.myshopify.com` domain), for any topic the app has registered a handler for. This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
Preconditions are low-cost and match the stated attacker capability: create/install the app on a self-owned development shop, trigger any subscribed webhook topic, capture the legitimately signed callback, then send an HTTP replay with a rewritten `shop-domain` header. No `api_secret_key`, access token, or victim credentials are required. This is trivially repeatable for any topic and any target shop domain, limited only by the attacker knowing (or guessing) the victim's `myshopify.com` domain, which is commonly public/discoverable.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` in the signed content verified against Shopify's HMAC, or — since Shopify's actual HMAC only covers the raw body — perform an out-of-band authorization check binding the webhook to the shop: e.g., require that the app maintain a per-shop-scoped webhook secret, or verify that `webhook_id`/`shop` is one that was actually registered by *this* app for *this* shop (e.g., via a lookup) before dispatching to the handler in `Registry.process`. At minimum, document/enforce that host apps must independently verify shop/session validity before trusting `WebhookMetadata.shop`, and add a check in `Registry.process` that the `shop` header corresponds to a shop with an active session/installation.

### Proof of Concept
```ruby
# test/webhooks/registry_shop_spoof_test.rb
require "test_helper"

class RegistryShopSpoofTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret",
      host_name: "example.com", api_version: "2023-01", is_embedded: true,
      is_private: false, scope: "read_products")
    @topic = "orders/create"
    @handled = nil
    handler = Class.new do
      define_singleton_method(:handle) { |data:| RegistryShopSpoofTest.class_variable_set(:@@last, data) }
    end
    ShopifyAPI::Webhooks::Registry.add_registration(topic: @topic, delivery_method: :http,
      path: "/webhooks", handler: handler)
  end

  def test_shop_domain_not_bound_to_hmac_or_webhook_id
    body = '{"id":1,"note":"attacker-shop-order"}'
    hmac = Base64.strict_encode64(
      OpenSSL::HMAC.digest("sha256", "secret", body)
    )

    # Legit request as attacker's own shop
    legit_request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: {
      "x-shopify-topic" => @topic,
      "x-shopify-hmac-sha256" => hmac,
      "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
      "x-shopify-webhook-id" => "attacker-webhook-id",
      "x-shopify-api-version" => "2023-01",
    })
    assert ShopifyAPI::Utils::HmacValidator.validate(legit_request)

    # Replayed body+hmac with victim's shop-domain header substituted
    spoofed_request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: {
      "x-shopify-topic" => @topic,
      "x-shopify-hmac-sha256" => hmac,
      "x-shopify-shop-domain" => "victim-shop.myshopify.com",
      "x-shopify-webhook-id" => "attacker-webhook-id",
      "x-shopify-api-version" => "2023-01",
    })

    # Binding under test: HMAC validity must imply shop == originating shop.
    # Assert both sides diverge: HMAC still validates, but shop differs from the
    # shop that actually produced/signed the body.
    assert ShopifyAPI::Utils::HmacValidator.validate(spoofed_request),
      "attacker-controlled shop-domain header still passes HMAC validation"
    refute_equal "attacker-shop.myshopify.com", spoofed_request.shop

    ShopifyAPI::Webhooks::Registry.process(spoofed_request)
    handled = self.class.class_variable_get(:@@last)
    assert_equal "victim-shop.myshopify.com", handled.shop,
      "handler received victim shop domain for data that originated from attacker's shop"
  end
end
```
This demonstrates: `HMAC_valid(spoofed_request) == true` while `spoofed_request.shop != actual_originating_shop`, and `Registry.process` dispatches to the handler with the attacker-chosen `shop` value — proving no code path in `Registry.process`/`HmacValidator` binds `webhook_id`/HMAC validity to the `shop-domain` header.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
