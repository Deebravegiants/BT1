Confirmed: the HMAC only signs `@raw_body` via `to_signable_string`, while `topic`, `shop`, `webhook_id`, and `api_version` are all pulled straight from unauthenticated request headers with no cryptographic binding, as seen in `Registry.process`, which passes `request.shop` into `WebhookMetadata` after only verifying the HMAC on the body.

### Title
Webhook `shop` identity is read from an unauthenticated header while the HMAC only signs the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#hmac` is validated only against `@raw_body` (`to_signable_string`), but the `shop`, `topic`, `webhook_id`, and `api_version` fields consumed by the app are taken directly from HTTP headers that are excluded from the HMAC computation.

### Finding Description
`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors instead read directly from the `shopify-*`/`x-shopify-*` headers with no cryptographic binding to the signature [2](#0-1) . `Registry.process` checks the HMAC once, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to construct `WebhookMetadata` passed to the app's handler [3](#0-2) .

This breaks the intended identity binding: `shop-that-authenticated-the-payload == shop-attributed-to-the-payload`. Since the header carrying the shop identity is not part of the signed content, any unprivileged internet user who can obtain one genuine `(raw_body, hmac)` pair — e.g., by installing the app on their own inexpensive/free development store and receiving a real webhook for a topic they control — can replay that exact body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and optionally `shopify-topic`/`shopify-webhook-id`) with a victim shop's domain. `HmacValidator.validate` still returns true because it only checks the body bytes, and `Registry.process` attributes the (attacker-controlled) payload to the victim shop.

### Impact Explanation
This crosses a tenant boundary: an attacker can make a merchant app process attacker-controlled webhook data under a victim shop's identity, corrupting per-shop state, triggering victim-scoped side effects (e.g., data updates, notifications, billing-related webhook processing) keyed off `request.shop`, without ever needing the app's `client_secret` or any victim credential.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate (even free-tier) merchant able to install the app and trigger one webhook of their choosing to harvest a valid `(body, hmac)` pair, then send a forged HTTP request to the app's public webhook endpoint with a modified shop header — no secrets, tokens, or privileged access are required.

### Recommendation
Bind the shop (and topic/webhook id) identity into the HMAC verification itself, e.g., include the relevant headers in the signable string, or have `Registry.process` cross-check `request.shop` against an out-of-band record of which secret/shop the payload was expected from, rather than trusting an unauthenticated header once the body-only HMAC passes.

### Proof of Concept
```ruby
# 1. Attacker installs the app on their own shop "attacker.myshopify.com"
#    and receives a genuine webhook:
raw_body = '{"id": 1}'
real_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret, raw_body)
# headers received: x-shopify-shop-domain: attacker.myshopify.com, x-shopify-hmac-sha256: Base64(real_hmac), ...

# 2. Attacker replays the same body+hmac but swaps the shop header to the victim's shop:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(real_hmac),   # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only raw_body is checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app now processes attacker-controlled data as if it belongs to victim-shop.myshopify.com
```

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
