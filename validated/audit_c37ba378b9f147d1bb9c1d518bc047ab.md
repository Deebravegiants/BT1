### Title
Webhook dispatch and metadata (`topic`, `shop`, `webhook_id`, `api_version`) are selected from unauthenticated headers while `HmacValidator` only signs the raw body - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Registry.process` authenticates a webhook request solely via `Utils::HmacValidator.validate(request)`, which checks `request.hmac` against an HMAC computed over `request.to_signable_string`. That signable string is defined as `@raw_body` alone. Handler selection (`@registry[request.topic]&.handler`) and the metadata handed to the handler (`shop`, `webhook_id`, `api_version`, `topic`) are all read from HTTP headers that are never part of the signed content, so a signature that is valid for a given body remains valid no matter what topic/shop/webhook-id/api-version headers accompany it.

### Finding Description
The binding the gem implicitly relies on is: `value verified by HmacValidator == value used to select/route the handler and populate WebhookMetadata`. Tracing the code shows this is false:

- `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `Request#topic`, `#shop`, `#webhook_id`, `#api_version` are all read straight from attacker-controlled HTTP headers with no cryptographic tie to the body: [2](#0-1) 
- `HmacValidator.validate_signature` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the received `hmac` header: [3](#0-2) 
- `Registry.process` gates on that body-only HMAC check, then dispatches purely by the (unsigned) `request.topic` header, and forwards the (unsigned) `shop`, `webhook_id`, `api_version` headers into `WebhookMetadata` that the handler trusts as authentic: [4](#0-3) 

Exploit flow: an attacker installs the app on their own development shop (permitted per rules) and receives one legitimately-signed webhook — body `B` with a valid `hmac-sha256` header `S` (computed by Shopify using the app's shared `client_secret`). Because `S` is a function of `B` alone, the attacker can replay `(B, S)` to the app's public webhook endpoint while freely rewriting `X-Shopify-Topic`, `X-Shopify-Shop-Domain`, `X-Shopify-Webhook-Id`, and `X-Shopify-Api-Version` headers. `HmacValidator.validate` still returns `true` (it never inspects headers), so `Registry.process` will: (a) route `B` to whatever handler is registered for the forged topic, and (b) hand the handler a `WebhookMetadata` claiming an arbitrary, attacker-chosen `shop` domain and `webhook_id` — values the handler has no independent way to distinguish from genuine Shopify-delivered data, since the gem provides no additional authentication of these fields.

Neither `ShopValidator.sanitize!`, `Context.setup?/private?/embedded?`, nor Sorbet runtime typing intervene here — none of them are invoked on this path, and Sorbet type-checks only guarantee `topic`/`shop` are `String`, not that they are the values Shopify actually sent for `B`.

The `get_webhook_id` GraphQL-interpolation detail cited in the question (unescaped `topic` embedded in a GraphQL query for `unregister`) is a separate, admin-API-side code path guarded by the app's own OAuth session and is not itself attacker-reachable without a valid session; the exploitable divergence is the header/body signature-coverage gap in `process`/`Request`, not `get_webhook_id`'s string interpolation.

### Impact Explanation
Because `shop`, `topic`, and `webhook_id` are unauthenticated relative to the HMAC, an app author who trusts `WebhookMetadata.shop` (as the gem's own struct implies they should — it is the field named `shop`) to decide which merchant's session/data to act on can be tricked into performing actions attributed to any merchant, using only a body/signature pair the attacker legitimately obtained for their own tenant. This is a cross-tenant authenticity failure: the app cannot distinguish "Shopify said this event is for shop X" from "attacker replayed a body I trust and just wrote a different `X-Shopify-Shop-Domain`". It also allows topic confusion (dispatching arbitrary attacker-supplied JSON to a handler meant for a different topic/schema), which can trigger mandatory-compliance handlers (`shop/redact`, `customers/redact`, `customers/data_request`) or business-logic handlers with attacker-shaped payloads. This matches "cross-tenant access" / "a forged... request is accepted as authentic by the app" (Critical).

### Likelihood Explanation
Preconditions: the attacker needs the app to expose a webhook endpoint reachable over the internet (standard for this gem's use) and needs to have obtained at least one valid `(body, hmac)` pair, which any attacker can get for free by installing the app on their own development shop and triggering any webhook. No `api_secret_key` or access token is required. Cost is a single legitimate webhook capture plus direct HTTP requests to the endpoint; the attack is trivially repeatable for every subsequent forged header combination, since only headers vary and the previously-captured signature is reused unchanged.

### Recommendation
Include the security-relevant headers (`topic`, `shop-domain`, `webhook-id`, `api-version`) in the value signed/verified, or otherwise cryptographically bind them to the body before use — e.g., have `to_signable_string` incorporate a canonical representation of these headers, or require the host app to additionally verify `shop` against a known/authorized shop list and reject topics not matching the value used at registration time, before trusting `WebhookMetadata`. At minimum, document loudly that `topic`/`shop`/`webhook_id` are NOT covered by the HMAC and must not be trusted for authorization decisions without independent verification.

### Proof of Concept
```ruby
# test/webhooks/registry_topic_confusion_test.rb
class RegistryTopicConfusionTest < Minitest::Test
  def setup
    ShopifyAPI::Webhooks::Registry.clear
    ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)
    @handler_a = HandlerA.new # spy that records data.shop
    @handler_b = HandlerB.new # spy that records data.shop
    ShopifyAPI::Webhooks::Registry.add_registration(topic: "products/create", delivery_method: :http, path: "/a", handler: @handler_a)
    ShopifyAPI::Webhooks::Registry.add_registration(topic: "customers/create", delivery_method: :http, path: "/b", handler: @handler_b)
  end

  def test_signature_does_not_bind_to_topic_or_shop_headers
    body = '{"id":1}'
    hmac = Base64.strict_encode64(OpenSSL::HMAC.digest("sha256", "secret", body))

    # Legitimately-shaped request for topic A / shop-a.myshopify.com
    genuine = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: {
      "x-shopify-topic" => "products/create",
      "x-shopify-hmac-sha256" => hmac,
      "x-shopify-shop-domain" => "shop-a.myshopify.com",
      "x-shopify-webhook-id" => "wh-1",
      "x-shopify-api-version" => "2024-01",
    })
    ShopifyAPI::Webhooks::Registry.process(genuine)
    assert_equal "shop-a.myshopify.com", @handler_a.last_shop

    # Same body+signature, forged topic/shop headers -> still validates, dispatches to handler_b
    forged = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: {
      "x-shopify-topic" => "customers/create",
      "x-shopify-hmac-sha256" => hmac,
      "x-shopify-shop-domain" => "victim-shop.myshopify.com",
      "x-shopify-webhook-id" => "wh-1",
      "x-shopify-api-version" => "2024-01",
    })
    ShopifyAPI::Webhooks::Registry.process(forged) # does not raise InvalidWebhookError
    assert_equal "victim-shop.myshopify.com", @handler_b.last_shop # proves topic/shop are unauthenticated
  end
end
```
This demonstrates that the value verified by `HmacValidator` (the body) diverges from the values used downstream (`topic`, `shop`, `webhook_id`), confirming the signature-coverage gap.

### Citations

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
