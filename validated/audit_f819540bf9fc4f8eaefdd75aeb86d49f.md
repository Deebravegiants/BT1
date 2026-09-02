### Title
Webhook `shop` (tenant) field is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string solely from the raw request body, while the `shop` (and `topic`/`api_version`/`webhook_id`) values used to identify the tenant are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body-based HMAC and then hands the header-derived `shop` straight to the app's webhook handler as if it were verified, breaking the equality `shop authenticated == shop trusted by handler`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `Webhooks::Request#shop` (and `topic`, `api_version`, `webhook_id`) are pulled from headers that are never part of that signed string: [2](#0-1) 

`Utils::HmacValidator.validate` verifies exactly this signable string against the configured secret: [3](#0-2) 

`Registry.process` then trusts `request.shop` as the tenant identity and forwards it, unmodified, into the app handler's `WebhookMetadata`: [4](#0-3) 

The library's own documentation instructs developers that `Registry.process` "will verify the request did indeed come from Shopify" and that the resulting `data.shop` is "The shop domain of the webhook," encouraging handlers to key business logic (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) directly off this value: [5](#0-4) [6](#0-5) 

Because the HMAC only binds the body bytes, any actor who possesses one genuinely-signed webhook body+HMAC pair for the app (e.g. a merchant who installed the app and received one legitimate webhook to their own endpoint) can replay that exact `raw_body`/`hmac-sha256` header pair while substituting an arbitrary `shopify-shop-domain` header value. `Registry.process` will still consider the HMAC valid (it only checks the body) and will invoke the handler with the attacker-chosen `shop`, breaking the binding between "HMAC-authenticated bytes" and "tenant identity acted upon."

### Impact Explanation
This is a cross-tenant access vector (Critical): an app whose webhook handler uses `data.shop` to scope database writes/reads (the exact pattern shown in this gem's own documentation) can be tricked into applying a webhook payload meant for one shop against a different shop's data, without needing that other shop's access token, `client_secret`, or any privileged credential — only a body/HMAC pair the attacker already legitimately received for their own installation.

### Likelihood Explanation
Any merchant who installs the app is, by design, sent genuine webhooks (body + valid HMAC) for their own shop by Shopify. Capturing one such request (e.g., from their own webhook endpoint logs) is trivial and requires no elevated access, no `api_secret_key`, and no interception of another tenant's traffic — only replay with a modified header value that this gem never authenticates.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the verified body (e.g., re-deriving/confirming the shop via a separately authenticated channel, such as looking up the shop tied to the webhook subscription/session rather than trusting the header). At minimum, document prominently that `data.shop` is unauthenticated and must not be used as a sole tenant-scoping key.

### Proof of Concept
1. App receives a legitimate Shopify webhook for `victim-shop.myshopify.com`:
   - `raw_body = '{"id":1}'`
   - `shopify-hmac-sha256: <valid HMAC over raw_body>`
   - `shopify-shop-domain: victim-shop.myshopify.com`
2. Attacker (who owns their own shop `attacker-shop.myshopify.com` and has captured one of their own genuine webhook deliveries with the *same raw body content*, e.g. an empty/`{}` payload topic) replays the request to the app's webhook endpoint but sets:
   - `shopify-shop-domain: victim-shop.myshopify.com` (or any other shop)
   - keeps the original valid `hmac-sha256` (still valid since it only signs the body)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` → passes because only `raw_body` is checked, per `lib/shopify_api/utils/hmac_validator.rb` and `lib/shopify_api/webhooks/request.rb`.
4. `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` is invoked with `shop = "victim-shop.myshopify.com"`, even though the request was not authenticated for that shop.

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
