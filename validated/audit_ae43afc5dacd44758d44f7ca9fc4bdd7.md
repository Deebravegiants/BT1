### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity by checking `Utils::HmacValidator.validate(request)`, but the HMAC is computed and verified only over the raw request body. The `shop` identity that the library exposes to the app's handler (`WebhookMetadata#shop`, used by the app to know *which tenant* the event belongs to) is read from an HTTP header that is never part of the signed data. This breaks the identity binding: `shop authenticated == shop acted on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is parsed straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is not included anywhere in `to_signable_string`: [2](#0-1) [3](#0-2) 

`Registry.process` performs exactly one authenticity check — the HMAC over the body — and then immediately forwards `request.shop` (the unauthenticated header value) into `WebhookMetadata`, which is handed to the app's handler as the trusted tenant identifier: [4](#0-3) 

The library's own documentation instructs integrators to treat `data.shop` as the shop the event belongs to and to use it directly for tenant-scoped work (e.g., enqueuing a job keyed by `shop_domain: data.shop`): [5](#0-4) [6](#0-5) 

**Identity binding broken:** `shop_that_produced_the_valid_HMAC (unknown/any) != shop_header_value_trusted_by_handler (attacker-controlled)`.

Concretely: since only the body bytes are HMAC-verified, the pair (body, HMAC) valid for shop A's real webhook remains a perfectly valid `(body, HMAC)` pair no matter what the accompanying `shop-domain` header says, because that header plays no role in `validate_signature`: [7](#0-6) 

An unprivileged internet user who has *any* store where they can trigger a webhook with an app installed (e.g. their own free Shopify dev store subscribed to the same topic, or simply crafting an equivalent body — many webhook payloads are shop-agnostic JSON, such as the `{}` bodies used throughout this gem's own test suite) can capture a legitimately-signed `(body, hmac)` pair and replay it to the victim app's webhook endpoint with the `shop-domain` header changed to the victim's domain. `Registry.process` will accept it as authentic and hand the app a `WebhookMetadata` claiming to be the victim shop, even though the HMAC never certified that claim.

### Impact Explanation
This is a **cross-tenant** vulnerability: the value applications are told to trust as the tenant/shop identifier for a cryptographically verified webhook is not actually covered by that verification. Any app that follows this gem's documented pattern (using `data.shop` to route/attribute webhook data to a specific merchant, e.g. looking up that shop's session/access token, writing to that shop's records, or triggering shop-scoped side effects) can be made to process attacker-supplied or replayed data under a victim shop's identity, i.e., cross-tenant data confusion/injection driven entirely through this gem's webhook verification API.

### Likelihood Explanation
Moderate-to-high. No credentials, tokens, or privileged access are required — only the ability to reach the app's public webhook endpoint (which by design accepts unauthenticated internet traffic) and knowledge/possession of a validly-signed body/HMAC pair for the given `api_secret_key`, which is straightforward when payloads are static, predictable, or obtainable via the attacker's own store subscribing to the same topic with the same app installed.

### Recommendation
Include the `shop` (and ideally `topic`) values in the signed content, or otherwise cryptographically bind them to the verified body before exposing them via `WebhookMetadata`. If Shopify's inbound HMAC scheme genuinely only signs the body (matching Shopify's own webhook delivery format), the gem should not present `shop` as a trusted, handler-facing field without a documented caveat, and should instead provide/require a secondary binding mechanism (e.g., matching the header shop against the topic/webhook_id pairing verified via a follow-up authenticated Admin API call, or cross-checking against the app's own webhook subscription registry) before `Registry.process` releases `WebhookMetadata` to the handler.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and subscribes to a topic whose payload is shop-agnostic or predictable (e.g. an empty-body event, mirroring the test fixture used in this gem's own suite: raw body `"{}"`).
2. Shopify delivers the real webhook to the attacker with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of "{}">`
3. Attacker captures the `(raw_body, hmac)` pair and re-POSTs it to the victim app's webhook endpoint, but replaces the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header into `shop`, and `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC — the `shop-domain` header is never part of `to_signable_string`. [1](#0-0) 
5. `Registry.process` calls the app's handler with `WebhookMetadata(shop: "victim.myshopify.com", ...)`, and the app (following this gem's documented usage pattern) performs shop-scoped actions attributed to the victim. [4](#0-3)

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

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
