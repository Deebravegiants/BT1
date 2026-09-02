### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as fully authenticated once `Utils::HmacValidator.validate` succeeds, but the HMAC only covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values — which are taken from unauthenticated HTTP headers and handed straight to the app's webhook handler — are never bound to that signature. This breaks the intended identity binding: `hmac == HMAC(secret, signed_content)` should equal `HMAC(secret, signed_content) == HMAC(secret, raw_body + shop + topic + ...)`, but in this gem `signed_content` is only `raw_body`.

### Finding Description
`ShopifyAPI::Auth::Oauth::AuthQuery` and `ShopifyAPI::Webhooks::Request` both include `Utils::VerifiableQuery` and are validated the same way via `Utils::HmacValidator.validate`, which recomputes an HMAC over `to_signable_string` and compares it to the supplied `hmac`.

For OAuth, `to_signable_string` binds `code`, `host`, `shop`, `state`, and `timestamp` together, so every field consumed later is covered by the signature. [1](#0-0) 

For webhooks, however, `to_signable_string` returns only the raw body: [2](#0-1) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from HTTP headers with no cryptographic link to the body or the HMAC: [3](#0-2) 

`Registry.process` gates dispatch solely on the body's HMAC, then forwards the header-derived `shop` (and `topic`, `webhook_id`, `api_version`) straight into `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The gem's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole payload (including `shop`) is authenticated — but that's not what the code does; only the body bytes are verified. [5](#0-4) 

Because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across all shops that install the app, any request with a body whose HMAC matches that shared secret is accepted regardless of which shop's headers are attached — i.e., the equality the code actually enforces is `hmac == HMAC(secret, raw_body)`, not `hmac == HMAC(secret, raw_body, shop)`.

### Impact Explanation
This breaks the shop-authentication boundary that the webhook handler relies on for multi-tenant isolation: `data.shop` (used by apps to decide which tenant's records to update, per the documented handler contract) can be forged to any value while still passing HMAC verification, as long as the attacker can produce (or replay) any one raw body whose HMAC validates against the shared secret. This constitutes cross-tenant access/spoofing — an app that trusts `data.shop` (as its own documentation instructs it to) can be made to write, queue, or act on data under an arbitrary victim shop's identity.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one genuine `(raw_body, hmac)` pair valid under the app's shared secret — achievable by installing the app on their own shop (a normal unprivileged action for any merchant) and triggering a subscribed webhook topic, then replaying that exact body with a forged `shop-domain` header (and optionally `topic`/`webhook-id`) to the app's public webhook endpoint. No access token, `client_secret`, or privileged access is needed. Likelihood is moderate: it depends on the host app actually trusting `data.shop` for tenant-scoped actions, which is exactly the documented usage pattern shown in the gem's own README example (`perform_later(topic: data.topic, shop_domain: data.shop, ...)`).

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed content, or require `Registry.process` to cross-check the header-derived `shop` against a shop that is independently known to have a webhook registered for the given `webhook_id`/topic before invoking the handler. At minimum, document prominently that `shop` is not covered by the HMAC and must be independently verified by the app (e.g., against its own session/shop store) before being trusted for tenant-scoped operations.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com` and subscribe to a topic (e.g. `orders/create`).
2. Trigger the topic so Shopify sends a legitimately-signed webhook: raw body `B`, header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(client_secret, B)`, and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Replay the exact same body `B` and `H` to the app's webhook endpoint, but replace the `X-Shopify-Shop-Domain` header with `victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(client_secret, B)`, which still equals `H`, so validation passes.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

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
