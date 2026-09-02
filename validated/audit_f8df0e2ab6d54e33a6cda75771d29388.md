### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`/`webhook_id`) values used by `Registry.process` and handed to app handlers as the trusted tenant identity are read from unauthenticated HTTP headers. This breaks the intended binding: `verified(body) == true` should imply `shop == the tenant that owns this signed payload`, but the gem's design allows `verified(body) == true` with `shop` set to any attacker-chosen value.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signable content: [2](#0-1) 

`Registry.process` validates only the body's HMAC and then unconditionally forwards the header-derived `shop` (along with `topic`, `api_version`, `webhook_id`) to the app's handler as trusted metadata: [3](#0-2) 

`HmacValidator.validate` only checks that the HMAC over `to_signable_string` (the raw body) matches the app's secret; it has no knowledge of or binding to the `shop` header: [4](#0-3) 

The gem's own documentation confirms that after `Registry.process` "verifies" the request, `data.shop` is meant to be trusted as the tenant identity by the host application (e.g., used to key background jobs): [5](#0-4) [6](#0-5) 

**Broken equality**: `HmacValidator.validate(request) == true` is meant to imply `request.shop == the tenant whose secret verified the payload`. In reality `validate` only checks `HMAC(raw_body, api_secret_key) == received_hmac`; `request.shop` is an independent, unauthenticated header value.

### Impact Explanation
An unprivileged internet user can create their own Shopify development store, install the target app on it, and trigger any webhook topic the app subscribes to (e.g. `orders/create`, `app/uninstalled`, `customers/data_request`). Shopify will deliver a webhook with a body fully controlled/observable by the attacker and a valid `X-Shopify-Hmac-Sha256` signed with the app's real `client_secret`. The attacker can then replay the identical `raw_body` and `hmac` header to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks body/secret consistency, and `Registry.process` will invoke the handler with `shop` set to the victim's domain and `body` fully attacker-controlled. Any host application following the gem's documented pattern (keying jobs/state/session lookups off `data.shop`) will process attacker-supplied data under another merchant's identity — a cross-tenant confusion that can lead to spurious uninstall/reinstall handling, incorrect data mutation, or fraudulent GDPR-style requests attributed to the victim shop.

### Likelihood Explanation
Requires only: (1) the ability to install the target app on a shop the attacker controls (any developer/free Shopify store, no privileged credentials needed), and (2) sending one crafted HTTP request with a captured body+HMAC pair and a modified header — well within reach of any unprivileged internet user, and does not require the `api_secret_key` or any leaked credential.

### Recommendation
Bind the shop identity to the verified payload instead of trusting a bare header: include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (matching what Shopify itself signs, if supported) or, at minimum, cross-check the header-derived `shop` against an independent trusted source (e.g., the shop stored for the corresponding session/access token) before invoking the handler. At the very least, document prominently that `data.shop` is not cryptographically authenticated and must not be used as a sole tenant key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers `orders/create` (or any subscribed topic).
2. Shopify sends: `POST /callback/orders/create` with `X-Shopify-Hmac-Sha256: <valid-hmac>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, body `B`.
3. Attacker captures `B` and `<valid-hmac>` and replays: `POST /callback/orders/create` with the same body `B`, same `X-Shopify-Hmac-Sha256: <valid-hmac>`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — this validates `B` against the app secret and passes [7](#0-6) .
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed(B) ...)`, even though the payload actually originated from and was signed for `attacker-shop.myshopify.com` [8](#0-7) .

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

**File:** docs/usage/webhooks.md (L123-135)
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
