### Title
Webhook shop-domain (and topic) identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb, lib/shopify_api/utils/hmac_validator.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from unauthenticated HTTP headers when invoking the app's handler. Because those identity fields are never included in the signed material, any shop that can obtain one genuinely-signed webhook (i.e., any app installer, an unprivileged actor from the app's perspective) can replay that same signed body while substituting an arbitrary `shop-domain` header, causing the app to process attacker-controlled data as if it belonged to a different (victim) tenant.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` verifies authenticity with: [1](#0-0) 

The HMAC check calls into `Utils::HmacValidator.validate`, which computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw HTTP body — none of the Shopify headers are part of the signed content: [3](#0-2) 

Yet `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from those same unauthenticated headers and handed to the handler as trusted tenant identity: [4](#0-3) [5](#0-4) 

The identity binding that should hold is:
`shop-domain used by handler == shop-domain that Shopify actually cryptographically vouched for`

But the implementation only proves:
`hmac(secret, raw_body) == received_hmac`

with `shop-domain` entirely excluded from `raw_body`'s coverage. This is exactly the "field acted on but not covered by the HMAC" bug class: the field consumed by application logic (`data.shop`) is disjoint from the field actually authenticated (only `@raw_body`).

The gem's own documentation reinforces that host apps are expected to trust `data.shop` as an authenticated identifier without further checks — it is described simply as "The shop domain of the webhook" and used directly (e.g., `shop_domain: data.shop`) in the sample handler with no guidance to cross-check it: [6](#0-5) [7](#0-6) 

Since `Context.api_secret_key` (the app's client secret) is the single shared signing key used for every tenant's webhooks, any shop that installs the app receives real, validly-HMAC-signed webhook deliveries. An attacker who controls one such installed shop can capture a genuine `(raw_body, hmac)` pair delivered to the app's shared webhook route, then re-send that exact body/HMAC pair to the same endpoint with the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`) header rewritten to name a victim shop. `HmacValidator.validate` still passes because it never inspected the header, so `Registry.process` invokes the handler with `WebhookMetadata` claiming the victim's shop while carrying attacker-chosen body content.

### Impact Explanation
This breaks tenant isolation: the handler receives forged tenant identity (`shop`) alongside attacker-controlled payload data, all backed by a cryptographically "valid" signature check. Depending on how the host app's handler uses `data.shop` (e.g., to look up the victim's stored access token/session and perform follow-up API actions, or to write/redact/react on the victim's records), this enables cross-tenant data confusion or cross-tenant actions taken under the victim's identity — matching the "cross-tenant access" Critical impact category, since a legitimate handler design (as documented by this gem) has no way to distinguish this forged request from a genuine one.

### Likelihood Explanation
Any actor who can install the app on a shop they control (a normal, unprivileged step for any Shopify app) can obtain one authentic `(body, hmac)` pair for their own shop and immediately reuse it against the shared webhook endpoint with a modified shop header, with no need to know `api_secret_key` or perform any cryptographic attack. The only prerequisite is the ability to install the app and observe the raw body Shopify sends it — no privileged credentials are required.

### Recommendation
Include the transport-level tenant identifiers (`shop`, and ideally `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise bind the header-derived `shop` to a value independently confirmed for that installation (e.g., cross-check `request.shop` against the shop stored for the session/access token used to originally register the webhook) before constructing `WebhookMetadata` and invoking the handler in `Registry.process`.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify POSTs a request to the app's shared webhook route with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Capture `(B, H)` (e.g., from the attacker's own request logs/proxy on infrastructure they control, or by intercepting on their own inbound network path).
3. Re-send an HTTP request to the same webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only checks `B` against `H`; `Registry.process` in `lib/shopify_api/webhooks/registry.rb` (lines 188-199) then calls the handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed(B) ...)`, i.e., the handler processes attacker-controlled data attributed to the victim shop.

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
