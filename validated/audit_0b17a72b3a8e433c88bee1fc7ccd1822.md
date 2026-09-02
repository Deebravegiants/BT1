Confirmed. This is a real, reachable vulnerability within the gem's own webhook processing code.

### Title
Webhook `shop-domain` field is trusted and handed to app handlers without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed by `Utils::HmacValidator.validate` in `Registry.process` authenticates *only the body bytes*, never the `X-Shopify-Shop-Domain` header. `Registry.process` nonetheless reads `request.shop` straight from that unauthenticated header and forwards it, as an implicitly trusted, first-class field, into every app's `WebhookHandler#handle` via `WebhookMetadata#shop`. Any caller who can produce one genuine `(body, hmac)` pair signed with the app's shared `api_secret_key` — which every shop that installs a multi-tenant app receives via real Shopify-delivered webhooks — can attach an arbitrary `shop-domain` header value and have the library report it as authenticated, breaking the binding `hmac-covered bytes == shop identity acted upon`.

### Finding Description
`Registry.process` performs exactly one authentication check before dispatching to app code: [1](#0-0) 

That check is `Utils::HmacValidator.validate(request)`, which HMACs `request.to_signable_string`: [2](#0-1) 

But `Request#to_signable_string` is defined to be just the raw body, entirely excluding any header: [3](#0-2) 

Meanwhile `Request#shop` is read straight from the `shop-domain`/`x-shopify-shop-domain` header with no cross-check against the signed body or against any other authenticated value: [4](#0-3) 

This unauthenticated value is what `Registry.process` promotes to `WebhookMetadata#shop` and hands to the app's `WebhookHandler`: [5](#0-4) [6](#0-5) 

The gem's own documentation instructs developers to treat this field as the authoritative shop identity for downstream, per-tenant actions (e.g., enqueuing per-shop jobs): [7](#0-6) 

The identity binding that should hold is: *bytes verified by HMAC == bytes the handler acts on as the tenant identity*. Here that equality fails — the HMAC covers `body` only, while the handler acts on `shop` from a sibling header that is never mixed into the signable string.

### Impact Explanation
Because `api_secret_key` is the app's single client secret shared across *all* installing shops (not a per-shop secret), any shop that has legitimately installed the app receives real, validly-HMAC-signed webhook deliveries for its own shop. An attacker who operates such a shop (trivial to obtain via a free development store) can capture one genuine `(raw_body, hmac)` pair and resend it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. `Registry.process` will accept the HMAC (it never depended on the header) and call the handler with `data.shop == "victim-shop.myshopify.com"`. Any app that uses `data.shop` to key per-tenant state (billing, entitlement changes, `app/uninstalled` cleanup, order/fulfillment records, GDPR data-erasure triggers, etc.) will apply the attacker's payload to the wrong tenant — a cross-tenant data integrity/confusion vulnerability reachable by an unprivileged, self-service app installer, without needing to know or leak `api_secret_key`, an access token, or any victim credential.

### Likelihood Explanation
High feasibility: no secrets need to be stolen — an attacker only needs to install the target app on a shop they control (self-service, free) to obtain one legitimately signed webhook body/HMAC pair for any topic they choose, then replay it with a forged shop header directly against the app's public webhook URL. The construction requires no cryptographic breaking, only reuse of an authentic signature the attacker was rightfully given.

### Recommendation
Bind the shop identity into the authenticated signable string, or otherwise independently verify it, before exposing `WebhookMetadata#shop` to handlers — e.g., include the `shop-domain` (and ideally `webhook-id`/`api-version`) header bytes in `to_signable_string` so the HMAC covers them, or require callers to resolve/confirm the shop via a previously stored, session-bound record rather than trusting the header verbatim.

### Proof of Concept
1. App "Foo" is installed on attacker-controlled shop `attacker.myshopify.com`; Shopify delivers a genuine webhook, e.g. `app/uninstalled`, to `POST /webhooks` with body `body_A` and header `X-Shopify-Hmac-Sha256: hmac_A` (valid for `body_A` under the app's `api_secret_key`), `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures `body_A` and `hmac_A` (trivially, since it's their own shop and traffic).
3. Attacker sends `POST /webhooks` directly to the app's public endpoint with the same `body_A` and `X-Shopify-Hmac-Sha256: hmac_A`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: body_A, headers: {...})` is built; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which hashes only `body_A` — passes.
5. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "app/uninstalled", body: parsed_body_A, ...))`, causing the app to run its uninstall/cleanup logic against the victim shop's tenant record, even though nothing about `victim-shop.myshopify.com` was ever cryptographically verified.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
