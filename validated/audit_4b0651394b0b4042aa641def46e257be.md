### Title
Webhook HMAC covers only the raw body, leaving `shop`, `topic`, and `webhook_id` headers unauthenticated, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by comparing an HMAC over the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by the handler are taken directly from unauthenticated HTTP headers. Any request whose body+HMAC pair is valid for the app's secret will pass validation regardless of what these header fields say, breaking the equality `shop authenticated == shop the handler acts on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is read from the `hmac-sha256` header: [1](#0-0) 

`Registry.process` uses `Utils::HmacValidator.validate(request)` — which calls `to_signable_string` (body only) — to decide whether "the request did indeed come from Shopify" (per the gem's own documentation), then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id`, none of which are part of the signed bytes: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string`: [3](#0-2) 

Documentation explicitly instructs developers to trust `data.shop` and `data.topic` coming out of this call as verified, and shows them being used to route work for a specific shop: [4](#0-3) [5](#0-4) 

The binding the gem implies but does not enforce is: `shop/topic/webhook_id claimed in headers == shop/topic/webhook_id bound by the HMAC signature`. In reality the HMAC only proves "this body was produced/observed with knowledge of the shared secret at some point" — it says nothing about which shop, topic, or webhook the body is currently being asserted for.

### Impact Explanation
Any unprivileged party who can obtain one legitimately-signed webhook delivery (e.g., by installing the app on their own development store and capturing the raw body + `X-Shopify-Hmac-Sha256` header from a webhook Shopify sends to the app's registered endpoint) can replay that exact `(raw_body, hmac)` pair to the same endpoint while substituting arbitrary `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, and `X-Shopify-Webhook-Id` header values. `HmacValidator.validate` will still return `true` because it never looks at those headers, and the handler will receive a `WebhookMetadata` claiming to originate from a different, victim shop/topic. Following the gem's own example handler pattern (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), this lets the attacker inject data attributed to a shop they do not control, or relabel one topic's payload as another topic, causing cross-tenant data corruption/impersonation in the host application — meeting the Critical "cross-tenant access" bar since the identity binding (shop) that gates per-tenant processing is not actually authenticated.

### Likelihood Explanation
Requires only: (1) the attacker's own installation of the target app (freely available to any merchant/developer for public apps) to receive one genuinely-signed webhook, and (2) the ability to send arbitrary HTTP requests to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is needed — this is achievable entirely by an unprivileged internet user who can install the app on a store they control.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the signed material, or otherwise cryptographically tie them to the verified body (e.g., include them in the HMAC computation, or require the caller to independently confirm `shop` against the shop that originally installed/registered the webhook via a stored session, and to correlate `webhook_id` for idempotency/topic consistency) before `Registry.process` dispatches to the handler. At minimum, update documentation to clarify that only body integrity is verified and that `shop`/`topic`/`webhook_id` require independent authorization checks by the host app.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own dev shop and captures a real webhook delivery:
#    raw_body = '{"id":1,...}'
#    headers  = {
#      "x-shopify-topic" => "orders/create",
#      "x-shopify-hmac-sha256" => "<valid-signature-for-raw_body>",
#      "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
#      "x-shopify-webhook-id" => "wh_1",
#      "x-shopify-api-version" => "2024-01",
#    }

# 2. Attacker replays the identical raw_body + hmac-sha256 header,
#    but swaps the shop/topic headers to target a victim shop:
forged_headers = headers.merge(
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",
  "x-shopify-topic" => "orders/create",
)

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. Validation succeeds because HMAC only covers raw_body, which is unchanged:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", ...))
# The host app now processes attacker-controlled data as if it belongs to victim-shop.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
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
