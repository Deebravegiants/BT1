## Title
Webhook shop/topic/webhook-id identity is trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the **raw request body**. The `shop`, `topic`, `webhook_id`, and `api_version` values that the host application uses to attribute and route the webhook data are all pulled from **HTTP headers that are never included in the signed material**, so an attacker who has one legitimately-signed `(body, hmac)` pair can replay it while swapping the shop-domain header to impersonate any other merchant.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`to_signable_string` returns only `@raw_body`. Every other attribute exposed by the request object — `shop`, `topic`, `webhook_id`, `api_version` — is read directly from HTTP headers via `shopify_header`, entirely outside the HMAC's coverage: [2](#0-1) [3](#0-2) 

`HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` (i.e., the raw body) against the `hmac` field: [4](#0-3) 

`Registry.process` relies on this validation and then immediately trusts `request.shop` (an unauthenticated header) to build the `WebhookMetadata` that is handed to the app's own handler: [5](#0-4) 

The library's own documentation tells integrators that `Registry.process` "will verify the request did indeed come from Shopify" and that handlers should key business logic off `data.shop` (e.g., `shop_domain: data.shop`), i.e. `shop` is treated as an authenticated tenant identifier: [6](#0-5) [7](#0-6) 

This is the same bug class as the reported analog: a value that a downstream consumer treats as authenticated/bound (the withdrawal's full set of L2 messages; here, the webhook's shop/topic identity) is not actually covered by the cryptographic check that is supposed to bind it (`ParseMessagePassed`'s single-event assumption; here, HMAC over body-only). The broken identity equality is:

`HMAC-verified bytes (raw body)` ≠ `bytes that determine tenant identity (shop/topic/webhook_id headers)`

### Impact Explanation
Any endpoint that exposes `ShopifyAPI::Webhooks::Registry.process` to the internet (as documented, a plain Rails controller reading `request.raw_post` and `request.headers`) can be sent a forged HTTP request: take a body+HMAC pair that is valid for the attacker's *own* shop (trivially obtainable by installing the app on a free/dev store and capturing one real webhook, since the attacker legitimately owns that shop and its secret-derived HMAC is delivered to them), then replay the exact same body and HMAC to the merchant's webhook endpoint with `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) set to a **victim** shop the attacker does not control. `Utils::HmacValidator.validate` passes because it only checks the body bytes, and `Registry.process` dispatches the handler with `shop: <victim-shop>` and attacker-chosen `body`. Any host application that scopes tenant data, deletion flows, or state transitions by `data.shop` (which is exactly what the gem's own docs instruct) will act on attacker-supplied data under a different tenant's identity — a cross-tenant integrity/confidentiality violation.

### Likelihood Explanation
Exploitation requires no secrets beyond what the attacker already legitimately possesses for their own store (they receive valid webhook bodies+HMACs from Shopify for their own installation) and only crafted HTTP headers, which any unprivileged internet user can send to a public webhook endpoint. The gem does nothing to bind headers to the signature, so this is reliably reproducible against any app that follows the documented integration pattern.

### Recommendation
Include the tenant-identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body (e.g., verify the request against Shopify's per-webhook shop registration/session rather than trusting the header), so that a replayed body cannot be re-attributed to an arbitrary shop.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's shared secret), `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker sends a POST to the merchant app's public webhook endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and desired `X-Shopify-Topic`).
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` succeeds because it only hashes `B`.
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, and the host app processes attacker-controlled data as if it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
