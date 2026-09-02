This confirms the root cause: `ShopifyAPI::Webhooks::Registry.process` documents itself as verifying "the request did indeed come from Shopify" via `Utils::HmacValidator.validate(request)`, but that validator only signs `request.to_signable_string`, which returns `@raw_body` alone — the `shop`, `topic`, `webhook_id`, and `api_version` header fields are passed straight into `WebhookMetadata` unauthenticated.

### Title
Webhook `shop` attribution is not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw JSON body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC over that signable string and then forwards the header-derived `shop` value unchanged to the app's handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop attributed to a webhook == shop whose secret produced the HMAC over the entire authenticated payload`. Instead, the binding actually enforced is only `HMAC(raw_body) == received_hmac`, with `shop` (and `topic`/`webhook_id`/`api_version`) taken from `shopify-shop-domain` and sibling headers that are never included in `to_signable_string` [4](#0-3) .

Because every shop that has this app installed shares the same `Context.api_secret_key` for HMAC computation [5](#0-4) , an unprivileged user who legitimately controls their own shop (a normal merchant/dev-store installer of the app) receives real, validly-signed webhook deliveries for their own shop. Since the signature only covers the body, that same attacker can replay the identical body+HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) header value. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because the body/HMAC pair is genuine [6](#0-5) , and then constructs `WebhookMetadata` with the attacker-controlled `shop` field [7](#0-6) , [8](#0-7) .

The documentation explicitly tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" before invoking their handler with `data.shop` [9](#0-8) , and shows a typical handler dispatching per-shop background work keyed directly off `data.shop` [10](#0-9) . Host applications following this documented contract have no way to independently re-verify shop attribution, since the gem presents `shop` as already-authenticated data.

### Impact Explanation
Any host application that keys per-tenant side effects (job dispatch, database writes, cache invalidation, order/inventory sync, etc.) off `WebhookMetadata#shop` as instructed by the gem's own documentation is exposed to cross-tenant data injection: a user with a legitimate install on Shop A can forge webhook deliveries that the app attributes to Shop B, using nothing but a genuine webhook they received for their own store. This is a cross-tenant boundary violation reachable by any unprivileged app installer, without needing the app's `client_secret` or any other shop's credentials.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple/untrusted merchants: obtaining a valid body+HMAC pair requires only installing the app on one's own store (a normal, unprivileged action) and triggering any subscribed webhook topic, then replaying it with a modified `shop` header to the app's public webhook endpoint.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed content verified for webhook requests, or otherwise cryptographically bind them to the delivery (e.g., validate the callback path/shop against the registration on record rather than trusting the header), so `WebhookMetadata#shop` cannot be forged independently of the HMAC-covered body.

### Proof of Concept
1. App is installed on Shop A (`a.myshopify.com`) and Shop B (`b.myshopify.com`), both configured against the same app `client_secret`.
2. Attacker controls Shop A and receives a genuine webhook delivery: headers `x-shopify-shop-domain: a.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`, plus `raw_body`.
3. Attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers [11](#0-10) ; `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the (unchanged) HMAC [6](#0-5) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "b.myshopify.com", ...)` [3](#0-2) , causing the app to process Shop A's webhook content as if it belonged to Shop B.

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
