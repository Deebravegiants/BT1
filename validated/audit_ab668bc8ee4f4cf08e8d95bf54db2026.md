This is exactly the identity-binding gap the report's bug class targets: `shop` (and `topic`/`webhook_id`) are read straight from HTTP headers in `ShopifyAPI::Webhooks::Request#shop` (`lib/shopify_api/webhooks/request.rb:20-23`), while the HMAC that `Utils::HmacValidator.validate` checks in `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-190`) is computed only over `to_signable_string`, which returns `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`). The header-derived `shop` is never part of the signed bytes, so an attacker who can produce one HMAC-valid `(body, hmac)` pair (trivially, from their own shop's genuine webhook) can replay that exact body/hmac to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `Registry.process` will accept it and dispatch `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: ..., ...)` (`lib/shopify_api/webhooks/registry.rb:190-199`) with the attacker-chosen `shop`, `topic`, and `webhook_id`, none of which were authenticated.

### Title
Webhook `shop`/`topic`/`webhook_id` are trusted from unauthenticated headers while HMAC only covers the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from HTTP headers, but `to_signable_string` (used by `Utils::HmacValidator.validate` in `Registry.process`) signs only the raw body. This breaks the binding `shop_authenticated == shop_delivered_to_handler`.

### Finding Description
`Registry.process` validates the request solely via `Utils::HmacValidator.validate(request)` [1](#0-0) , and `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` [2](#0-1) . For webhooks, `to_signable_string` returns only `@raw_body` [3](#0-2) , while `shop`, `topic`, and `webhook_id` are read directly from attacker-controllable HTTP headers with no cryptographic tie to the signature [4](#0-3) . After signature validation succeeds, `Registry.process` builds `WebhookMetadata` using these unauthenticated header values and passes them straight to the app's registered handler [5](#0-4) . Because any given `(raw_body, hmac)` pair is valid for *any* combination of headers, an attacker who obtains one legitimate webhook delivery (e.g., from their own store, or any store they can trigger a webhook against) can capture that body+HMAC and replay it to the app's public webhook endpoint with a forged `x-shopify-shop-domain`/`x-shopify-topic`/`x-shopify-webhook-id`, and the gem will treat it as a fully authenticated webhook for the victim shop/topic.

### Impact Explanation
Handlers are documented to key business logic off `data.shop` (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [6](#0-5) . Because `shop` is unauthenticated, this enables cross-tenant confusion: attacker-controlled body content can be delivered to the app under an arbitrary victim shop identity and topic, letting an attacker inject/replay data as if it came from a different merchant's store, which the report's bug-class scope calls out as cross-tenant access.

### Likelihood Explanation
The webhook receiver is by design a public, unauthenticated internet endpoint (`docs/usage/webhooks.md` shows the controller performs no additional check before calling `Registry.process`) [7](#0-6) . Obtaining one valid `(body, hmac)` pair only requires triggering any real webhook once (e.g., installing the app on an attacker-owned dev store), after which the header fields can be freely rewritten for replay. No access token, `api_secret_key`, or privileged account is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material for webhooks (mirroring the OAuth `AuthQuery#to_signable_string`, which signs `code`, `host`, `shop`, `state`, and `timestamp` together [8](#0-7) ), or otherwise cryptographically bind these header values to the signed body so header substitution invalidates the signature.

### Proof of Concept
1. Register/observe a legitimate webhook delivery for shop `attacker-shop.myshopify.com`, capturing `raw_body` and `x-shopify-hmac-sha256`.
2. Replay a POST to the victim app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`/`x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [9](#0-8) .
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker's body, despite the request never having been authenticated for that shop [10](#0-9) .

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L128-135)
```markdown
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
