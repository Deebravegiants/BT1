### Title
Webhook `shop` domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Request#shop` is read from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header. `ShopifyAPI::Webhooks::Registry.process` validates only that the body+HMAC pair is authentic, then trusts the header-derived `shop` value when building the `WebhookMetadata` passed to the app's handler. Because the same `api_secret_key` is shared across every shop that has installed the app, any tenant who has installed the app can capture one legitimate body+HMAC pair for their own shop and replay it with an arbitrary `shopify-shop-domain` header, producing a request that this gem reports as verified for a shop it never came from.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` is defined to be just the raw body — the shop domain is excluded from what's signed: [2](#0-1) [3](#0-2) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` and then unconditionally forwards `request.shop` into `WebhookMetadata`, which is handed to the app's handler as the authoritative tenant identifier: [4](#0-3) 

The documentation for this feature explicitly tells integrators that calling `Registry.process` "will verify the request did indeed come from Shopify," and shows `data.shop` being used directly to route/attribute the webhook (e.g. `perform_later(shop_domain: data.shop, ...)`): [5](#0-4) [6](#0-5) 

The identity binding broken is:
`hmac == HMAC(secret, raw_body)` proves only `raw_body` is authentic; it does **not** prove `shop == request.shop`. The gem treats `verified(raw_body)` as if it implied `verified(shop)`, but `shop` is parsed from a header that is completely outside the signed payload.

### Impact Explanation
Because a single app-level `api_secret_key` is used to validate webhooks for *every* installed shop, any attacker who has legitimately installed the app on their own shop (a normal, unprivileged action) can:
1. Trigger a real webhook to their own endpoint (or otherwise obtain a genuine `raw_body` + `hmac-sha256` pair for their shop).
2. Replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim's shop domain, or a shop the attacker never installed on).
3. `HmacValidator.validate` still returns `true` (only the body is checked), and `Registry.process` calls the handler with `WebhookMetadata#shop` set to the attacker-chosen value.

Any app that uses `data.shop` to scope database writes, trigger per-tenant business logic, or select which merchant record to update will act on forged, cross-tenant data — this is a cross-tenant access/spoofing primitive stemming entirely from this gem's webhook verification not binding the shop identity to the signature.

### Likelihood Explanation
Likelihood is high for any app with more than one merchant installed: obtaining one valid `(raw_body, hmac)` pair only requires being a legitimate (even free/trial) installer of the target app — no special credentials, leaked secrets, or privileged access are required. Because `shop` is a plain header, forging it is trivial with any HTTP client.

### Recommendation
Include the shop domain (and other routing-relevant headers like topic/webhook-id) in the signed material, or otherwise cryptographically bind them, e.g. by having `to_signable_string`/`hmac` computation incorporate a canonical string of `shop + topic + raw_body`, or by requiring callers to independently verify that `request.shop` corresponds to a shop with an active, registered webhook subscription (looked up server-side) before trusting it, rather than treating `Registry.process`'s success as proof that the declared shop is authentic.

### Proof of Concept
```ruby
# Attacker owns/installed the app on "attacker-shop.myshopify.com" and receives
# a real webhook, capturing:
raw_body = '{"id":1,"note":"legit order"}'
hmac_header = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# Attacker resends the identical body/HMAC but claims it's from the victim shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac_header),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # never installed the app, no secret involved
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) is true because only raw_body is signed;
#    the handler receives data.shop == "victim-shop.myshopify.com"
```

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
