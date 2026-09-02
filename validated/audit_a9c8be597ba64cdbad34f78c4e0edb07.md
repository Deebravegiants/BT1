### Title
Webhook HMAC only signs `@raw_body`, so an attacker-forged `shop-domain` header on a legitimately-signed body drives session/token lookup - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`Request#to_signable_string` returns only `@raw_body`, and `Request#shop` reads the `shopify-shop-domain`/`x-shopify-shop-domain` header directly with no cross-check against the signed content. `Utils::HmacValidator.validate` therefore only proves that *some* body was signed with the app's `api_secret_key`; it says nothing about which shop that body belongs to. `Registry.process` passes this unauthenticated header value straight into `WebhookMetadata.shop`, which the documented handler pattern (`docs/usage/webhooks.md`) uses to look up a merchant's session/access token.

### Finding Description
Binding claimed: `hmac_authenticated_shop == WebhookMetadata.shop` (the shop identity verified by HMAC equals the shop identity used for session/token selection).

Trace:
- `Request#hmac` reads `shopify-hmac-sha256`/`x-shopify-hmac-sha256` [1](#0-0) .
- `Request#to_signable_string` returns `@raw_body` only - no header, including `shop-domain`, is part of the signable string [2](#0-1) .
- `Request#shop` reads the `shop-domain` header verbatim, independent of the body/HMAC [3](#0-2) .
- `HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the received signature - it validates the body, never the headers [4](#0-3) .
- `Registry.process` calls `HmacValidator.validate(request)`, and on success builds `WebhookMetadata.new(... shop: request.shop ...)` directly from the header, with no additional check that the header matches a shop associated with the signed body [5](#0-4) .
- The documented handler pattern explicitly encourages using `data.shop` to key further work (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), and the general documented pattern for reacting to webhooks with further Admin API calls is to look up a session/access token by `data.shop` [6](#0-5) .

Root cause: the app's `api_secret_key` is shared across all shops that install the app; it is not shop-specific. Because the signable string is body-only, an attacker who installs the app on their own shop can receive a genuinely, validly-signed webhook (signed by Shopify with the app's real secret) for their own shop, then replay that exact `raw_body` to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with `victim.myshopify.com`. `HmacValidator.validate` still returns `true` (body untouched, secret matches), but `WebhookMetadata.shop` is now the forged victim domain. If the host app's handler (per the documented pattern) loads a session/access token keyed by `data.shop`, it will load the victim's token and act on attacker-controlled body content under the victim's identity/session.

None of the gem's existing guards catch this: `HmacValidator.validate` (body-only, as shown), `ShopValidator.sanitize!` (only used in OAuth `shop` param flow, not invoked anywhere in the webhook path), the `state` comparison (OAuth-only), `JwtPayload`'s `aud` check (session-token flow, unrelated), `HttpRequest#verify`/`Context.setup?`/`private?`/`embedded?` (unrelated to webhook shop binding). No code in `Request`, `Registry`, or `WebhookMetadata` cross-checks `request.shop` against anything derived from the signed body.

### Impact Explanation
Any shop the attacker controls (their own installed instance of the app) lets them mint arbitrary bodies that are validly HMAC-signed by the app's secret. By forging only the `shop-domain` header (which is never covered by the signature), the attacker can make `Registry.process` deliver that body to the handler tagged as belonging to any victim shop that has installed the app. If the host app follows the gem's documented pattern of using `data.shop` to look up a session/access token and perform further Admin API calls, this results in the victim's stored access token being used to perform an action whose content is chosen by the attacker - a cross-tenant access issue, repeatable against arbitrary victim shop domains (the attacker only needs to know or guess the victim's `myshopify.com` domain, which is often public). This matches the Critical category: cross-tenant access via an unauthenticated value (`shop-domain` header) being trusted as if it were HMAC-authenticated.

### Likelihood Explanation
Preconditions: the attacker must be able to install the app on a shop they control (readily available via a free Shopify development/partner store) to legitimately receive at least one signed webhook, and the app's webhook controller must accept `raw_body`/`headers` directly as documented (`request.raw_post`, `request.headers.to_h`) without imposing its own additional shop-binding check. The host app must additionally follow the documented pattern of using `data.shop` for session/token lookup - a pattern explicitly shown in this gem's docs. Attacker cost is low: no secrets are needed, only a signed body legitimately obtained from their own store and a forged HTTP header on a replayed request to the app's public webhook endpoint. This is repeatable per victim shop domain with no rate limiting in the gem.

### Recommendation
Bind the header-derived shop to something verifiable, or eliminate the header as a trust boundary: e.g., require the body's `raw_body` to include shop-identifying data (many Shopify webhook payloads include shop-scoped resource IDs, but not shop domain) is insufficient; instead the app should not use `shop-domain` header for authorization decisions without an independent join against the registered webhook's known destination shop (e.g., match the shop to a shop that is known to have this specific `webhook_id`/subscription registered, or use per-shop signing/verification such as checking that the shop associated with the current session context matches). At minimum, document explicitly (and enforce in `Registry.process`) that `request.shop`/`WebhookMetadata.shop` is **not** authenticated by HMAC and must not be used as a sole key for session or access-token lookup without an additional binding check.

### Proof of Concept
minitest under `test/webhooks/registry_test.rb` style, using the existing signing helper pattern from `test/utils/hmac_validator_test.rb`:

```ruby
def test_forged_shop_domain_header_is_accepted_with_victims_shop
  body = { "id" => 1, "note" => "attacker-controlled" }.to_json
  hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
  encoded_hmac = Base64.strict_encode64([hmac].pack("H*"))

  request = ShopifyAPI::Webhooks::Request.new(
    raw_body: body,
    headers: {
      "X-Shopify-Topic" => "orders/create",
      "X-Shopify-Hmac-Sha256" => encoded_hmac,
      "X-Shopify-Shop-Domain" => "victim.myshopify.com", # forged, attacker's real shop was attacker.myshopify.com
      "X-Shopify-Webhook-Id" => "1",
      "X-Shopify-Api-Version" => "2023-10",
    },
  )

  assert(ShopifyAPI::Utils::HmacValidator.validate(request)) # HMAC passes: body-only signature untouched
  assert_equal("victim.myshopify.com", request.shop) # unauthenticated header trusted as shop identity

  handler = mock
  handler.expects(:handle).with(has_entry(shop: "victim.myshopify.com"))
  ShopifyAPI::Webhooks::Registry.add_registration(topic: "orders/create", delivery_method: :http,
    path: "cb", handler: handler)
  ShopifyAPI::Webhooks::Registry.process(request)
end
```

This demonstrates: `computed_hmac(raw_body) == received_hmac` holds (both sides of the *body* HMAC binding match), while `hmac_authenticated_shop == WebhookMetadata.shop` does not hold - the shop passed to the handler is fully attacker-controlled despite a "validly signed" body.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L20-29)
```markdown
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
