This confirms the vulnerability path: the docs explicitly state `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" — but the HMAC only covers the raw body, and the `shop` value trusted by handlers comes from an unauthenticated header.### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, but the `shop` value the gem hands to the app's handler is read from an HTTP header that is never included in that signature. Anyone who can obtain one valid `(body, HMAC)` pair for the app (e.g. an attacker who legitimately installed the app on their own store) can replay that exact body/signature to the app's public webhook endpoint while substituting an arbitrary `shop-domain`/`x-shopify-shop-domain` header, and the gem will report the forged shop to the handler as authenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop` directly from the `shop-domain` header without any cryptographic binding: [1](#0-0) 

The `to_signable_string` used for HMAC verification is only the raw body, not the headers: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which calls `to_signable_string` (body only) and `hmac` (from the header), and then unconditionally passes `request.shop` — the unauthenticated header value — into `WebhookMetadata` given to the handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes/compares the HMAC purely against `verifiable_query.to_signable_string`: [4](#0-3) 

This breaks the identity binding `authenticated_shop == shop_used_by_handler`: the equality only holds for the body content, not for the shop that the gem asserts the webhook belongs to. The gem's own documentation asserts that `Registry.process` "will verify the request did indeed come from Shopify" and that handlers can trust `data.shop` as "The shop domain of the webhook": [5](#0-4) [6](#0-5) 

But that guarantee does not extend to the `shop` field, since it is never part of the signed content.

### Impact Explanation
This is a cross-tenant identity-confusion vulnerability: an unprivileged internet user who has legitimate access to their own store (and therefore receives real, validly-signed webhooks from Shopify for topics whose body is attacker-influenced or replayable, e.g. `app/uninstalled`, `shop/update`, or any webhook whose body content the attacker controls or can predict) can forge webhook deliveries that the host application will attribute to a different shop. Any host app that follows the documented pattern (`perform_later(topic:, shop_domain: data.shop, webhook: data.body)` as shown in the gem's own docs) will process attacker-supplied data under a victim tenant's identity — e.g., triggering data deletion/redaction flows, marking a victim shop as uninstalled, or corrupting shop-scoped state keyed by `data.shop`. This matches the "cross-tenant access" impact class.

### Likelihood Explanation
High: no special access is required beyond the ability to install the app on an attacker-controlled Shopify store (a normal, unprivileged action) and the ability to POST arbitrary headers to the app's public webhook endpoint. No `api_secret_key`, access token, or privileged credentials are needed — the attacker reuses a genuine signature that Shopify itself generated for the attacker's own store's webhook, since the header carrying the tenant identity sits entirely outside the signed content.

### Recommendation
Bind the shop identity into the authenticated content, or otherwise cryptographically or contextually verify it before trusting it:
- Include the `shop-domain` header (and ideally `topic`, `api-version`, `webhook-id`) as part of the signable string used in HMAC validation, or
- Require the caller of `Registry.process` to supply the expected shop (e.g., resolved from the route/session) and assert it matches `request.shop` before invoking the handler, rejecting on mismatch.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g. `shop/update`).
2. Shopify sends a legitimately-signed webhook to the app's endpoint:
   ```
   POST /callback/shop/update
   x-shopify-topic: shop/update
   x-shopify-hmac-sha256: <valid HMAC over body>
   x-shopify-shop-domain: attacker.myshopify.com
   Body: {"id": 1, ...}
   ```
3. Attacker captures this exact `(body, HMAC)` pair and replays it directly to the same public endpoint, changing only the header:
   ```
   POST /callback/shop/update
   x-shopify-topic: shop/update
   x-shopify-hmac-sha256: <same valid HMAC, unchanged body>
   x-shopify-shop-domain: victim.myshopify.com
   Body: {"id": 1, ...}   # identical, unmodified body
   ```
4. `ShopifyAPI::Webhooks::Request.new` parses this successfully; `Utils::HmacValidator.validate` succeeds because it only checks the unmodified raw body against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:12-22`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` invokes the handler with `WebhookMetadata` whose `shop` is `"victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`, `lib/shopify_api/webhooks/request.rb:20-23`), even though Shopify never sent any webhook about `victim.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
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
