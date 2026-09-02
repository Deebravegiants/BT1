### Title
Webhook shop-domain identity not bound to HMAC signature enables cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw body, but the `shop` identity that the gem hands to the app's handler (used by the documented API as the tenant key) is taken from an HTTP header that is never covered by that HMAC. This breaks the expected binding `authenticated(shop) == used(shop)`, mirroring the reported bug class where a field is acted upon without being covered by the integrity check.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` extracted from the `shopify-hmac-sha256` / `x-shopify-hmac-sha256` header: [2](#0-1) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is completely outside the signed material: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately constructs `WebhookMetadata` using `request.shop` (the unauthenticated header) and hands it to the app-provided handler: [4](#0-3) 

The gem's own documentation instructs apps to key tenant-specific work directly off `data.shop` returned from this exact flow — this is the gem's own supported contract, not a case of the host app ignoring the API: [5](#0-4) [6](#0-5) 

The equality that should hold is:
`shop_that_the_HMAC_proves_this_body_came_from == shop_the_gem_passes_to_the_handler`

Because `to_signable_string` never includes `shop`, this equality is not enforced by the gem. Before the attack: a legitimate webhook for shop A has header `x-shopify-shop-domain: A.myshopify.com` and a valid HMAC over its body. After the attack: the attacker (any merchant/tenant that has installed the app, since `HmacValidator.validate` only proves the body was signed with the app's secret — it does not prove which shop the webhook is "for") captures a webhook they legitimately receive for their own shop A, and replays the identical `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header to shop B's domain. `HmacValidator.validate` still returns `true` (only `raw_body` is checked), and `Registry.process` will invoke the handler with `data.shop == "B.myshopify.com"` and `data.body` equal to A's data — a cross-tenant identity mix-up entirely internal to the gem's authentication step.

### Impact Explanation
This is a cross-tenant boundary violation reachable by an unprivileged internet user who is merely a legitimate/malicious merchant of the app (no access token, no `api_secret_key`, no privileged account required — they only need any webhook of their own, which every installed shop legitimately receives). Any host application following the gem's documented pattern of keying shop-scoped operations (session lookup, GDPR redaction, uninstall cleanup, order processing, billing side effects, etc.) off `data.shop` will attribute attacker-controlled data/events to an arbitrary victim shop of the attacker's choosing. This satisfies the "cross-tenant access" Critical-impact category defined in scope, since the identity binding that the HMAC is supposed to enforce (which tenant this authenticated payload belongs to) is not actually enforced by the gem.

### Likelihood Explanation
High. No secrets are required beyond having any shop install the target app (a standard, low-privilege action). The attacker only needs to capture one of their own real webhook deliveries (trivial, since they control their own endpoint/network path or can simply log the raw request) and resend it with a different `shop-domain` header value — the endpoint code path shown in the gem's own usage example performs no additional shop verification before calling the handler.

### Recommendation
Bind the `shop` field into the HMAC-verified material, or otherwise cryptographically tie the shop domain to the signed body before it is trusted:
- Include the `shop-domain` (and ideally `webhook-id`/`topic`) header values in `to_signable_string`, matching the same fields Shopify signs the payload against, so `HmacValidator.validate` fails if the shop header is altered independent of the body.
- Alternatively (or in addition), require and validate that the `shop` used downstream match an app-controlled record established during OAuth/installation for that specific webhook id, rather than trusting the unauthenticated header outright.
- Document explicitly in `docs/usage/webhooks.md` that `data.shop` is not covered by HMAC verification if this remains unresolved, so integrators do not use it as an authenticated tenant key.

### Proof of Concept
1. App installs on shop A; app registers `orders/create` webhook.
2. Shopify sends webhook to app's endpoint for shop A:
   ```
   POST /webhook
   x-shopify-topic: orders/create
   x-shopify-shop-domain: shop-a.myshopify.com
   x-shopify-hmac-sha256: <valid-hmac-of-raw-body-with-app-secret>
   body: {"id": 123, "note": "A's order"}
   ```
3. Attacker (who legitimately controls shop A, or intercepts this delivery) resends the exact same body and HMAC header to the app's endpoint, only changing:
   ```
   x-shopify-shop-domain: shop-b.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request object; `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only (per `to_signable_string`) and it matches — `Registry.process` proceeds.
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: {"id": 123, "note": "A's order"}, ...))`, per [7](#0-6) , causing shop A's order data to be processed and stored under shop B's tenant context in any host app following the documented pattern.

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

**File:** docs/usage/webhooks.md (L10-29)
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
