### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` never covers the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` headers. The library treats a request as "verified" and hands `request.shop` straight to the app's handler as an authenticated tenant identifier, even though that field was never bound to the signature.

### Finding Description
`Registry.process` gates all webhook handling on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

The HMAC check itself computes the signature only from `to_signable_string`, which for `Webhooks::Request` returns `@raw_body` alone: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from unauthenticated headers: [3](#0-2) 

and are passed unchecked into `WebhookMetadata`, which the host app's handler treats as the identity of the shop that triggered the event: [1](#0-0) [4](#0-3) 

This is the same bug class as the external report: a field that is *acted upon* (here, the `shop` used to attribute/authorize the webhook payload to a tenant) is not covered by the identity-binding mechanism (the HMAC), so `verified(bytes)` ≠ `bound(shop)`. The equality that should hold — "the shop that the HMAC secret proves the request came from" == "the shop the handler is told the data belongs to" — is broken because the secret only proves the *body* was signed, not who the sender claims to be.

The docs explicitly instruct developers to construct the `Request` directly from raw headers/body and rely on `Registry.process` to "verify the request did indeed come from Shopify": [5](#0-4) 
which reinforces that host apps are expected to trust `data.shop` as authenticated once `process` succeeds.

### Impact Explanation
Any actor who can install the app on their own shop (an unprivileged, self-service action for public/embedded apps) receives a genuinely-signed webhook for their own store. Because the HMAC only covers the JSON body — never the `shop-domain` header — that same attacker can capture their own valid `(body, hmac)` pair and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim merchant's domain. `Utils::HmacValidator.validate` still succeeds (it only re-hashes the body with the app's shared `api_secret_key`), and `Registry.process` invokes the app's handler with `WebhookMetadata#shop` set to the victim's domain. Any downstream logic that uses `data.shop` to look up records, apply per-tenant business logic, or write to a merchant's data store can be tricked into acting on/for a shop the attacker doesn't own — a cross-tenant data-integrity/confidentiality issue rooted entirely in this gem's incomplete signable-string coverage, not in any assumption the host app must additionally verify.

### Likelihood Explanation
High for any app that follows the documented, default usage in `docs/usage/webhooks.md` (constructing `Webhooks::Request` from `raw_body` + headers and dispatching via `Registry.process`) without independently re-validating the shop against a known/allow-listed session — which nothing in the public API surfaces as a requirement, since `process` is advertised as verifying "the request did indeed come from Shopify." The only prerequisite is that the attacker be an installed merchant of the app, which is a normal, unprivileged use case for any public Shopify app.

### Recommendation
Include the trusted headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signable content the same way `Oauth::AuthQuery#to_signable_string` binds `shop`/`host`/`state` into its signature, or otherwise cryptographically bind the shop identity to the payload before exposing it to `WebhookHandler#handle`. At minimum, document prominently that `Registry.process`'s HMAC check does not authenticate the `shop`/`topic`/`webhook_id` headers, and require callers to cross-check `data.shop` against a known, previously-authorized shop/session before trusting it.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`). Shopify sends a request signed with the app's shared `api_secret_key`:
   - `X-Shopify-Hmac-Sha256: <valid hmac of raw_body>`
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - body: `{"id": 123, ...}`
2. Attacker captures `raw_body` and the `X-Shopify-Hmac-Sha256` value.
3. Attacker POSTs the identical `raw_body`/`hmac` to the app's webhook endpoint again, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` — [6](#0-5)  — which passes because `to_signable_string` never included the `shop-domain` header, so the same body+hmac pair validates for any spoofed shop value.
5. The handler receives `WebhookMetadata.shop == "victim.myshopify.com"` and processes attacker-controlled order data as if it came from the victim's store.

### Citations

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
