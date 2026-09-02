### Title
Webhook `shop` identity not covered by HMAC verification enables cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate` succeeds, and the docs explicitly state this "will verify the request did indeed come from Shopify." In reality the HMAC only covers the raw request body — the `shop` identity that the handler receives and acts on comes from an unauthenticated header that is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no relation to what was signed: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e. the body only) and compares it to the `hmac` field, so the check never touches `shop`: [3](#0-2) 

`Registry.process` gates all processing on this HMAC check, then forwards `request.shop` unchanged into `WebhookMetadata` handed to the app's handler as the authoritative tenant identifier: [4](#0-3) 

The identity binding that should hold is: `HMAC-valid(raw_body) == (topic, shop, body) all originated together from Shopify for that shop`. In fact the equality that actually holds is only `HMAC-valid(raw_body) == raw_body originated from Shopify for *some* shop that shares this app's `client_secret``; `shop` is an independent, unauthenticated field. Because every shop that installs the app shares the same `api_secret_key` (the app's `client_secret`, not a per-shop secret), a legitimate webhook captured for shop A retains a valid HMAC when replayed with the `shop-domain` header rewritten to shop B — the signature is unaffected because it never depended on that header.

The library's own documentation reinforces the false guarantee, describing `Registry.process` as verifying "the request did indeed come from Shopify" (implying the whole payload, including `shop`) and shows the sample handler using `data.shop` directly as the tenant key (`shop_domain: data.shop`): [5](#0-4) [6](#0-5) 

### Impact Explanation
This is a cross-tenant identity-binding break entirely within the gem's own verification path: an app that follows the documented API and trusts `data.shop` as the tenant identifier (exactly as the docs' example does) processes webhook data attributed to the wrong shop. An unprivileged installer of the app (any merchant, i.e. an "unprivileged internet user" relative to other tenants) can capture one authentic webhook delivery for their own store and replay it to the app's shared webhook endpoint with the `x-shopify-shop-domain` header swapped to a victim shop, since `HmacValidator` never checks that header. Depending on how the app keys its per-shop state off `data.shop`, this enables cross-tenant data confusion/corruption — writing or triggering actions against a shop the attacker does not control.

### Likelihood Explanation
Requires only that the attacker be a legitimate installer of the target app (no special privilege, no access token, no `client_secret`), be able to capture one raw webhook body+HMAC pair delivered to their own store, and replay it with a modified header to the app's public webhook endpoint. No cryptographic secret needs to be recovered.

### Recommendation
Do not treat `request.shop` as trusted merely because `HmacValidator.validate` passed. Either (a) include the shop domain (and topic) in the signed material used for verification, or (b) require callers to cross-check `request.shop` against a shop for which the app already holds a stored, previously-authenticated session/installation record before acting on the webhook, and update `docs/usage/webhooks.md` to stop implying the entire payload (including `shop`) is verified.

### Proof of Concept
1. App installs on `shop-a.myshopify.com` and registers an `orders/create` webhook.
2. Shopify delivers a genuine webhook to the app's endpoint with body `B`, `x-shopify-hmac-sha256: HMAC(secret, B)`, and `x-shopify-shop-domain: shop-a.myshopify.com`.
3. The merchant who owns `shop-a` (a normal, unprivileged app user) intercepts this request and replays it to the same endpoint, changing only `x-shopify-shop-domain` to `shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` and `Registry.process` call `HmacValidator.validate`, which recomputes `HMAC(secret, B)` — unchanged — and passes: `lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/registry.rb:188-190`.
5. The registered handler receives `WebhookMetadata` with `shop == "shop-b.myshopify.com"` even though the payload actually originated from `shop-a`, per `lib/shopify_api/webhooks/registry.rb:198-199` and `lib/shopify_api/webhooks/request.rb:20-23`.

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
