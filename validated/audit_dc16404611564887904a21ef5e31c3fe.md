### Title
Webhook shop identity is trusted from an unauthenticated header while HMAC only covers the body, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, but the `shop` (and `topic`, `webhook_id`, `api_version`) values used to identify the tenant are read straight from HTTP headers that are never included in that signature. `Webhooks::Registry.process` then hands `request.shop` to the app's handler as the trusted merchant identity. Any party who can obtain one genuine `(body, hmac)` pair — trivially, the operator of their own installed shop, who can trigger a real webhook delivery to themselves — can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header. The HMAC check still passes, and the handler is invoked believing the event legitimately originated from the victim shop.

### Finding Description
The binding that should hold is:
`hmac == HMAC(secret, body ‖ shop ‖ topic ‖ webhook_id)`, i.e. the field acted upon (`shop`) should be cryptographically bound to the same proof that authenticates the request.

What actually holds is:
`hmac == HMAC(secret, body)` only [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are parsed from headers that are never fed into `to_signable_string` [2](#0-1) .

`HmacValidator.validate` verifies exactly this narrower binding — it calls `verifiable_query.to_signable_string`, which for `Webhooks::Request` is `@raw_body` alone [3](#0-2) .

`Webhooks::Registry.process` then trusts `request.shop` as the tenant identity passed to the app's handler, with no secondary check that this header is consistent with anything cryptographically verified: [4](#0-3) .

Because the equality that's actually enforced (`hmac == HMAC(secret, body)`) is weaker than the equality the app relies on (`hmac` authenticates that this body came from `shop`), an attacker who owns/controls their own legitimately-installed shop can:
1. Trigger a real webhook from their own shop, capturing a valid `(raw_body, hmac)` pair signed by Shopify with the app's real secret.
2. Replay that exact body and HMAC to the app's webhook endpoint, but with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header changed to the victim shop's domain.
3. `HmacValidator.validate` still succeeds (only the body is checked), and `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's own data>, ...)` [5](#0-4) .

Any host application that keys tenant-scoped state (session/token lookups, order/customer records, app-uninstall cleanup, GDPR/compliance actions, billing state, etc.) off `WebhookMetadata#shop` — which is the documented and only way to identify the originating shop for a webhook in this gem — will process the attacker's payload as though it belongs to the victim tenant.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to establish for webhook delivery: the `shop` field is the sole tenant identifier exposed by `WebhookMetadata`, and it is not authenticated. This enables cross-tenant confusion/injection of webhook events between shops that are both installed on the same app, which maps to the "cross-tenant access" Critical-impact category (an attacker forces the app to associate their controlled webhook content with a different merchant's identity).

### Likelihood Explanation
Requires only that the attacker be a legitimate installer of the app on their own shop (an ordinary unprivileged, unauthenticated-to-other-tenants position) and be able to send arbitrary HTTP headers to the app's public webhook endpoint — no possession of `api_secret_key`, access tokens, or any victim credentials is needed. The only "difficulty" is capturing one genuine `(body, hmac)` pair from their own shop, which is under the attacker's control and easy to obtain (they can trigger `orders/create`, `app/uninstalled`, etc. on their own store at will).

### Recommendation
Bind the tenant identity into the signature verification, not just the body. Either:
- Extend `VerifiableQuery`/`Webhooks::Request#to_signable_string` (or a dedicated check in `Registry.process`) so that verification is scoped per-`(shop)` context, e.g., require the caller to additionally confirm the `shop` header matches a shop-specific secret, expected tenant list, or previously-issued webhook registration for that shop; or
- At minimum, document/enforce that `WebhookMetadata#shop` must never be trusted as an authenticated tenant identifier by itself, and that host applications must cross-check it against session state established through an authenticated channel before acting on it.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# triggers a real webhook (e.g. orders/create) which Shopify signs and delivers:
#
#   headers:
#     x-shopify-topic: "orders/create"
#     x-shopify-hmac-sha256: "<valid_hmac_for_body>"
#     x-shopify-shop-domain: "attacker.myshopify.com"
#   body: '{"id": 1, "note": "malicious payload"}'
#
# Attacker replays the exact same body + hmac to the victim app's webhook
# endpoint, only changing the shop-domain header:

headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => "<valid_hmac_for_body>",   # unchanged, still valid because body is unchanged
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, NOT covered by HMAC
}
body = '{"id": 1, "note": "malicious payload"}'

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) returns true (only `body` is checked)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: ..., ...))
# The app's handler now processes attacker-controlled data as if it came from victim-shop.
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
