### Title
Webhook shop/topic/webhook_id identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `ShopifyAPI::Utils::HmacValidator.validate` and `ShopifyAPI::Webhooks::Registry.process` only verify that the body matches the HMAC computed with the app's secret — they never bind the `shop-domain` header (or the other headers) to that signature. An unprivileged attacker who legitimately installs the app on their own store can capture a genuine `(body, hmac)` pair from their own webhook deliveries and replay it against the app's webhook endpoint with an arbitrary `shop-domain` header, causing the app to process the attacker's payload as if it came from a victim shop.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and the identity fields consumed by handlers come straight from headers with no cryptographic binding: [2](#0-1) 

`HmacValidator.validate_signature` computes the digest strictly over `verifiable_query.to_signable_string` (the raw body) and compares it to the received HMAC, never incorporating `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` treats a passing HMAC check as proof the whole webhook — including `request.shop` — is authentic, then hands `request.shop` straight to the app's handler: [4](#0-3) 

The documented equality the gem promises is: `shop header used for tenant routing == shop authenticated by the Shopify HMAC`. In reality the HMAC only authenticates the byte content of the body; it says nothing about which shop sent it. Any attacker capable of obtaining one valid `(raw_body, hmac)` pair for their own app installation — which is inherent to legitimately installing the app and receiving webhooks — can resend that exact body/HMAC pair with a forged `x-shopify-shop-domain` (and forged `x-shopify-topic`/`x-shopify-webhook-id`) to the app's webhook route. `HmacValidator.validate` reports success because the body/HMAC pair is genuinely valid, and `Registry.process` forwards the attacker-chosen `shop` to the handler as though it were verified.

This is not host-application misuse: the gem's own documentation instructs developers to route on `data.shop` after calling `Registry.process`, presenting the HMAC check as sufficient proof of authenticity for the whole webhook, including the shop field: [5](#0-4) [6](#0-5) 

### Impact Explanation
This breaks the tenant isolation boundary the gem is supposed to provide for webhook processing: it satisfies the "Critical - cross-tenant access" bar because an unprivileged attacker (who only needs the ability to install the app on their own store, a normal merchant capability) can make the app believe fabricated body content originated from any other shop. Depending on the handler logic recommended in the docs (e.g., enqueuing jobs keyed by `data.shop`), this can be used to inject falsified order/product/customer webhook payloads attributed to a victim's shop, corrupting per-tenant data or triggering shop-scoped business logic for a shop the attacker does not control and has no credentials for.

### Likelihood Explanation
Likelihood is high for any app that follows the gem's documented webhook pattern verbatim. No secrets, tokens, or privileged access are required — only the ability to install the app once (or otherwise obtain one legitimate `body+hmac` pair, which Shopify sends to every installer) and then send a crafted HTTP POST with different headers to the app's own public webhook endpoint.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-verified signable content, or otherwise cryptographically bind them to the payload (e.g., verify that `shop` is a known-installed shop *and* that the specific `webhook_id`/topic pairing is one the app actually registered for that shop) before trusting `request.shop`/`WebhookMetadata#shop` in `Registry.process`. Update `Request#to_signable_string` and `HmacValidator` accordingly, and adjust the documentation to no longer claim the whole request "did indeed come from Shopify" when only the body is authenticated.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`), as any merchant can.
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>` and some JSON body the attacker fully controls (attacker can shape order fields on their own store).
3. Attacker records this `(raw_body, hmac)` pair.
4. Attacker sends a new POST to the same webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and finds it matches — validation succeeds.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, so the app processes attacker-controlled data as though it belongs to `victim-shop`, per the flow in [4](#0-3) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L12-30)
```markdown
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
