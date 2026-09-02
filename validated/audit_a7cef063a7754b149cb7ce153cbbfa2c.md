This confirms the vulnerability. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) computes the HMAC solely over `verifiable_query.to_signable_string`, and `Webhooks::Request#to_signable_string` returns only `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`). The `shop` value used downstream comes from `Webhooks::Request#shop`, which reads the `shop-domain` header directly and is never included in the signed payload (`lib/shopify_api/webhooks/request.rb:20-23`). `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) validates the HMAC, then builds `WebhookMetadata` using `request.shop` — an unauthenticated, attacker-controlled header — and dispatches it to the handler.

### Title
Webhook shop-domain header is not covered by HMAC, allowing cross-tenant shop-label forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`HmacValidator.validate` authenticates only `@raw_body` via `Webhooks::Request#to_signable_string`, never the `shop-domain` header. An attacker who owns a legitimate dev shop can capture one validly-signed webhook body/HMAC pair and replay it with a mutated `x-shopify-shop-domain` header pointing at a victim shop; `Registry.process` accepts the HMAC and dispatches `WebhookMetadata.new(shop: request.shop, ...)` to the handler with the forged shop label.

### Finding Description
The broken binding: `HMAC(secret, @raw_body) == received_hmac` is claimed to authenticate `WebhookMetadata.shop == shop-domain header`, but these are independent values. `to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) returns only `@raw_body`; the `shop` header is read separately by `Request#shop` (`lib/shopify_api/webhooks/request.rb:20-23`) and is not part of the signed string. `HmacValidator.validate_signature` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) computes `HMAC-SHA256(secret, to_signable_string)` and compares against `verifiable_query.hmac`, so it validates only that the body matches, not that the shop header is genuine.

`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) does:
```
raise ... unless Utils::HmacValidator.validate(request)
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
```
Since `request.shop` is taken from an unsigned header, an attacker who has captured one valid `(raw_body, hmac)` pair from Shopify for their own shop (a legitimate webhook they received on their own dev shop/endpoint) can replay that exact body+hmac to the app's webhook endpoint with `x-shopify-shop-domain: victim-shop.myshopify.com` substituted in. The HMAC check still passes because it never examined the shop header. The handler then receives `WebhookMetadata` claiming to be for `victim-shop`, while it was never sent by Shopify for that shop.

No existing guard fixes this: `HmacValidator` only checks body integrity/secret possession; there is no comparison of `request.shop` against any session, registered endpoint, or signed claim.

### Impact Explanation
This breaks the authentication guarantee that a webhook's shop label is trustworthy. Any app that uses `request.shop` (via `WebhookMetadata.shop`) for tenant lookup/scoping in its handler will act on behalf of an attacker-chosen victim shop identifier, using data from the attacker's own (topic-matching) webhook payload. This is cross-tenant data confusion: the app performs the handler's tenant-scoped logic (e.g., writes, redactions, lookups) using a forged victim shop domain. Severity matches "Critical - cross-tenant access" since the shop binding used for per-tenant dispatch is forgeable by any external actor without secrets.

### Likelihood Explanation
Preconditions: the app must have an HTTP webhook registration for a topic reachable by the attacker's own dev shop (mandatory or app-configured topics commonly qualify, e.g., `orders/create` analogs), and the handler must trust `data.shop` for tenant identification without independent verification (a common and reasonable-looking pattern given the gem's documented API). The attacker needs zero credentials — only their own dev shop, their own registered endpoint, and the ability to capture and replay one webhook’s raw body/HMAC with a modified header. This is cheap, fully repeatable against any victim shop name, and requires no timing constraints (HMAC has no nonce/timestamp binding to shop or delivery).

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signable string, or otherwise cryptographically bind `shop` to the HMAC before dispatch. At minimum, `Registry.process`/handlers should not trust `request.shop` for tenant identification unless it is verified against a known, previously-registered shop associated with the specific webhook subscription (e.g., cross-check against a session record keyed by `webhook_id`/`topic`, or require Shopify's newer verification mechanisms that bind shop context). Concretely, change `to_signable_string` to incorporate `shop-domain` (and reject if it's absent) so `HmacValidator.validate` fails when the shop header is altered.

### Proof of Concept
```ruby
# test/webhooks/shop_binding_forgery_test.rb
require "test_helper"

class ShopBindingForgeryTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", api_version: "unstable",
      host_name: "app.com", scope: "read_products", is_private: false,
      is_embedded: true, session_storage: ShopifyAPI::Auth::FileSessionStorage.new
    )
  end

  def test_hmac_ignores_shop_domain_header
    raw_body = "{}"
    hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new("sha256"), "secret", raw_body)
    hmac_b64 = Base64.strict_encode64([hmac].pack("H*"))

    legit_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "x-shopify-topic" => "orders/create",
        "x-shopify-hmac-sha256" => hmac_b64,
        "x-shopify-shop-domain" => "attacker-dev-shop.myshopify.com",
        "x-shopify-api-version" => "unstable",
        "x-shopify-webhook-id" => "1",
      },
    )

    forged_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "x-shopify-topic" => "orders/create",
        "x-shopify-hmac-sha256" => hmac_b64,
        "x-shopify-shop-domain" => "victim-shop.myshopify.com",
        "x-shopify-api-version" => "unstable",
        "x-shopify-webhook-id" => "1",
      },
    )

    assert ShopifyAPI::Utils::HmacValidator.validate(legit_request)
    assert ShopifyAPI::Utils::HmacValidator.validate(forged_request)

    refute_equal legit_request.shop, forged_request.shop
    assert_equal legit_request.hmac, forged_request.hmac
    # SHOP_BINDING fails: shop authenticated != shop acted upon
  end
end
```
This demonstrates both requests pass `HmacValidator.validate` identically while `WebhookMetadata.shop` (via `request.shop`) diverges, confirming the shop label is unauthenticated and forgeable.