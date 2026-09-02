### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the tenant-identifying `shop` value (and topic/version/id) is taken from an unauthenticated HTTP header. This breaks the intended binding `HMAC-verified bytes == identity used for authorization`, allowing any actor who can obtain one validly-signed webhook body (e.g. by installing the app on their own store and triggering an event) to replay that exact body to the same public callback URL with a forged `shop-domain` header, causing the receiving application to process/attribute the event as coming from an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `HmacValidator.validate` signs/verifies exactly this signable string against `Context.api_secret_key`: [2](#0-1) .

However, `Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all read directly from HTTP headers that are never part of the signed content: [3](#0-2) .

`Registry.process` only checks the body HMAC before dispatching to the app-supplied handler with these unauthenticated values: [4](#0-3) .

The gem's own documentation tells integrators that `data.shop` is "The shop domain of the webhook" and that `Registry.process` "will verify the request did indeed come from Shopify" [5](#0-4) , and the reference handler example uses `data.shop` directly as the tenant key to enqueue work (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`) [6](#0-5) . This strongly implies host applications are expected to trust `data.shop` as an authenticated tenant identifier once `process` succeeds — but the gem never actually binds that value to the cryptographic signature.

**Binding that should hold:** `shop header value == shop cryptographically bound in the signed payload`. In reality: `HMAC verifies raw_body only`, while `shop (and topic/webhook_id/api_version) are read from unauthenticated headers`, so the equality does not hold.

### Impact Explanation
Any actor able to install the target app on a store they control (a normal, unprivileged step for any Shopify merchant/developer) can capture one legitimately Shopify-signed webhook body for a topic the app subscribes to. Because the signature never covers the `shop-domain` header, that same `(raw_body, hmac)` pair remains valid when replayed to the app's public callback endpoint with the `shop-domain` header changed to a victim shop that also has the app installed. `Registry.process` will accept the forged request and hand the handler a `WebhookMetadata` claiming to originate from the victim shop [7](#0-6) . Any host application that follows the documented pattern and uses `data.shop` to look up the victim's stored session/access token or to key business logic will process attacker-controlled data under the victim's tenant context — a cross-tenant integrity/isolation break, matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires no privileged credentials: only installing the target app on any store (attacker's own) to obtain one valid signed body, then replaying it with a modified header to the app's public webhook endpoint. This is entirely within reach of an ordinary internet-facing attacker with no `api_secret_key`, access token, or social engineering needed.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the value that is HMAC-verified, or otherwise cryptographically bind them (e.g., have `HmacValidator`/`VerifiableQuery` sign a canonicalized string composed of body + these headers), and reject the request if any of them cannot be validated. At minimum, update `to_signable_string` in `lib/shopify_api/webhooks/request.rb` so the shop/topic/id/version cannot be forged independently of the signed payload, and update the docs/handler example to warn against trusting `data.shop` without additional verification if this is not fixed.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled dev store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST body and its `X-Shopify-Hmac-Sha256` header from the real Shopify request.
2. Replay the exact captured body and HMAC header to the same webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers [8](#0-7) , `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` [2](#0-1) , and `Registry.process` invokes the handler with `shop: "victim.myshopify.com"` [4](#0-3)  — despite the request never having been sent by Shopify for `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
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
