### Title
`Webhooks::Request#to_signable_string` signs only the raw body, letting attacker-controlled `shop-domain`/`topic`/`webhook-id` headers reach the handler unauthenticated - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Utils::VerifiableQuery` only requires that an implementation expose *some* string to `HmacValidator`; it does not require that string to cover every field the implementation exposes to consumers. `Webhooks::Request#to_signable_string` returns `@raw_body` only [1](#0-0) , while `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are read straight from HTTP headers [2](#0-1)  and are never part of the HMAC-signed content. `Registry.process` forwards these unauthenticated header values, including `request.shop`, directly into `WebhookMetadata` and the app's handler as if they were verified [3](#0-2) , and the documentation confirms apps are expected to trust `data.shop` as "the shop domain of the webhook" [4](#0-3) .

### Finding Description
The claimed binding is: `to_signable_string(request) ⊇ {request.shop, request.topic, request.webhook_id, request.api_version, request.raw_body}` — i.e., every value the handler consumes from a `VerifiableQuery` should be inside the string handed to `HmacValidator`.

In practice, `to_signable_string` for `Webhooks::Request` equals only `@raw_body` [1](#0-0) . `HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest(sha256, secret, verifiable_query.to_signable_string)` and compares it against `verifiable_query.hmac`, which is parsed from the `x-shopify-hmac-sha256` header [5](#0-4) [6](#0-5) . This means the signature covers *only the body bytes*; the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are outside the signed content entirely, so any value an attacker places in those headers passes validation as long as the body+hmac pair is genuine.

The `api_secret_key` is a single shared app secret, not a per-shop secret. An attacker who is an unprivileged internet user can, per the threat model, install the app on their own development shop and legitimately receive validly-signed webhook deliveries (real body + real HMAC computed with the shared app secret). They can then replay that exact `(body, hmac)` pair to the app's public webhook endpoint while rewriting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`, `x-shopify-webhook-id`) to name a different, victim shop. `HmacValidator.validate` still returns true because it never looks at those headers [7](#0-6) . `Registry.process` then raises no error and dispatches `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` to the app-supplied handler [3](#0-2) , which per the gem's own documented usage pattern trusts `data.shop` to route/attribute the webhook to a specific merchant (e.g., `perform_later(shop_domain: data.shop, ...)`) [8](#0-7) .

No other guard closes this gap: `HmacValidator` checks only `hmac`/`to_signable_string`; there is no `ShopValidator.sanitize!` or session cross-check inside `Registry.process`; `Context.setup?`/`private?`/`embedded?` are irrelevant to webhook processing; Sorbet's `interface!`/`abstract` only enforces the *presence* of `to_signable_string`, not its *coverage* of exposed fields.

### Impact Explanation
An attacker can make the host application attribute an arbitrary, attacker-chosen shop domain (and topic/webhook id) to data that is otherwise genuine (their own webhook body), or — more importantly — this proves the general class: whatever data a `VerifiableQuery` implementation exposes to consumers outside `to_signable_string` is not authenticated at all. For `Webhooks::Request`, this is a cross-tenant data-attribution issue: the app processes/attributes a webhook as coming from a shop it did not actually come from, which can poison per-shop job queues, trigger unauthorized actions against a victim shop's session/data, or be used to fabricate mandatory compliance webhooks (`shop/redact`, `customers/redact`, `customers/data_request`) for a shop the attacker doesn't control. It's repeatable against arbitrary victim shop domains at will, since the attacker only needs one genuine signed webhook from their own shop.

### Likelihood Explanation
The attacker only needs to install the app on a shop they control and register a webhook endpoint they control (both explicitly permitted in the threat model) to obtain one real `(body, hmac)` pair. No special app configuration is required beyond having any HTTP webhook handler registered. Cost is a single legitimate webhook capture; the header-rewrite-and-replay is trivial to script and infinitely repeatable.

### Recommendation
Include the values that consumers are expected to trust as authenticated inside the signed material, or otherwise enforce the invariant at the `VerifiableQuery` boundary. Concretely, for `Webhooks::Request`, either (a) validate `request.shop` against the shop associated with the session/registration the app expects before trusting it, or (b) require host apps to independently verify shop identity out-of-band from the HMAC-covered body (as Shopify's real webhook contract does), and document explicitly that `shop`/`topic`/`webhook_id`/`api_version` are **not** covered by `hmac` verification so app authors don't treat `WebhookMetadata#shop` as authenticated. More generally, add a coverage contract/test to `Utils::VerifiableQuery` (or its specs) asserting that every public accessor an implementation exposes for consumption is either included in `to_signable_string` or explicitly documented/flagged as unauthenticated.

### Proof of Concept
```ruby
# test/webhooks/registry_spoofed_shop_test.rb
require "test_helper"

class SpoofedShopWebhookTest < Test::Unit::TestCase
  def test_shop_domain_header_not_covered_by_hmac
    body = '{"id":1}'
    real_hmac = Base64.encode64(
      OpenSSL::HMAC.digest("sha256", ShopifyAPI::Context.api_secret_key, body)
    )

    # Attacker's own shop delivery, headers rewritten to victim shop
    forged_headers = {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => real_hmac,
      "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker rewrites this
      "x-shopify-webhook-id" => "forged-id",
      "x-shopify-api-version" => "2024-01",
    }

    request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)

    # Binding under test: to_signable_string does NOT cover `shop`
    refute_includes(request.to_signable_string, "victim-shop.myshopify.com")

    # HMAC validation still passes despite forged shop header
    assert(ShopifyAPI::Utils::HmacValidator.validate(request))

    received_shop = nil
    handler = Object.new
    handler.define_singleton_method(:handle) { |data:| received_shop = data.shop }
    ShopifyAPI::Webhooks::Registry.add_registration(
      topic: "orders/create", delivery_method: :http, path: "cb", handler: handler,
    )

    ShopifyAPI::Webhooks::Registry.process(request)

    # Proof: handler receives attacker-forged shop as if authenticated
    assert_equal("victim-shop.myshopify.com", received_shop)
  end
end
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L24-26)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
