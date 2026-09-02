The gem's own documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" based solely on the `Utils::HmacValidator.validate(request)` check, and instructs host apps to use `data.shop` from `WebhookMetadata` as the trusted shop identity. This confirms the vulnerability is reachable through the gem's documented API, not something that depends on the host app misusing it.

### Title
Webhook shop/topic identity spoofing via HMAC coverage gap in `ShopifyAPI::Webhooks::Request` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity solely via `Utils::HmacValidator.validate(request)`, which HMACs only the raw request body [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers [2](#0-1)  and are never included in the signed content. `Registry.process` then forwards `request.shop` as the trusted tenant identifier straight into `WebhookMetadata`, which the host app uses to attribute the webhook body to a shop [3](#0-2) .

### Finding Description
The identity binding that should hold is: `HMAC-authenticated bytes == bytes that determine tenant attribution`. Here it does not — `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from headers that sit entirely outside the signed content [4](#0-3) .

Because the app's `client_secret` (`Context.api_secret_key`) is shared across every shop that installs the app, an unprivileged user who installs the public app on their own store legitimately receives valid, HMAC-signed webhook deliveries for their own shop. That attacker can capture one such genuine `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`) header with a victim shop's domain. `Utils::HmacValidator.validate` will still pass, because it only recomputes the HMAC over `raw_body` [5](#0-4) . `Registry.process` will accept the forged request and hand the attacker-chosen `shop` value to the handler as if it came from Shopify [3](#0-2) .

The gem's own documentation tells implementers that `Registry.process` "will verify the request did indeed come from Shopify" and that `data.shop` is "The shop domain of the webhook" to be trusted for dispatch/attribution (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), reinforcing that this is the gem's intended, documented contract rather than a host-app misuse [6](#0-5) [7](#0-6) .

### Impact Explanation
This is a cross-tenant data-attribution vulnerability: an attacker who is merely an installer of the app on their own shop can cause the app to process webhook payloads under a victim shop's identity, e.g. triggering `orders/create`/`customers/update` style processing that writes attacker-supplied data into the victim's tenant scope, or causes the app to perform tenant-scoped side effects (job enqueue, DB writes, notifications) keyed to a shop the attacker does not own. This matches the "cross-tenant access" Critical impact category since the trust boundary between shops is broken using only a legitimately-obtained webhook from the attacker's own store.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple untrusted merchants (the standard SaaS/public-app model): any merchant can install the app, capture one genuine webhook body+HMAC pair from their own shop, and replay it with a forged `shop-domain` header — no access to `client_secret`, access tokens, or victim credentials is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (or otherwise cryptographically bind them), or require the host application to independently verify that `shop` in `WebhookMetadata` corresponds to a shop that legitimately has this webhook `topic` registered for the `webhook_id`, rather than trusting the raw header value. At minimum, document that `request.shop`/`request.topic` are unauthenticated headers and must not be relied upon for tenant attribution without an independent registration/idempotency check keyed by `webhook_id` against Shopify's API.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker.myshopify.com`, receiving genuine webhook deliveries (e.g. `orders/create`) signed with the app's shared `client_secret`.
2. Attacker captures the raw POST body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` from one such delivery.
3. Attacker sends a new POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`), but sets `X-Shopify-Shop-Domain: victim.myshopify.com` and `X-Shopify-Topic: orders/create`.
4. `ShopifyAPI::Utils::HmacValidator.validate` computes `HMAC(client_secret, B)`, matches `H`, and returns `true` [8](#0-7) .
5. `Registry.process` dispatches to the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, and the host app processes/persists the attacker's payload under the victim shop's identity [3](#0-2) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-21)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
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
