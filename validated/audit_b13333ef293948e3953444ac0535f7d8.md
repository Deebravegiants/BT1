Confirmed the vulnerability. I have sufficient evidence to write up the finding.

### Title
Webhook shop-domain is trusted for tenant identity but is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) attributes purely from unauthenticated HTTP headers, while `to_signable_string` — the data actually protected by the HMAC signature — only covers the raw request body. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then forwards `request.shop` straight into the `WebhookMetadata` object delivered to the app's handler, without ever binding that shop value to the signed payload.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` (etc.) HTTP headers with no integrity check: [2](#0-1) 

`Registry.process` validates only the HMAC over the body, then trusts `request.shop` as the tenant identifier passed to the app-supplied handler: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — since `to_signable_string` is body-only, this validation is entirely independent of the `shop`, `topic`, or `webhook_id` header values: [4](#0-3) 

The library's own docs describe `Registry.process` as verifying "the request did indeed come from Shopify," which developers reasonably read as authenticating the whole webhook, including which shop it is for: [5](#0-4) 

and the documented handler contract explicitly treats `data.shop` as a trustworthy per-tenant field to key off of (e.g., `shop_domain: data.shop`): [6](#0-5) 

Because the app's API secret key is shared across every shop that installs a multi-tenant app, any shop owner installing the app is a legitimate holder of correctly-HMAC'd `(raw_body, hmac)` pairs generated for their own store's events. Since the header carrying the shop identity is not part of the signed material, an attacker who owns a shop can take a genuine, correctly signed webhook body they legitimately receive (or can trigger) for their own store, and directly POST it to the app's public webhook endpoint again with the `shop-domain` header (and/or `webhook-id`/`topic`) rewritten to name a victim shop. `Utils::HmacValidator.validate` still returns `true` because the signature only certifies the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the victim's `shop` value, breaking the equality that the app relies on: *the shop that authenticated the HMAC == the shop stored/acted upon by the handler.*

### Impact Explanation
This breaks the tenant/identity binding between "who Shopify authenticated this payload for" and "who the app's handler believes the data belongs to," which the report's "Rules" classify as Critical (cross-tenant access). A downstream app that keys off `data.shop` to route webhook effects to a specific merchant's record (exactly as shown in this gem's own documentation) can be made to apply an attacker-controlled shop's data/event under a victim shop's identity, or vice versa — e.g. forging an `app/uninstalled` or `shop/redact` event, or injecting attacker-controlled order/product data attributed to a victim's store record.

### Likelihood Explanation
Any user who can install the app on their own (even free/development) Shopify store obtains legitimately signed `(body, hmac)` pairs for events they trigger themselves, and the app's webhook endpoint is a public HTTP(S) endpoint by design (per the docs' Rails example, it just calls `Registry.process` on whatever `raw_body`/`headers` arrive). No `api_secret_key`, access token, or privileged access is required — only the ability to send an HTTP POST with attacker-chosen headers, which is squarely an "unprivileged internet user" capability.

### Recommendation
Bind the tenant-identifying headers (`shop`, and ideally `topic`/`webhook_id`) into the signed material verified by `HmacValidator`, or otherwise require the caller/host app to cross-check `request.shop` against an expected/allow-listed shop for the webhook route before trusting it. At minimum, document prominently that `Registry.process` only authenticates the body and that `data.shop` must not be trusted as tenant-authenticated without an independent binding (e.g., correlating against a known session/shop record via `webhook_id`/topic-specific expectations).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a genuine webhook (e.g. `orders/create`) delivered by Shopify to the app's public webhook URL, with body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker captures `B` and `H` (e.g., by using a reverse proxy/logging endpoint they control in front of their own installation, or by using a topic/body they can predict/replicate).
3. Attacker sends a new POST directly to the app's public webhook endpoint with the same body `B`, the same `X-Shopify-Hmac-Sha256: H` header, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` only checks `B` against `H`.
5. `ShopifyAPI::Webhooks::Registry.process(request)` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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
