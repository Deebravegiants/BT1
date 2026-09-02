### Title
Webhook `shop` (and `topic`/`webhook-id`/`api_version`) headers are not covered by HMAC verification, allowing shop-spoofing on replayed webhooks - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` accepts any request whose body HMAC validates and then forwards the header-derived `shop` value to the app's handler as `WebhookMetadata.shop`, without it ever being covered by the signature. This breaks the identity binding `shop authenticated == shop the app acts on`.

### Finding Description
`Request#hmac` decodes the `hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`Request#shop` is read from the `shop-domain` header, which is never included in the signed string: [3](#0-2) 

`Utils::HmacValidator.validate` only compares the computed HMAC of `to_signable_string` (i.e., the body) against the received signature — it never touches `shop`, `topic`, `webhook_id`, or `api_version`: [4](#0-3) 

`Registry.process` uses `Utils::HmacValidator.validate(request)` as the sole authenticity check, then builds `WebhookMetadata` directly from the request's header-derived `shop`, `topic`, `webhook_id`, and `api_version`, handing it to the app's handler as trusted data: [5](#0-4) 

The documented API explicitly describes `process` as verifying "the request did indeed come from Shopify," and instructs apps to use `data.shop` to key business logic (e.g., `shop_domain: data.shop`), reinforcing that `shop` is meant to be a trusted, authenticated field: [6](#0-5) [7](#0-6) 

The binding broken: the app assumes `shop (validated by HMAC) == shop (acted upon by handler)`. In reality, only the body is bound by the HMAC; the `shop-domain` header is unauthenticated and freely attacker-controllable on any replayed, previously-valid webhook request.

### Impact Explanation
An unprivileged actor who can capture (or is the recipient of, e.g. via their own store's real webhook deliveries) one genuinely-signed webhook request for shop A can replay that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header with shop B's domain. `HmacValidator.validate` still passes because it never checks the header, and `Registry.process` will invoke the handler with `WebhookMetadata.shop == "shop-B"` while the body content actually belongs to shop A. Any host application that scopes actions (data updates, cache invalidation, orders/customers/inventory sync, GDPR/mandatory-topic side effects) by `data.shop` as documented will attribute attacker-influenced, cross-tenant data to a shop the attacker does not own — a cross-tenant access/integrity violation crossing the shop trust boundary that this gem is responsible for enforcing via `process`.

### Likelihood Explanation
Any merchant using the app receives legitimately signed webhooks for their own store on a routine basis (webhooks fire continuously for normal storefront/checkout activity), giving an attacker-merchant a steady supply of valid body+HMAC pairs to replay with a forged shop header — no secret material is needed. The mechanics require only intercepting/replaying an HTTP request the attacker already legitimately receives and editing one header value, which is straightforward and repeatable.

### Recommendation
Bind `shop` (and ideally `topic`, `webhook_id`, `api_version`) into the HMAC-verified surface: either include these header values in `to_signable_string`/verification, or have `Registry.process` independently corroborate the header-derived `shop` against verified session state / a body-embedded shop identifier (many Shopify webhook payloads carry `"shop_id"`/domain fields for cross-check) before constructing `WebhookMetadata`. At minimum, document clearly that `data.shop` is not signature-protected, since the current docs and code both suggest it is a verified value.

### Proof of Concept
1. App registers `WebhookHandler` for topic `orders/create`; handler does `perform_later(shop_domain: data.shop, webhook: data.body)` per `docs/usage/webhooks.md`.
2. Attacker (a merchant installed on shop `attacker-shop.myshopify.com`) receives a genuine Shopify webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret), header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the identical request to the app's webhook endpoint, keeping body `B` and `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com"})` is constructed; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and matches `H` — validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)` (`lib/shopify_api/webhooks/registry.rb:188-200`), causing the app to process attacker-supplied webhook content under victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
