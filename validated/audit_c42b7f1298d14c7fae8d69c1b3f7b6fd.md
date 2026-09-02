### Title
Webhook Tenant Identity (`shop`) Header Not Covered by HMAC, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify," but the actual HMAC check only binds the raw request body to the signature — it never binds the `shop`, `topic`, `webhook-id`, or `api-version` headers. Because those headers (especially `shop`) are handed to the app's handler as trusted tenant-identifying metadata, an unprivileged attacker who legitimately installs the app on their own shop can capture one of their own genuinely-signed webhook deliveries and replay it to the same endpoint with the `x-shopify-shop-domain` header swapped for a victim shop, producing a request that passes signature verification while claiming to originate from a different tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which participate in the signable string: [2](#0-1) 

`Registry.process` performs exactly one check — `Utils::HmacValidator.validate(request)` — and then dispatches directly to the handler using `request.shop` and the other unauthenticated headers: [3](#0-2) 

`HmacValidator.validate` computes `HMAC-SHA256(api_secret_key, verifiable_query.to_signable_string)` (i.e., over the body only) and `secure_compare`s it to the `hmac` header: [4](#0-3) 

The `api_secret_key` is the app's single `client_secret`, shared across every shop that installs the app — it is not shop-specific. So a signature that is valid for one shop's webhook body is equally valid for a replayed request claiming to be from a different shop, as long as the body bytes are unchanged. The identity binding broken is:
`shop header used by the handler (tenant selector)` ≠ `bytes actually covered by the HMAC (body only)`.

The gem's own documentation instructs developers to trust `data.shop` as the tenant identifier coming out of a "verified" webhook request, reinforcing that this is the intended, documented use of the API rather than host-application misuse: [5](#0-4) [6](#0-5) 

`WebhookMetadata.shop` is populated straight from the unauthenticated header and passed to the handler as trustworthy data: [7](#0-6) 

### Impact Explanation
An attacker who installs the app on their own shop (an ordinary, unprivileged action requiring no stolen credentials) will legitimately receive real webhook deliveries — bodies with a matching, correctly-computed HMAC over the app's shared secret. By replaying that exact body/HMAC pair to the app's public webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`) header changed to a victim shop's domain, the attacker produces a request that passes `Registry.process`'s HMAC check yet is dispatched to the host application's handler as authentic data for the victim shop. Any host app following the gem's documented pattern (using `data.shop` to select which tenant's record to update, as shown verbatim in the gem's own webhooks doc) will apply the attacker-controlled webhook body to the wrong shop's record — a cross-tenant write/confusion.

### Likelihood Explanation
Requires only that the attacker be able to install the app on a shop they control (a normal, unprivileged flow for any public or freemium app) and be able to intercept/observe one webhook delivery to their own configured endpoint — no credential theft, TLS interception, or privileged access is required. The replay itself is a trivial HTTP POST with a modified header.

### Recommendation
Bind the tenant-identifying and dispatch-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) into the HMAC-covered signable content, or otherwise independently authenticate the `shop` header (e.g., cross-check it against a shop value embedded in the signed body, or require callers to additionally verify shop ownership before trusting `data.shop`) before it is handed to `WebhookHandler#handle`.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; the app registers a webhook, e.g. `orders/create`, to `POST /callback/orders/create`.
2. Shopify sends a legitimate webhook to the attacker's endpoint:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of body>`
   - Body: `{"id": 1, ...}`
3. Attacker captures the raw body and the `x-shopify-hmac-sha256` value.
4. Attacker sends their own POST to the same public endpoint URL, keeping body and `x-shopify-hmac-sha256` identical, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` (lines 26-31) succeeds because it only checks the body bytes against the app's shared secret.
6. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb` lines 188-199) dispatches to the handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's order data>, ...)`.
7. If the host app follows the gem's documented handler pattern (`docs/usage/webhooks.md` lines 20-29), it processes/stores the attacker's data under the victim's tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
