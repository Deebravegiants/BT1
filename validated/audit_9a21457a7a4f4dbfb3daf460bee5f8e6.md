This confirms the vulnerability. The library explicitly documents that `Registry.process` "will verify the request did indeed come from Shopify" as a whole, but the actual verification logic only covers the raw body bytes, not the `shop`, `topic`, `webhook_id`, or `api_version` header values that get passed to the app's handler as trusted tenant-identification data.

### Title
Webhook `shop`, `topic`, and `webhook_id` headers are trusted for tenant attribution without being covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC of the raw request body against the `X-Shopify-Hmac-Sha256` header. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — which are handed to the app's handler as authoritative, per-tenant identity data — are never included in the signed bytes, so their authenticity is never actually verified.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` with: [1](#0-0) 

`hmac` is read from the `hmac-sha256` header, but `to_signable_string` returns only `@raw_body` — the `topic`, `shop-domain`, `webhook-id`, and `api-version` headers are excluded from the signable string entirely.

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it with `OpenSSL.secure_compare`: [2](#0-1) 

`Registry.process` uses only this body-only HMAC check as its entire authenticity gate, then immediately forwards the unverified `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` header values straight to the app's handler as trusted tenant/event metadata: [3](#0-2) 

This breaks the identity binding: `hmac_valid(headers, body) == hmac_valid(body)`, while the app's handler is invoked as if `shop == authenticated_shop`. The gem's own documentation instructs developers to treat `data.shop` as the authoritative shop identity for attributing webhook effects to a specific merchant/tenant: [4](#0-3)  and explicitly claims `Registry.process` "will verify the request did indeed come from Shopify": [5](#0-4) 

Because only the body bytes are signed, any attacker who can obtain one validly-signed webhook body (e.g., by installing the app on their own shop and letting Shopify send them a legitimately-signed webhook, since request bodies for a given topic/shape are often attacker-influenceable or replayable) can resend that exact `raw_body` + `hmac` pair to the app's public webhook endpoint while substituting the `shop-domain` (and/or `topic`, `webhook-id`) headers. `HmacValidator.validate` will still pass because it only checks the body, and `Registry.process` will dispatch the handler with the attacker-chosen `shop` value, causing the host app to attribute the webhook's data/effects to a different (victim) tenant.

### Impact Explanation
This is a cross-tenant identity-binding failure: the equality the gem is supposed to guarantee — `authenticated_source == attributed_shop` — does not hold, because `attributed_shop` is taken from an unauthenticated header while `authenticated_source` only certifies the body. Any host application that uses `data.shop` (as the docs instruct) to route webhook effects to per-tenant storage/state can be made to apply a legitimately-signed payload to the wrong shop's data, a cross-tenant access/integrity violation.

### Likelihood Explanation
Exploitability requires the attacker to possess at least one validly HMAC-signed raw body for the target topic. This is realistically obtainable by installing the app on an attacker-controlled development/trial store and capturing Shopify's legitimate webhook delivery, since the webhook endpoint is a public HTTP route by design and headers are attacker-controlled once the request is replayed outside of Shopify's original delivery.

### Recommendation
Include the `shop-domain`, `topic`, `webhook-id`, and `api-version` header values in the HMAC-signed material (or otherwise cryptographically bind them to the body, e.g., by validating the shop domain against a known session/store before acting, and/or asking Shopify's webhook signing scheme to cover headers), so that `HmacValidator.validate` cannot pass unless the header values that are subsequently trusted for tenant attribution are exactly the ones Shopify actually sent.

### Proof of Concept
1. Install the target app on an attacker-owned shop `attacker.myshopify.com` and trigger a webhook (e.g. `orders/create`) so Shopify legitimately signs body `B` with `HMAC(client_secret, B) = H`.
2. Capture `B` and `H` from the delivered request.
3. Send a new HTTP POST to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but header `x-shopify-shop-domain: victim.myshopify.com` (and/or a different `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request#hmac` returns the (still-valid) decoded `H`; `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` only and it matches, so validation passes.
5. `Registry.process` invokes the registered handler with `shop: "victim.myshopify.com"`, `body: parsed_body(B)`, causing the host app to process attacker-supplied data as if it originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
