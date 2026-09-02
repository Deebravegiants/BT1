## Title
Webhook HMAC only signs the request body, letting a replayed signature be re-attributed to any shop via the unauthenticated `shopify-shop-domain` header - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read from headers that are never included in that signature. `ShopifyAPI::Webhooks::Registry.process` only checks that the body's HMAC is valid before handing `request.shop` straight to the app's handler as the trusted tenant identifier, so the "shop that produced a validly-signed payload" and "shop the app treats as the source of that payload" are two different bindings that the gem never reconciles.

## Finding Description
`Utils::VerifiableQuery`/`HmacValidator.validate` verifies a query object by recomputing the HMAC over `to_signable_string` and comparing it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw JSON body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers that are completely outside that signed string: [3](#0-2) 

`Registry.process` validates only the body HMAC, then forwards `request.shop` (and the other header-derived fields) unchanged to the app's handler as the authoritative tenant identity: [4](#0-3) 

The gem's own documented integration pattern treats `data.shop` from `WebhookMetadata` as the trusted per-tenant key to route/store webhook data: [5](#0-4) 

The binding this breaks, expressed as an equality that the gem never enforces:

`shop_that_produced(body, hmac)` (implicit — Shopify never actually binds a shop to the HMAC because the signature covers only the body) `!=` `shop_used_by_handler(request.shop)`.

Since the signature never covers the shop identifier at all, **any bytes + hmac pair that once validated for one shop remains valid forever for a request carrying a different `shopify-shop-domain` header**. An unprivileged internet user who legitimately installs the target app on their own store (a normal, unprivileged action any developer/merchant can take) receives real webhook deliveries with a valid `hmac-sha256` for their own shop. They can capture one such `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to a victim shop domain. `HmacValidator.validate` still succeeds because it only checks the (unchanged) body against the (unchanged) hmac, and `Registry.process` passes the attacker-chosen `shop` value straight through to the handler.

## Impact Explanation
This is a cross-tenant identity-binding break: a signature that was only ever computed over the payload body is treated by the gem/handler as if it authenticated the `shop` field too. Any app that follows this gem's documented pattern of keying persistence/actions off `WebhookMetadata#shop` can have webhook data attributed to, or trigger side effects against, a shop the attacker does not control and never received that specific webhook for. This meets the "cross-tenant access" criterion.

## Likelihood Explanation
Requires no secrets: the attacker needs a legitimate account/store to receive at least one real webhook of the desired topic and body shape (trivially obtainable by installing any test app on a free development store), then a single unauthenticated HTTP request to the target app's public webhook endpoint with a modified header. No `api_secret_key`, access token, or privileged access is needed at any step.

## Recommendation
Include the shop domain (and topic/webhook id) in the value that is HMAC-verified, or otherwise cryptographically bind `request.shop` to the same signed payload the HMAC covers, e.g. by requiring the app to also compare the delivered shop against the shop tied to the app's own known/installed sessions before trusting `WebhookMetadata#shop`, and document this requirement prominently since `Registry.process` currently offers no such binding itself.

## Proof of Concept
```ruby
# Attacker installs the app on their own store "attacker-shop.myshopify.com"
# and captures a real, validly-signed webhook delivery:
captured_body = '{"id": 1, "note": "hello"}'
captured_hmac = "shopify-hmac-sha256: <value Shopify computed for attacker-shop>"

# Attacker replays the exact same body + hmac to the victim app's endpoint,
# but swaps only the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac,   # unchanged, still valid: only signs body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unsigned
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds (body+hmac match),
# handler.handle receives shop: "victim-shop.myshopify.com" — attacker-attributed to victim tenant.
``` [4](#0-3) [6](#0-5)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
