### Title
Webhook `shop-domain` header is not covered by HMAC verification, allowing shop-spoofing via replay of a self-signed webhook - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `Registry.process` accepts the request once `HmacValidator.validate` confirms that HMAC over the body. `request.shop` (and `topic`, `api_version`, `webhook_id`) come from headers that are never part of the signable string, so `request.shop == "value Shopify's edge actually sent"` is not enforced by any cryptographic check. The specific duplicate-header-normalization mechanism described in the question is not itself the exploitable bug (there is only one non-cryptographic fallback-or between `shopify-shop-domain` and `x-shopify-shop-domain`, and Shopify's edge only ever sends one of them), but the underlying binding failure the question is pointing at — "the shop header is trusted with no signature over it" — is real and independently exploitable.

### Finding Description
Binding claimed: `request.shop` (used in `WebhookMetadata.new(shop: request.shop, ...)` at `lib/shopify_api/webhooks/registry.rb:198`) should equal the shop that Shopify's edge actually attributed to this signed payload.

Trace:
- `Request#initialize` (`lib/shopify_api/webhooks/request.rb:46-63`) normalizes header keys to lowercase/dash form and stores them in `@headers`. `shopify_header(name)` (`lib/shopify_api/webhooks/request.rb:67-70`) does `@headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]`.
- `shop`, `topic`, `api_version`, `webhook_id`, and `hmac` are all read from `@headers` via `shopify_header`.
- `to_signable_string` (`lib/shopify_api/webhooks/request.rb:36-38`) returns only `@raw_body` — no header, including `shop-domain`, is included in the signed string.
- `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) computes `HMAC-SHA256(secret, request.to_signable_string)` and compares it against `request.hmac`. This only proves the **body** was produced by Shopify (using `api_secret_key`); it proves nothing about `shop-domain`, `topic`, `api_version`, or `webhook_id` headers.
- `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-200`) calls `HmacValidator.validate(request)`, and on success trusts `request.shop`, `request.topic`, etc., verbatim to build `WebhookMetadata` passed to the app's handler.

Exploit flow: an attacker creates their own development shop, installs the app, and lets Shopify send them a genuine, validly-HMAC-signed webhook for their own shop/topic/body. The attacker then replays that exact `raw_body`+`hmac` to the app's webhook endpoint but substitutes the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header value with `victim-shop.myshopify.com` (or another topic). Since `to_signable_string` never includes headers, `HmacValidator.validate` still succeeds (the body and hmac are untouched, genuinely signed by Shopify with the app's real `api_secret_key`), and `Registry.process` will invoke the handler with `shop: "victim-shop.myshopify.com"` even though that shop never sent this data.

The specific "duplicate header, normalization tie-break" mechanism in the question does not add anything beyond this: there is no merging of two different Shopify-sent headers into one at any transport layer that this gem relies on (Rack/Rails normally raises or picks a single value deterministically for duplicate header names, and Shopify's edge never sends both `shopify-shop-domain` and `x-shopify-shop-domain` simultaneously), so the described "attacker controls which of two conflicting values wins in the hash" scenario is speculative/unproven for this gem's real call path. The exploitable core is simply that **no header is signed**, independent of which fallback resolves.

### Impact Explanation
An attacker can cause an app's webhook handler to process attacker-controlled body data while asserting it originates from an arbitrary victim shop (cross-tenant data confusion) or with an arbitrary declared `topic`/`api_version`/`webhook_id`. This is limited to what the attacker's own already-genuine webhook body contains (they cannot forge arbitrary `raw_body` content without the secret), but they fully control the header-derived metadata (`shop`, `topic`, `api_version`, `webhook_id`) that accompanies it to the handler. Depending on how the host app uses `shop` inside `handler.handle` (e.g., to look up or write per-shop state, revoke access, or delete data — this includes the mandatory `shop/redact`/`customers/redact`/`customers/data_request` topics), this can drive cross-tenant data corruption or spurious redaction/deletion for a victim shop. This matches "Critical - cross-tenant access" since one tenant's webhook can be attributed, at the app's data layer, to another tenant, repeatable for any topic/shop the attacker chooses, and repeatable against arbitrary victim shop names (no need to compromise the victim).

### Likelihood Explanation
The attacker needs only: (1) their own development shop and app install, permitted under the threat model, (2) causing at least one genuine webhook delivery to be captured (trivial — e.g., trigger an order/create webhook), and (3) direct network access to the app's webhook endpoint to replay the request with a modified `shop-domain`/`topic` header, which is basic HTTP client capability, not requiring TLS interception or credentials. No secret material is needed. This is low-cost and fully repeatable against any target shop name.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable string / HMAC computation, or otherwise cryptographically bind them to the body (e.g., verify `shop-domain` against session/shop context established through OAuth for that specific installation, not solely from an unauthenticated header). At minimum, document and/or enforce that `request.shop` must match a shop already known/authenticated for this app installation before invoking handlers, rather than trusting the header outright once the body-only HMAC passes.

### Proof of Concept
```ruby
# test/webhooks/registry_shop_spoof_test.rb
require "test_helper"

class RegistryShopSpoofTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", api_version: "unstable",
      host_name: "app.example.com", scope: "read_products", is_embedded: true,
      is_private: false, session_storage: ShopifyAPI::Auth::InMemorySessionStorage.new,
    )
    ShopifyAPI::Webhooks::Registry.clear
  end

  def test_shop_header_is_not_covered_by_hmac
    raw_body = '{"id":1}'
    valid_hmac = Base64.strict_encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", raw_body),
    )

    # Attacker's own genuine webhook (for their own shop) - HMAC is valid for this body
    attacker_request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "X-Shopify-Hmac-Sha256" => valid_hmac,
        "X-Shopify-Topic" => "orders/create",
        "X-Shopify-Shop-Domain" => "victim-shop.myshopify.com", # attacker swaps this
        "X-Shopify-Api-Version" => "unstable",
        "X-Shopify-Webhook-Id" => "1",
      },
    )

    # HMAC validation succeeds because it only ever checked raw_body, never the shop header
    assert ShopifyAPI::Utils::HmacValidator.validate(attacker_request)
    # Yet the "shop" attributed to this payload is attacker-controlled, unauthenticated
    assert_equal "victim-shop.myshopify.com", attacker_request.shop
  end
end
```
This demonstrates the equality `request.shop == "value Shopify's edge actually sent"` fails: `HmacValidator.validate` returns `true` for a body genuinely signed by Shopify, while `request.shop` is set to an arbitrary attacker-chosen value that Shopify's edge never sent for this body, with no cryptographic check preventing the divergence.