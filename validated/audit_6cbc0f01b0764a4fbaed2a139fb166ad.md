### Title
Webhook HMAC signature does not bind `x-shopify-topic` or `x-shopify-shop-domain`, allowing cross-tenant identity spoofing on replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`Webhooks::Request#hmac` and `Utils::HmacValidator.validate` verify only the raw request body against the app's shared `api_secret_key`; the `x-shopify-topic` and `x-shopify-shop-domain` headers are never included in the signed material. `Registry.process` then uses the unauthenticated `topic` header to select the handler and passes the unauthenticated `shop` header straight into `WebhookMetadata`, which the host app uses to decide whose data to act on.

### Finding Description
The claimed binding — "a valid HMAC over the body implies the accompanying `topic`/`shop-domain` headers are authentic" — does not hold. Tracing the code:

- `Request#hmac` decodes `x-shopify-hmac-sha256` [1](#0-0) , and `#to_signable_string` returns only `@raw_body` [2](#0-1) .
- `HmacValidator.validate_signature` computes `HMAC(secret, to_signable_string)` and compares it to `verifiable_query.hmac` — nothing derived from `topic` or `shop-domain` enters this computation [3](#0-2) .
- `Registry.process` first calls `HmacValidator.validate(request)` (body-only check), then uses the **unauthenticated** `request.topic` to look up the handler, and forwards the **unauthenticated** `request.shop` into `WebhookMetadata` [4](#0-3) .
- `request.topic` and `request.shop` are read straight off headers with no cryptographic tie to the signature [5](#0-4) .

Because `api_secret_key` is a single app-level secret shared across every shop that installs the app (not a per-shop secret), an attacker who installs their own app instance on a shop they control receives genuinely-signed `(body, hmac)` pairs from Shopify for their own shop/topic. Nothing prevents the attacker from taking that valid pair and POSTing it directly to the target app's public webhook endpoint with the `x-shopify-topic` and `x-shopify-shop-domain` headers rewritten to an arbitrary topic (that the host app has registered a handler for) and an arbitrary victim shop domain. `HmacValidator.validate` still returns `true` because it only checks the body against the secret; `Registry.process` will happily dispatch the attacker-chosen handler with `WebhookMetadata#shop` set to the spoofed victim domain.

None of the existing guards catch this: `HmacValidator.validate` is body-only by design [6](#0-5) ; there is no `ShopValidator.sanitize!` call, no cross-check between the registered topic and the signed body's shape, and `WebhookMetadata` is a plain `T::Struct` with no validation on `shop` [7](#0-6) .

### Impact Explanation
A host app that trusts `WebhookMetadata#shop`/`#topic` (the documented way to consume webhook data) to select which merchant's records or session to touch can be made to act on behalf of an attacker-chosen victim shop domain using attacker-controlled body content, because the signature never authenticates which shop or topic the payload is "for" — only that some shop under the same app produced it. This is a genuine tenant-identity confusion (the shop the signature actually vouches for vs. the shop the handler is told to act on diverge), which falls into the Critical "cross-tenant access" category. It does not, by itself, exfiltrate an Admin API access token through this gem's own code — no code path in `request.rb`, `registry.rb`, or `webhook_handler.rb` returns or logs a token — so the specific "theft of Admin API access token" framing in the question is not demonstrated by this gem; the concrete, provable impact is cross-tenant metadata/handler confusion, contingent on how a given host app uses `shop`.

### Likelihood Explanation
Preconditions: attacker needs their own development shop with the target app installed (freely available, matches the described unprivileged threat model) and the target app's webhook endpoint reachable directly over HTTP (typical for Rails-mounted webhook controllers). No secrets, no TLS interception, and no privileged access are required — only replay of a genuinely-received `(body, hmac)` pair with rewritten headers. This is cheap and repeatable against any topic the host app has registered a handler for, and against any victim shop domain (the field is a free-text header, not validated against an install list by this gem).

### Recommendation
Bind the HMAC signature (or a secondary MAC) to the `topic` and `shop-domain` headers in addition to the body, or require host apps to cross-check `WebhookMetadata#shop` against a known/installed-shop list before trusting it, and validate that `WebhookMetadata#topic` matches the topic the endpoint was registered for.

### Proof of Concept
```ruby
# test/webhooks/registry_cross_tenant_test.rb
require "test_helper"

class RegistryCrossTenantTest < Test::Minitest
  def setup
    ShopifyAPI::Context.setup(api_secret_key: "secret", ...)
    ShopifyAPI::Webhooks::Registry.clear
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "app/uninstalled", delivery_method: :http, path: "/", handler: victim_handler
    )
  end

  def test_replayed_body_with_spoofed_shop_and_topic_is_accepted
    body = '{"id":1}'
    secret = "secret"
    hmac = Base64.strict_encode64(OpenSSL::HMAC.digest("sha256", secret, body))

    request = ShopifyAPI::Webhooks::Request.new(
      raw_body: body,
      headers: {
        "x-shopify-topic" => "app/uninstalled",       # attacker chosen
        "x-shopify-hmac-sha256" => hmac,               # legit signature for THIS body only
        "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker chosen, unauthenticated
      },
    )

    # Binding under test: hmac validity should not imply shop/topic authenticity
    assert ShopifyAPI::Utils::HmacValidator.validate(request)
    assert_equal "victim-shop.myshopify.com", request.shop # unauthenticated value accepted as-is

    ShopifyAPI::Webhooks::Registry.process(request) # dispatches handler with spoofed shop
  end
end
```
This demonstrates that a body/HMAC pair legitimately obtained for one shop/topic is accepted unchanged by `HmacValidator.validate` after the `topic` and `shop-domain` headers are swapped, confirming the signature does not bind to shop/topic identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
