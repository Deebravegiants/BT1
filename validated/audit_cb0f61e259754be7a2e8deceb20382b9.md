The library documents that `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" based on `ShopifyAPI::Webhooks::Request`, and the `data.shop` field is explicitly documented and handed to app handlers as "The shop domain of the webhook" for tenant identification.### Title
Webhook `shop-domain`, `topic` and `webhook-id` headers are trusted for tenant routing but are excluded from HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the shop identity (`shop-domain`), `topic`, and `webhook-id` are taken from unauthenticated HTTP headers and passed straight through to the application's webhook handler. `ShopifyAPI::Webhooks::Registry.process` verifies only that the body's HMAC is valid for *some* previously-received payload; it never binds that signature to the header values that determine which tenant/topic the event is attributed to.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors read directly from HTTP headers that are never part of the signed message: [2](#0-1) 

`Registry.process` validates the HMAC of the body via `Utils::HmacValidator.validate(request)`, then immediately looks up the handler by `request.topic` and forwards `request.shop`, `request.parsed_body`, `request.api_version`, and `request.webhook_id` to the app's handler without any additional binding check: [3](#0-2) 

`HmacValidator.validate` only proves `HMAC(secret, raw_body) == received_hmac`; it says nothing about which shop or topic that body was originally sent for: [4](#0-3) 

The gem's own documentation confirms that `data.shop` — sourced from this unauthenticated header — is the field apps are expected to use for tenant identification when persisting/queuing webhook data: [5](#0-4) 
and that `Registry.process` is documented to "verify the request did indeed come from Shopify": [6](#0-5) 

This creates a broken identity binding: the equality the app relies on is `hmac_valid(body) ⟺ shop_header_trustworthy`, but in reality `hmac_valid(body)` only proves `body` bytes are unmodified — the `shop-domain` header (and `topic`/`webhook-id`) are never part of the signed bytes. Any unprivileged internet user who has legitimately installed the target app on their own store (a normal, free, unprivileged action — no `api_secret_key`, access token, or leaked credential required) will receive a genuinely-signed `(raw_body, hmac)` pair for their own shop. Because the HMAC covers only the body, that exact `(raw_body, hmac)` pair remains valid when replayed directly against the app's public webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header rewritten to name a different, victim shop — no TLS interception, MITM, or credential theft is needed, since the attacker crafts and sends the HTTP request themselves.

### Impact Explanation
This is a cross-tenant identity-binding break: it lets an unprivileged attacker (any merchant who has installed the app, or anyone who has ever observed one delivered webhook body+signature for a given topic) make the app process arbitrary attacker-chosen bodies as if they originated from an arbitrary victim shop of the attacker's choosing. Downstream, apps typically use `data.shop` to select which merchant record/session/queue to write into (per this gem's own documented usage pattern), so this can lead to cross-tenant data confusion/injection into another merchant's data pipeline — satisfying the "cross-tenant access" Critical impact category, since the identity the app trusts for a request is not actually authenticated.

### Likelihood Explanation
Likelihood is high for any app that (a) allows any merchant to install it (standard for public Shopify apps) and (b) uses `data.shop`/`data.topic`/`data.webhook_id` from `WebhookMetadata` to route/store data as documented, since that is exactly the intended and documented usage of this API. The attacker only needs their own installed instance of the target app to obtain one valid `(raw_body, hmac)` pair for a topic whose body carries no shop-specific secret (many webhook payloads, e.g. `app/uninstalled`, carry little or no shop-identifying content in the body itself, making replay against another shop trivial), then send a forged HTTP POST directly to the app's public webhook endpoint with a modified `shop-domain` header.

### Recommendation
Include the trusted identity fields (`shop-domain`, and ideally `topic`/`webhook-id`) in the HMAC-signed message, or otherwise cryptographically bind them to the body signature, rather than relying on unauthenticated headers for tenant attribution. At minimum, document prominently that `data.shop`/`data.topic`/`data.webhook_id` are NOT covered by the HMAC check and must not be trusted for tenant/topic routing without additional verification (e.g., cross-checking against the shop's currently registered webhook subscriptions/session store).

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store (no special privilege required).
2. Trigger a webhook delivery for a topic whose body is not shop-specific (e.g. `app/uninstalled`), capturing the raw body and the `x-shopify-hmac-sha256` header Shopify sends — this HMAC is valid because `Request#to_signable_string` only signs `@raw_body`, per `lib/shopify_api/webhooks/request.rb` lines 35-38.
3. Replay this exact `(raw_body, hmac)` pair via a direct HTTP POST to the target app's public webhook endpoint, but set `x-shopify-shop-domain` to the victim shop's domain (and, if desired, a different `x-shopify-webhook-id`/`x-shopify-topic` matching a registered handler).
4. `ShopifyAPI::Webhooks::Registry.process` (lib/shopify_api/webhooks/registry.rb lines 188-200) calls `Utils::HmacValidator.validate(request)`, which succeeds because the body+secret HMAC matches, then invokes the app's handler with `shop: request.shop` set to the attacker-chosen victim domain — the app now processes attacker-controlled data as if it came from the victim shop.

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

**File:** docs/usage/webhooks.md (L10-26)
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
