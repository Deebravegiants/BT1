### Title
Webhook HMAC signs only the raw body, never the `X-Shopify-Shop-Domain` header, so `Registry.process` forwards an unauthenticated tenant identifier to handlers - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `shop` (and `topic`, `webhook_id`, `api_version`) are read straight from attacker-controllable HTTP headers with no cryptographic binding to the body. `Registry.process` validates the HMAC of the body alone and then calls `handler.handle` with `shop: request.shop` taken from the unauthenticated header, so an attacker who obtains any validly-signed body (e.g., from their own dev-shop webhook) can replay it to the app's public callback URL with a forged `X-Shopify-Shop-Domain` header pointing at a victim merchant.

### Finding Description
The binding the gem should enforce is: `signed_content` (the bytes covered by `hmac`) `==` the full tuple `{shop, topic, webhook_id, api_version, body}` that the handler acts on. In fact:

- `to_signable_string` only returns `@raw_body`: [1](#0-0) 
- `shop` is read purely from the header, never checked against anything signed: [2](#0-1) 
- `HmacValidator.validate` computes the HMAC only over `to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 
- `Registry.process` validates HMAC and immediately builds `WebhookMetadata` using `request.shop` (header) alongside `request.parsed_body`, with zero cross-check between the two: [4](#0-3) 

Exploit flow: the attacker installs the app on their own development shop (permitted by the threat model). Through normal use of that shop (e.g., creating an order with attacker-chosen free-text fields such as note/attributes), Shopify sends a legitimately HMAC-signed webhook body to the app's shared callback route (the route is topic-scoped, not shop-scoped — see `Registrations::Http#callback_address`, which is fixed per topic, not per shop). The attacker captures this `raw_body` + `X-Shopify-Hmac-SHA256` header pair (they run their own server or simply observe their own webhook delivery). They then issue their own raw HTTP POST directly to the app's public webhook endpoint, re-using that exact `raw_body`/`hmac` pair, but replacing `X-Shopify-Shop-Domain` with a victim merchant's real domain. Because `to_signable_string` never included the shop header, `HmacValidator.validate` still returns `true`. `Registry.process` then calls `handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-authored JSON>, ...))`. If the host app's handler uses `data.shop` (undocumented as authenticated, but the only tenant hint the gem provides) to pick the tenant partition to write `data.body` into, this is a cross-tenant write of attacker-chosen content into the victim's data.

None of the existing guards intercept this: `HmacValidator.validate` only proves the body wasn't tampered with, not that the header/body pairing is genuine; there is no `ShopValidator.sanitize!` call in this path; there is no `state` comparison (that only exists for OAuth); `JwtPayload` is unrelated (session tokens, not webhooks); `Context.setup?/private?/embedded?` do not participate in webhook processing; Sorbet signatures only enforce types (`String`), not cross-field integrity.

### Impact Explanation
A successful exploit lets an unprivileged attacker who controls only their own development shop and its webhook deliveries make the host application believe attacker-authored webhook content originated from any other real, named merchant shop of the attacker's choosing. If the host app trusts `WebhookMetadata#shop` as the tenant key (which is the only shop identifier the gem exposes to handlers, and which the documentation presents without any authenticity caveat), this yields cross-tenant data corruption/write — matching the "cross-tenant access" Critical category. The attack is repeatable against arbitrary victim shops since the callback route is shared across all shops for a topic and the victim's `*.myshopify.com` domain is public/guessable. The blast radius is bounded by what content type the attacker can smuggle into a legitimately-signed webhook body for their own shop (typically free-text/attribute fields on orders, products, customers, etc.), but the tenant-selection field itself is fully attacker-controlled.

### Likelihood Explanation
Preconditions: (1) the host app's webhook handler decides which tenant/shop's data to mutate using `WebhookMetadata#shop` without independently confirming that shop against any authenticated source (e.g. without checking that a `webhook_id` returned by this exact shop's own registration matches, or without an app-level allowlist bound at OAuth time); (2) the app's webhook callback URL is discoverable/guessable (typically true, since it's a fixed public route, e.g. `/webhooks`). Attacker cost is minimal: create a free development shop, install the app, trigger one webhook naturally, and replay it with a modified header — no secrets, no privileged access, fully repeatable per victim.

### Recommendation
Bind the shop identity (and topic/webhook id) into something the gem verifies, and/or make the trust boundary explicit:
- Extend `Request#to_signable_string` (or add a separate check in `HmacValidator`/`Registry.process`) so that the callback's expected shop is not solely header-derived — e.g. require host apps to pass the shop the webhook was registered for and have `Registry.process` reject processing if that does not match, or document in `WebhookMetadata` that `shop` is unauthenticated and must be cross-checked against the app's own session/install records before being used as a tenant key.
- At minimum, update documentation/`docs/usage/webhooks.md` and `WebhookMetadata` to state explicitly that `shop` is derived from an unauthenticated header and must never be used directly to select a tenant partition without corroboration (e.g., checking that an active installed session exists for that shop, or that `webhook_id`/topic pairing was actually registered for that shop).

### Proof of Concept
```ruby
# test/webhooks/registry_shop_spoof_test.rb
require_relative "../test_helper"

class RegistryShopSpoofTest < Test::Unit::TestCase
  def setup
    super
    ShopifyAPI::Webhooks::Registry.clear
    @raw_body = '{"note":"legit content for attacker-shop.myshopify.com"}'
    @valid_hmac = Base64.encode64(
      OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, @raw_body)
    )
  end

  def test_hmac_does_not_bind_shop_header
    attacker_headers = {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => @valid_hmac,
      "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
    }
    victim_headers = attacker_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

    attacker_request = ShopifyAPI::Webhooks::Request.new(raw_body: @raw_body, headers: attacker_headers)
    victim_request    = ShopifyAPI::Webhooks::Request.new(raw_body: @raw_body, headers: victim_headers)

    # Both pass HMAC validation despite different shop headers -> header not covered by signature.
    assert(ShopifyAPI::Utils::HmacValidator.validate(attacker_request))
    assert(ShopifyAPI::Utils::HmacValidator.validate(victim_request))
  end

  def test_process_never_compares_shop_to_body_content
    received_shop = nil
    handler = TestHelpers::FakeWebhookHandler.new(lambda { |data| received_shop = data.shop })
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", path: "callback", delivery_method: :http, handler: handler,
    )

    forged_headers = {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => @valid_hmac,
      "x-shopify-shop-domain" => "victim-shop.myshopify.com",
    }
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: @raw_body, headers: forged_headers)
    )

    # Registry.process trusted the header shop even though body/hmac were generated
    # for a different (attacker) shop context, with no equality check performed.
    assert_equal("victim-shop.myshopify.com", received_shop)
  end
end
```
Both assertions demonstrate that `HmacValidator.validate` and `Registry.process` never enforce `request.shop == <any signed field>`, confirming the reachable, unauthenticated cross-tenant path.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
