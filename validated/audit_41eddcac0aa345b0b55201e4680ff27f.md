## Title
Webhook shop-tenant spoofing via unauthenticated `shop-domain` header not covered by HMAC - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then unconditionally trusts the `X-Shopify-Shop-Domain` header to identify which merchant/tenant the payload belongs to. Because the header is never part of the signed bytes, any caller who can produce (or reuse) a body+HMAC pair valid for the shared app secret can relabel that payload as belonging to an arbitrary victim shop, breaking the binding `authenticated_bytes == acted_upon_tenant`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, however, is read straight from the client-supplied `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not part of that signed string: [2](#0-1) 

`Registry.process` validates the HMAC over the body via `Utils::HmacValidator.validate(request)`, and, once that (body-only) check passes, forwards `request.shop` unchanged into `WebhookMetadata`, which is delivered to the host app's handler as the authoritative tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes/compares the digest exclusively over `verifiable_query.to_signable_string`, i.e. the raw body, using the single app-wide `Context.api_secret_key` (the same secret is used for every shop installed on the app — it is not shop-specific): [4](#0-3) 

Consequently: `hmac_valid(body) == true` does **not** imply `shop_header == originating_shop`. An attacker who legitimately installs the app on their own shop ("Shop A") will receive Shopify-signed webhooks (valid body + hmac, signed with the same `api_secret_key` shared by all installs of that app). They can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain ("Shop B"). The HMAC check still passes (it never inspected the header), and `Registry.process` hands the handler a `WebhookMetadata` claiming the payload is for Shop B.

This is exactly the documented, expected usage pattern of the gem — the gem's own docs instruct developers to trust `data.shop` as the tenant key: [5](#0-4) 
and describe `Registry.process` as verifying "the request did indeed come from Shopify": [6](#0-5) 
— but the verification never binds the shop identity to that guarantee.

### Impact Explanation
This crosses a tenant boundary: an attacker who is a legitimate (unprivileged, non-victim) user of the app on their own store can forge webhook events attributed to a different merchant. Depending on which topics the host app subscribes to (mandatory topics such as `customers/redact`, `shop/redact`, `customers/data_request`, or app-specific topics like `app/uninstalled`, `orders/paid`), this can trigger cross-tenant side effects — e.g. spoofing data-erasure/redaction requests against a victim shop, or injecting fabricated business data attributed to another merchant — without ever needing the victim's credentials or access token. This matches the "cross-tenant access" impact class.

### Likelihood Explanation
Requires only that the attacker (a) install the same app on a shop they control, which is unprivileged/normal usage, and (b) be able to send an HTTP request with a forged header to the app's public webhook endpoint. No `api_secret_key`, access token, or victim credentials are needed — the only "credential" involved (`api_secret_key`) is legitimately possessed by the app, not the attacker, and it is shared across all installs, which is what allows the replay to validate.

### Recommendation
Bind the shop identity into the signed material or otherwise cryptographically tie the header claim to the verified payload:
- Include the `shop-domain` header value in `to_signable_string`, or
- Cross-check `request.shop` against a shop that's independently derivable from `@raw_body` (e.g., a `shop_id`/`shop_domain` field inside the verified JSON body when present), rejecting the webhook if they disagree, and document that host apps must not trust header-derived shop identity in isolation.

### Proof of Concept
1. App is installed on attacker-controlled shop `attacker.myshopify.com`; Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's shared `api_secret_key`), header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures this request and replays it to the same app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com`, keeping body `B` and header `H` identical.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (== `B`) and compares to `H` — passes, since neither depends on the shop header.
4. `request.shop` returns `"victim.myshopify.com"` (attacker-controlled), and `WebhookMetadata.new(... shop: request.shop ...)` is passed to the host app's `handler.handle`, which — per the gem's documented pattern — trusts `data.shop` as the tenant for which the event applies, thereby processing a forged event for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
