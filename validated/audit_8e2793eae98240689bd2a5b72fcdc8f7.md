Confirmed: `Registry.process` validates the HMAC over `request.to_signable_string`, which is defined as `@raw_body` only.### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw request body, then hands the caller-supplied `shop-domain`, `topic`, and `webhook-id` HTTP headers straight into the `WebhookMetadata` passed to the app's handler — even though none of those headers are part of the signed payload. This breaks the equality binding: `bytes verified by HMAC == identity fields the handler acts on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers, independent of the body: [2](#0-1) 

`Registry.process` validates only that `HmacValidator.validate(request)` succeeds — i.e., that the *body* bytes match the HMAC computed with `Context.api_secret_key` — and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` delivered to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` computes the HMAC purely over `verifiable_query.to_signable_string` (the body): [4](#0-3) 

Documentation for `WebhookHandler` explicitly tells app authors to trust `data.shop` as the tenant identifier for routing/persisting webhook data (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), reinforcing that this field is meant to be an authenticated tenant key: [5](#0-4) 

Because the same HMAC (computed for a given JSON body, e.g. `"{}"` or any other resource payload) is valid regardless of what `shop-domain` header accompanies it, any entity capable of obtaining a single legitimately-signed `(body, hmac)` pair for the app (for example a merchant who has installed the app and can trigger real webhooks for their own store, since `orders/create`, `products/update`, etc. bodies are frequently generic/predictable JSON shapes) can replay that exact body+HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value naming a different merchant/tenant. `Registry.process` will accept it (the body HMAC still checks out) and hand the handler `WebhookMetadata` claiming the victim shop, `topic`, and `webhook_id` of the attacker's choosing.

### Impact Explanation
This is a cross-tenant identity-binding failure: the value the HMAC verifies (body bytes) is disjoint from the value the application uses to determine *which tenant* the payload belongs to (`shop` header) and *which resource type* it represents (`topic` header, which also determines webhook-id/dedup handling). An attacker who can only legitimately trigger webhooks for their own tenant can make the host application process/persist/act on webhook data under another merchant's `shop` identity — i.e., cross-tenant data injection/confusion, which the rules classify as Critical impact.

### Likelihood Explanation
Likelihood is High for a multi-tenant app: any user who installs the app (an "unprivileged internet user" relative to other merchants on the same app) already possesses valid `(body, hmac)` pairs for topics they can trigger themselves (e.g., updating their own product/order). No possession of `api_secret_key` is required — only a legitimate, arbitrary webhook delivery for the attacker's own store, which any merchant can generate at will. The only work required is resending that captured POST with a modified `shop-domain` (and optionally `topic`/`webhook-id`) header, since the header is never covered by the signature.

### Recommendation
Bind the tenant/topic identity into the HMAC-verified data instead of trusting unauthenticated headers:
- Include `shop-domain`, `topic`, and `webhook-id` in the signable string used by `HmacValidator`, matching Shopify's actual webhook delivery guarantees only when combined with additional server-side controls (e.g., verifying the `shop` header value against a shop known to have an active session/registration for that specific webhook topic before dispatching to the handler).
- At minimum, cross-check that the `shop` header corresponds to a shop for which this exact webhook `topic`/`webhook_id` was registered (e.g., look up an expected shop via a webhook-id-to-shop mapping maintained at registration time) rather than trusting the header verbatim in `Registry.process`.
- Document clearly that `WebhookMetadata#shop` is not covered by the HMAC and require app developers to independently validate it against the shop that legitimately registered that topic/subscription before using it for tenant-keyed persistence.

### Proof of Concept
1. App registers webhook handler for topic `products/update` and shop-agnostic HTTP endpoint via `ShopifyAPI::Webhooks::Registry.process`.
2. Attacker (a merchant who has legitimately installed the app on `attacker-shop.myshopify.com`) triggers a `products/update` webhook for their own store and captures the raw POST, including body and the `x-shopify-hmac-sha256` header Shopify computed over that body with the shared `api_secret_key`.
3. Attacker resends the identical HTTP POST (same body, same `x-shopify-hmac-sha256`) to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (unmodified) body against the (unmodified) HMAC: [6](#0-5) 
5. The handler receives `WebhookMetadata.shop == "victim-shop.myshopify.com"` and processes/persists the attacker's payload under the victim's tenant identity, per the documented handler contract: [7](#0-6)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L19-30)
```markdown
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
