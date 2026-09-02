### Title
Webhook `shop` (and `topic`/`webhook_id`) fields are trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC signature validated by `Utils::HmacValidator.validate` in `Registry.process` never covers the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers. `Registry.process` nonetheless treats `request.shop` as the authenticated tenant identifier and hands it straight to the app's webhook handler via `WebhookMetadata`.

### Finding Description
`lib/shopify_api/webhooks/request.rb` defines the `shop`, `topic`, `api_version`, and `webhook_id` accessors purely from HTTP headers: [1](#0-0) 

Notice `to_signable_string` (line 36-38) returns `@raw_body` only — none of the header-derived fields are part of the signed content.

`Utils::HmacValidator.validate` computes the signature strictly over `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build `WebhookMetadata`, which is passed to the app-supplied handler as the shop-of-record for the event: [3](#0-2) 

The identity binding this breaks: `HMAC-covered-bytes(raw_body)` ≠ `authenticated-tenant(shop-domain header)`. The signature only proves the **body bytes** were produced with the app's secret; it proves nothing about which shop the body belongs to, yet the gem/documentation instructs the host application to key all tenant-scoped side effects (`data.shop`) off this unauthenticated header: [4](#0-3) [5](#0-4) 

### Impact Explanation
Any actor who can obtain one legitimately-signed `(raw_body, hmac)` pair for the app — e.g., by installing the app on their own free/dev store and letting Shopify deliver a real webhook to the endpoint (which is publicly reachable) — can replay that exact body and HMAC value while substituting an arbitrary `shopify-shop-domain` header value for a victim shop. Because `to_signable_string` never incorporates the shop header, `Registry.process` still calls `Utils::HmacValidator.validate` successfully, and the handler receives `WebhookMetadata(shop: "<victim-shop>", body: <attacker's own event payload>)`. Any host application that uses `data.shop` (as literally shown in the gem's own documented usage example, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) to select which tenant's records to update will process attacker-controlled data under a victim tenant's identity — a cross-tenant data-injection/spoofing primitive that satisfies the "cross-tenant access" impact bar, since the shop boundary that the app relies on this gem to enforce is not actually authenticated.

### Likelihood Explanation
Low-to-moderate effort: the attacker needs no leaked secret, no privileged account, and no TLS interception — only the ability to install the target app on any shop they control (including a free development store) to receive one genuinely signed webhook, then replay it directly to the app's public webhook endpoint with a forged `shop-domain` header. Webhook endpoints are, by design, unauthenticated public HTTP endpoints that rely solely on this HMAC check for trust.

### Recommendation
- **Short term:** Extend `Webhooks::Request#to_signable_string` (or `Registry.process`) to bind the `shop`, `topic`, and `webhook_id` values into the material that is authenticated, or otherwise cross-check the `shop-domain` header against an independently-verified value (e.g., a shop already associated with the specific webhook subscription/session) before constructing `WebhookMetadata`.
- **Long term:** Document explicitly, and enforce in the library, that `shop` in `WebhookMetadata` is not cryptographically bound to the payload, and provide an API that returns a verified shop identity for webhook processing so host applications cannot inadvertently trust a spoofable header as a tenant key.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers a subscribed webhook topic (e.g. `orders/create`), letting Shopify deliver it to the app's public webhook endpoint. Attacker captures the raw POST body `B` and header `x-shopify-hmac-sha256: H`, which is valid because `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker sends a new POST request to the same public webhook endpoint with the same body `B` and same `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` — matching `H` because the body was untouched.
4. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's payload>, topic: ..., webhook_id: ...)`, ` [3](#0-2) ` causing the host app to attribute attacker-controlled webhook content to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
