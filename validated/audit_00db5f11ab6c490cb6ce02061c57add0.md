This confirms the finding: `Registry.process` is the gem's own documented API, and it hands `data.shop` (derived solely from the unauthenticated `x-shopify-shop-domain` header) directly to the handler, with the gem's own docs explicitly telling developers to trust `data.shop` as "The shop domain of the webhook" — the gem never covers the `shop`, `topic`, `webhook_id`, or `api_version` headers with the HMAC.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header is trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` but its `to_signable_string` only returns the raw request body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only that HMAC against the body, then forwards `request.shop` (and the other header-derived fields) verbatim to the app's handler as trusted tenant identity [3](#0-2) .

### Finding Description
The identity binding the gem is supposed to enforce is: `shop attributed to the webhook == shop the HMAC actually authenticates`. In reality the HMAC only authenticates the raw body bytes; it never binds the `x-shopify-shop-domain` (or topic/webhook-id/api-version) header to that signature. `HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for `Webhooks::Request` is defined as just `@raw_body` [1](#0-0)  and `lib/shopify_api/utils/hmac_validator.rb" start="26" end="31" />. Any request whose body produces a matching HMAC (i.e., any genuine webhook body the app's own `client_secret` previously signed, replayed with a different `shopify-shop-domain` header) passes `Errors::InvalidWebhookError` validation in `Registry.process` [4](#0-3)  and is delivered to the handler tagged with the attacker-chosen shop, exactly analogous to the reported class: a value acted upon (the shop attribution) is not covered by the cryptographic check (the HMAC), just as Chainlink's `roundId`/staleness data isn't checked before being trusted downstream.

Concretely, an attacker who legitimately installs the app on their own store (shop A) receives genuine, correctly-HMAC-signed webhooks for shop A's own events. Because the HMAC signs only the JSON body — which frequently contains no shop-identifying field, or one the attacker can craft themselves for their own resources — the attacker can capture their own valid `(body, hmac)` pair and resend it to the app's webhook endpoint with `x-shopify-shop-domain: victim-shop.myshopify.com`. `HmacValidator.validate` still succeeds (same body, same secret, same signature) [5](#0-4) , and `Registry.process` hands `WebhookMetadata.new(... shop: request.shop ...)` to the handler as if it were an authentic event for the victim shop [6](#0-5) .

### Impact Explanation
This is a cross-tenant identity/data-integrity break: the gem's own documented flow (`Registry.process` → handler) delivers webhook data falsely attributed to a victim merchant's shop domain, without the merchant's involvement [7](#0-6) . Downstream host applications are explicitly told by the gem's docs that `data.shop` is "the shop domain of the webhook" and can be used directly (e.g., to enqueue per-shop jobs) [8](#0-7) , so this is not "host app ignoring documented API" — it's the gem's own documented contract being unsound. This can lead to cross-tenant data confusion/injection in any app that keys business logic off `data.shop` without additional verification.

### Likelihood Explanation
Likelihood is bounded by the attacker needing a legitimately-signed `(body, hmac)` pair, which they can always obtain by installing the app on their own store (any unprivileged internet user can do this) and capturing Shopify's genuine webhook delivery to themselves; they then only need to change one HTTP header when replaying it to the same endpoint.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed material `to_signable_string` returns (or otherwise cryptographically bind them to the request, e.g. by deriving/verifying the shop from a server-side registration lookup rather than trusting the header), so the HMAC actually authenticates every field the handler is told to trust, not just the raw body.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) so Shopify sends a genuinely HMAC-signed request to the app's webhook endpoint.
2. Capture the raw body and the `x-shopify-hmac-sha256` value from that request.
3. Resend the same body and HMAC header to the identical endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (`@raw_body` only) and finds it matches, so validation passes [1](#0-0) .
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the request never touched the victim's store [6](#0-5) .

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** docs/usage/webhooks.md (L12-27)
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
