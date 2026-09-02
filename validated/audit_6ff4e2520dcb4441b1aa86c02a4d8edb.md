### Title
Webhook `shop` attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates only the raw request body against the `X-Shopify-Hmac-Sha256` signature, then forwards the `shop` (and `topic`, `webhook_id`, `api_version`) values taken from unauthenticated HTTP headers to the app's webhook handler as if the whole request had been verified. Because these header fields are not part of the signed bytes, an attacker who has ever obtained one valid `(body, hmac)` pair can replay it while swapping the `shop-domain` header to a victim shop, and the signature still validates. This is the same bug class as the referenced report: a field the code acts on (`shop`) is not the field actually covered by the cryptographic check (`hmac` over `raw_body` only).

### Finding Description
`Request#hmac`/`Request#to_signable_string` binds the signature check exclusively to `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`HmacValidator.validate` computes/compares the HMAC using only `verifiable_query.to_signable_string`, i.e. only the body: [3](#0-2) 

`Registry.process` performs exactly this body-only check, then immediately trusts `request.shop` (an unauthenticated header) to build the `WebhookMetadata` that is handed to the app's handler: [4](#0-3) 

The gem's own documentation asserts a stronger guarantee than what is implemented — that `process` "will verify the request did indeed come from Shopify" — and explicitly tells integrators to key their downstream work off `data.shop`: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `shop authenticated == shop the HMAC actually covers`. In this code, `shop` used to build `WebhookMetadata` is only equal to the header value, not to any value bound by the signature — the two are conflated even though the header is fully attacker-controlled on replay.

### Impact Explanation
Since the signature only covers the body, any previously captured `(raw_body, hmac)` pair — trivially obtainable by an attacker who owns their own development/test shop and can generate arbitrary legitimate webhook deliveries signed with the real `client_secret` — can be replayed to the shared webhook endpoint with an arbitrary `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header. `HmacValidator.validate` will accept it because it never looks at those headers, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim shop domain. Any host application that follows the documented pattern (using `data.shop` to select the tenant record to update, e.g. `perform_later(shop_domain: data.shop, webhook: data.body)`) will act on attacker-controlled data attributed to a shop the attacker does not control — a cross-tenant confusion/access issue.

### Likelihood Explanation
The attacker only needs one legitimate webhook signature they can generate themselves (from a shop they own) and network access to the app's public webhook endpoint — no access token, `api_secret_key`, or privileged account is required. This is directly reachable through the gem's documented API (`Registry.process` / `Request.new`) exactly as instructed in `docs/usage/webhooks.md`.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the bytes that are HMAC-verified (or otherwise cryptographically bind them, e.g., re-derive `shop` only from a value that Shopify signs), and/or have `Registry.process` treat header-derived `shop`/`topic` as untrusted metadata that the host app must additionally validate against its own installed-shop records before acting on it. At minimum, update `docs/usage/webhooks.md` to stop stating that `process` "verifies the request did indeed come from Shopify" for header-derived fields, since only the body is currently verified.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers a real webhook (e.g., `orders/create`) for a body `B`; Shopify sends `X-Shopify-Hmac-Sha256: H(B)` computed with the app's real `client_secret`. Attacker records `(B, H)`.
2. Attacker POSTs `B` with header `X-Shopify-Hmac-Sha256: H` unchanged, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` to the app's webhook endpoint.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds a `Request` whose `hmac` returns the (still valid) signature and whose `shop` returns `"victim.myshopify.com"`.
4. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only hashes `B`.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, exactly as shown in `docs/usage/webhooks.md`'s example handler, causing the host app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
