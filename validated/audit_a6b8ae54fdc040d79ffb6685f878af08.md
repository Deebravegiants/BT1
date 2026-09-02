## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `#shop` is read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header. `Registry.process` validates the HMAC over the body only, then forwards the header-derived `shop` to the application's webhook handler as the authenticated tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`shop` is pulled straight from a header, and `to_signable_string` only returns the raw body: [1](#0-0) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) using the app's single, shop-independent `api_secret_key`: [2](#0-1) 

`Registry.process` checks only this body-based HMAC, then hands the attacker-controllable `shop` header straight to the app's handler as trusted tenant metadata: [3](#0-2) 

The documented usage pattern explicitly tells integrators that `Registry.process` "will verify the request did indeed come from Shopify," and passes `data.shop` on to application logic (e.g. `shop_domain: data.shop`) without any further check: [4](#0-3) [5](#0-4) 

**Identity binding broken as an equality:**
`shop_authenticated_by_gem` (the value the host app trusts as the webhook's tenant, via `WebhookMetadata#shop`) is expected to equal `shop_that_produced_the_HMAC`. In reality, the HMAC is computed only over `@raw_body` with the app's single shared `api_secret_key`; the `x-shopify-shop-domain` header is not part of the signed material at all, so `shop_authenticated_by_gem` can be set to any value independent of which shop's secret/body actually produced the signature.

Because `api_secret_key` is one value shared by the app across every merchant installation (it is not shop-specific), any actor who has legitimately received one valid `(raw_body, hmac)` pair from Shopify (e.g., by installing the app on their own store — an ordinary, unprivileged action) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `HmacValidator.validate` will still pass because it never inspects the header, and `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop domain alongside the attacker's own (but validly-signed) body content.

### Impact Explanation
This breaks the tenant identity boundary the gem is supposed to enforce for webhook processing: it lets an unprivileged app-installer impersonate any other shop when the gem hands off "verified" webhook data to the host application. Per the documented usage pattern, this shop value is treated as trusted (e.g., used as `shop_domain` to look up/act on that tenant's data), so this is a cross-tenant confusion vector rooted entirely in the gem's own body-only HMAC scheme.

### Likelihood Explanation
Requires only that the attacker be a legitimate (even trial/free) merchant with the app installed on their own shop, so they can capture at least one authentic `(raw_body, hmac)` pair generated with the shared `api_secret_key`, then replay it to the public webhook endpoint with a forged shop header. No access token, `api_secret_key`, or privileged account is needed.

### Recommendation
Bind the shop identity into the signed material (or otherwise cryptographically tie the `x-shopify-shop-domain` header to the HMAC), and/or require `Registry.process`/`WebhookMetadata` to cross-check the header-derived shop against an out-of-band verified value (e.g., the shop tied to the webhook subscription that Shopify's delivery infrastructure guarantees) rather than trusting an unsigned header as the tenant identity.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering a real webhook delivery with body `B` and a valid `hmac = HMAC_SHA256(api_secret_key, B)`.
2. Attacker POSTs to the app's public webhook endpoint with the same raw body `B` and `hmac`, but sets header `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request; `HmacValidator.validate` succeeds because it only checks `B` against `hmac` [6](#0-5) .
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim-shop.myshopify.com"` [7](#0-6) .
5. The host app, following the documented pattern, processes the (attacker-supplied) body as belonging to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** docs/usage/webhooks.md (L125-136)
```markdown
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
