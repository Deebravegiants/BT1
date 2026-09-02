### Title
`Webhooks::Registry.process` trusts unauthenticated `X-Shopify-Shop-Domain` / `X-Shopify-Topic` headers for tenant attribution and handler dispatch - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`Webhooks::Registry.process` derives both the handler to invoke and the `shop` value passed into `WebhookMetadata` from HTTP headers (`request.topic`, `request.shop`) that are never covered by the webhook HMAC. Because the HMAC signable string is only the raw request body [1](#0-0) , an attacker who legitimately owns a validly-signed webhook payload (from their own shop's own subscription) can replay it to the target app's webhook endpoint with the `shop-domain`/`topic` headers rewritten to a victim shop and an arbitrary registered topic, and the HMAC will still validate because it never depended on those headers or on which shop sent the request.

### Finding Description
The invariant that should hold is:
`shop authenticated by the HMAC signature over the webhook payload == request.shop used to build WebhookMetadata and dispatch tenant-scoped handler logic`.

Tracing the code:
- `Request#shop` and `Request#topic` are read straight from HTTP headers with no cross-check against the signed body: [2](#0-1) .
- `Request#to_signable_string` returns only `@raw_body` — headers, including `shop-domain` and `topic`, are excluded from what is HMAC'd: [1](#0-0) .
- `HmacValidator.validate` calls `validate_signature`, which computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header, using the app's single, shop-independent `Context.api_secret_key` (and optionally `old_api_secret_key`): [3](#0-2) .
- `Registry.process` validates the HMAC, then picks the handler via `@registry[request.topic]&.handler`, and if found, invokes it with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`: [4](#0-3) .

Because the same `api_secret_key` is used for every shop installed on the app (it is the app's client secret, not a per-shop secret), and the HMAC is computed purely over the raw body, a payload that is validly signed for shop A's subscription is *also* a validly signed payload when replayed with different `shop-domain`/`topic` headers claiming shop B and a different topic — the signature check in `HmacValidator.validate_signature` has no way to detect the mismatch, since it never inspects headers.

Attacker's exact request: the attacker (1) creates their own development shop, installs the target app, and registers a webhook subscription for a topic the app handles; (2) receives a genuine, validly-HMAC-signed webhook callback from Shopify at their own server; (3) replays that exact raw body to the target app's public webhook endpoint, but substitutes `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and/or `X-Shopify-Topic: <another-registered-topic>`, keeping the original `X-Shopify-Hmac-Sha256` header unchanged. `HmacValidator.validate` returns `true` (body/HMAC pair is unchanged and valid), `Registry.process` resolves the (possibly attacker-chosen) handler, and constructs `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`. Any handler that uses `WebhookMetadata#shop` to scope a database write/read, queue a job, or key a cache entry now operates under the victim's tenant identity using attacker-controlled body content.

None of the existing guards catch this: `HmacValidator.validate` only guarantees the body+secret pair is authentic, not which shop or topic it belongs to; there is no `ShopValidator.sanitize!`, no comparison of `request.shop` against any signed claim, and Sorbet's `T.cast` calls in `Request` only assert a header's *presence*/type, not its correctness. `Context.setup?`/`private?`/`embedded?` and JWT `aud` checks are unrelated to inbound webhook processing and provide no protection here.

### Impact Explanation
This is a cross-tenant vulnerability: the tenant identity (`shop`) and the dispatch key (`topic`) used by `Webhooks::Registry.process` are attacker-controllable headers, decoupled from what the HMAC actually authenticates (only the raw body, under a shop-agnostic app secret). An attacker with a single legitimate webhook subscription on their own shop can forge shop-attribution for every subsequent replay of that payload, targeting any victim shop by name, repeatably, for as long as they retain one valid signed body. Depending on the handler's logic (out of this gem's control but directly enabled by it), this can result in another merchant's records being read, overwritten, or polluted with attacker data — matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Preconditions are minimal and squarely within the attacker capabilities defined by the rules: create a dev shop, install the app, register one webhook subscription, capture one valid signed callback. No `api_secret_key`, access token, or victim credentials are needed. Victim shop domains are guessable/enumerable (`*.myshopify.com`), and the attack is fully repeatable against arbitrary victims using the same captured payload, only changing the `shop-domain` header. The only requirement is that the app exposes its webhook-processing endpoint (`Registry.process`) reachable over the internet, which is the standard deployment model this gem is designed for.

### Recommendation
Do not derive tenant/dispatch identity solely from unauthenticated headers. Include `shop-domain` and `topic` (or a canonical representation of them) in the HMAC signable string, or independently verify that the `shop-domain` header corresponds to a shop actually entitled to send this specific `webhook-id`/payload (e.g. by checking against Shopify's per-webhook delivery metadata or requiring the app to look up an active session for `request.shop` before trusting handler-supplied topic dispatch). At minimum, document and enforce that host apps must treat `WebhookMetadata#shop` as requiring independent verification before using it for tenant-scoped writes.

### Proof of Concept
```ruby
# test/webhooks/cross_tenant_replay_test.rb
require "test_helper"

class CrossTenantReplayTest < Test::Unit::TestCase
  def setup
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
    ShopifyAPI::Webhooks::Registry.clear
    @handler = mock
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", delivery_method: :http, path: "/wh",
      handler: @handler,
    )
  end

  def test_shop_header_not_bound_to_hmac
    raw_body = '{"id":1,"note":"attacker-own-shop-payload"}'
    hmac = Base64.encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", raw_body)
    ).strip

    # Attacker replays their own validly-signed body but swaps shop-domain to victim
    request = ShopifyAPI::Webhooks::Request.new(
      raw_body: raw_body,
      headers: {
        "x-shopify-hmac-sha256" => hmac,
        "x-shopify-topic" => "orders/create",
        "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker never owned this shop
        "x-shopify-api-version" => "2023-01",
        "x-shopify-webhook-id" => "1",
      },
    )

    # HMAC validation succeeds even though the shop was never authenticated
    assert ShopifyAPI::Utils::HmacValidator.validate(request)

    @handler.expects(:handle).with do |data:|
      # Binding broken: shop used downstream != any shop that produced this signature
      data.shop == "victim-shop.myshopify.com"
    end

    ShopifyAPI::Webhooks::Registry.process(request)
  end
end
```
This demonstrates that `request.shop` (and `request.topic`) diverge freely from the shop/topic that actually produced the HMAC-valid body, breaking the required SHOP BINDING invariant purely through header manipulation, with no knowledge of `api_secret_key` beyond what the attacker legitimately obtained for their own shop's webhook.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
