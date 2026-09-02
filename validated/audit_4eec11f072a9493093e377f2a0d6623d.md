### Title
Webhook `shop` (and `topic`/`webhook_id`) header is trusted as the tenant identity but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's HMAC over the raw request body only, then unconditionally trusts the `shop-domain` HTTP header (along with `topic` and `webhook-id`) as the authoritative tenant identity passed to the host application's handler. Because the HMAC signature never covers these headers, an attacker who can obtain one valid `(body, hmac)` pair for their own shop can replay it to the same public endpoint with an arbitrary `shop-domain` header, causing the host app to process the payload as if it originated from a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are all read directly from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` verifies only the HMAC over that body, then immediately hands `request.shop` (and `request.topic`, `request.webhook_id`) to the registered handler as trusted identity fields: [3](#0-2) 

`Utils::HmacValidator.validate` computes/compares the signature purely from `verifiable_query.to_signable_string` (i.e., the body) and the app's `api_secret_key`/`old_api_secret_key`: [4](#0-3) 

This breaks the intended binding: `shop header used by host app == shop that produced/authorized this signed body`. In reality the HMAC only proves `body == body signed by the app's secret at some point`; it says nothing about which shop the header claims to be. The gem's own documentation reinforces the false assumption that `Registry.process` "will verify the request did indeed come from Shopify" (implying the whole request, including shop attribution, is authenticated): [5](#0-4) 

and explicitly instructs handlers to treat `data.shop` as the trusted shop domain of the webhook: [6](#0-5) [7](#0-6) 

### Impact Explanation
An attacker who installs the app on their own store (an ordinary, unprivileged action requiring no secret key or leaked credential) can legitimately trigger a webhook for their own shop and capture the resulting `(raw_body, hmac)` pair. Since the same public webhook endpoint is shared across all tenants and the signature check ignores the `shop-domain`, `topic`, and `webhook-id` headers, the attacker can replay that exact body/HMAC to the endpoint while substituting the `shop-domain` header of any victim shop that also uses the app. `Registry.process` will accept the HMAC as valid (it matches the body) and dispatch `WebhookMetadata` with the attacker-forged `shop` to the host handler, causing the application to process attacker-controlled event data attributed to a different tenant — a cross-tenant confusion that can lead to state corruption, incorrect authorization decisions, or data leakage in any host app that keys per-tenant logic off `data.shop` (as this gem's own documentation instructs).

### Likelihood Explanation
Likelihood is high for any adopter following the documented pattern: the attack requires only (1) the ability to install the target app on an attacker-controlled shop — the normal, unprivileged onboarding flow — and (2) knowledge of the victim's `myshopify.com` domain, which is not secret. No access to `api_secret_key`, access tokens, or any privileged account is required.

### Recommendation
Bind the `shop`, `topic`, and `webhook_id` values into the signed material that `HmacValidator` verifies (or otherwise cryptographically bind them to the body/signature), rather than trusting them as free-form headers. At minimum, update `docs/usage/webhooks.md` to make explicit that `Registry.process` only authenticates body integrity, not the shop/topic/webhook_id headers, and require host applications to cross-check `data.shop` against an independently known, per-installation identifier (e.g. the shop tied to the specific registered webhook subscription) before trusting it for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and lets it register an HTTP webhook (e.g. `orders/create`) pointing at the shared endpoint `POST /callback/orders/create`.
2. Attacker triggers the event on their own store, capturing the real request Shopify sends, including body `B` and header `x-shopify-hmac-sha256: H` (valid for `B` under the app's `api_secret_key`, per `HmacValidator.validate` / `Registry.process`: [8](#0-7) ).
3. Attacker resends the identical `B`/`H` to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`), all of which are read verbatim from headers with no cryptographic binding: [9](#0-8) .
4. `Registry.process` accepts the request (HMAC still matches `B`) and calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, causing the host application to act on attacker-supplied data as though it belongs to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L1-12)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Webhooks
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
