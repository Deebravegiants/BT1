### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking the HMAC over the raw request body, then hands the handler a `shop` value taken from the `X-Shopify-Shop-Domain` HTTP header — a value that is never included in the signed content. An attacker who possesses any single valid `(body, hmac)` pair signed with the app's shared secret (e.g. from webhooks delivered to their own store, since the webhook secret is the app's `client_secret`/`api_secret_key`, not per-shop) can resend that exact body/HMAC pair while substituting the `shop-domain` header with a victim shop's domain, and the check still passes.

### Finding Description
`Registry.process` gates all further processing on the HMAC check alone: [1](#0-0) 

The HMAC is computed only over `to_signable_string`, which for a webhook `Request` is the raw body: [2](#0-1) 

The `shop` field consumed by the handler comes straight from the `shopify-shop-domain` header, which is not part of the signed material: [3](#0-2) 

`HmacValidator.validate` confirms only that the body matches an HMAC computed with `Context.api_secret_key`; it makes no assertion about which shop the header claims: [4](#0-3) 

The broken identity binding is: `shop authenticated by HMAC` (nothing — the HMAC authenticates the app’s secret and the body bytes only) vs. `shop trusted and forwarded to the handler as the tenant key` (`request.shop`, taken from an unsigned header). Because Shopify signs webhooks with the app-wide secret (the same `api_secret_key` for every shop that installs the app, not a per-shop key), any merchant who installs the public app on their own store legitimately receives valid `(body, hmac)` pairs. They can then replay that body and HMAC to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain; `Utils::HmacValidator.validate` still returns `true` because it only checks the body against the signature, and `Registry.process` passes the attacker-chosen `shop` straight into `WebhookMetadata`, which the docs explicitly describe as "The shop domain of the webhook" and instruct app authors to use as the tenant key: [5](#0-4) 

The docs even claim that `Registry.process` "will verify the request did indeed come from Shopify," which is only true for the body, not for the shop attribution: [6](#0-5) 

### Impact Explanation
This breaks the tenant boundary the gem is documented to guarantee: an unprivileged internet user who can install the app on their own (attacker-controlled) store can forge webhook deliveries that the app's own handler will attribute to any other shop by domain. Any host application following the documented pattern (using `data.shop` to key session/data lookups, enqueue jobs, or trigger merchant-specific side effects) will process attacker-supplied body content under a victim shop's identity — a cross-tenant data-integrity/cross-tenant access issue reachable without any credentials belonging to the victim.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on a store the attacker controls (any unprivileged Shopify Partner/dev account), (2) capturing one legitimate webhook body+HMAC pair sent to that store (trivial, they receive their own webhooks), and (3) POSTing that exact body/HMAC to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at the victim. No secret material belonging to the victim or the app is needed. This is a low-effort, reliably reproducible attack path.

### Recommendation
Bind the shop identity to the verified content. Either:
- Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed material rather than trusting an unsigned header, or
- Cross-check `request.shop` against the shop associated with the specific webhook subscription/session that was registered (e.g., look up the webhook by `webhook_id` and compare the originating shop) before invoking the handler, or
- At minimum, clearly document in `docs/usage/webhooks.md` that `data.shop` is NOT authenticated by the HMAC and must not be used as a trust boundary without additional verification, and provide/require a hook in `Registry.process` for host apps to authenticate `shop` against known subscriptions.

### Proof of Concept
1. Attacker registers a free store `attacker.myshopify.com` and installs the victim's public app, causing Shopify to POST a legitimate webhook, e.g.:
   ```
   POST /callback/orders/create
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC over body, signed with app's api_secret_key>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   Body: {"id": 1, ...attacker-controlled order data...}
   ```
2. Attacker replays the identical body and `X-Shopify-Hmac-Sha256` header, but changes:
   ```
   X-Shopify-Shop-Domain: victim.myshopify.com
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — using `lib/shopify_api/utils/hmac_validator.rb`, this passes because it only checks the (unchanged) body against the (unchanged) HMAC.
4. The handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com", body: <attacker-controlled JSON> ...)` per `lib/shopify_api/webhooks/registry.rb` line 198, and any host app following the documented pattern in `docs/usage/webhooks.md` will process attacker data under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
