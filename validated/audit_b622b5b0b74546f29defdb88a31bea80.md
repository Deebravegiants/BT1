Confirmed: `WebhookMetadata.shop` is populated directly from `Request#shop` (the `shopify-shop-domain` header) at [1](#0-0) , while the HMAC validated in `Registry.process` covers only the raw body via `to_signable_string` at [2](#0-1) . This gives a concrete, in-scope analog to the Palmera bug class (a value trusted for identity purposes that is not actually covered by the cryptographic check).

### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, allowing cross-tenant webhook data injection - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value that is later used as the tenant identifier for dispatching webhook data purely from the unauthenticated `shopify-shop-domain` (or `x-shopify-shop-domain`) HTTP header, while the HMAC signature that `Utils::HmacValidator.validate` checks is computed only over the raw request body. The `shop` field is never included in the signed bytes.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are the two methods used by `HmacValidator.validate` (via the `VerifiableQuery` interface) to authenticate a webhook: [3](#0-2) . `to_signable_string` returns only `@raw_body`, so the computed signature only certifies the integrity of the payload bytes, not of any header.

`Request#shop`, however, is read straight from the `shopify-shop-domain` header, with no relationship to the HMAC at all [4](#0-3) .

`Registry.process` validates the HMAC over the body, then immediately trusts `request.shop` (the header) as the tenant identity when constructing `WebhookMetadata` and invoking the host application's handler: [5](#0-4) . `WebhookMetadata.shop` is a plain `String` field with no further validation [6](#0-5) .

The binding that should hold is:
`shop` bound inside the HMAC-signed bytes == `shop` used to select/attribute tenant data downstream.

What the gem actually implements is:
`shop` (unsigned header) == `shop` used to select/attribute tenant data downstream,

with the HMAC only certifying `raw_body` was unmodified. Because the header is outside the signed material, `HmacValidator.validate(request)` returns `true` for any `(body, hmac)` pair that is valid for *some* shop, regardless of what value is placed in the `shop-domain` header.

### Impact Explanation
An attacker who controls a Shopify development store (or otherwise obtains one legitimate `(raw_body, hmac)` pair — this is routine, since any developer can install their own app and have Shopify send them a real signed webhook) can capture that valid body+HMAC and resend it to the same webhook endpoint with the `shopify-shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` will still succeed because it only checks the body against the HMAC using the app's own `client_secret`/`api_secret_key` (the check never depends on the header). The host application's `WebhookHandler#handle` will then receive `WebhookMetadata` claiming the payload belongs to the victim shop, causing cross-tenant data confusion inside the host app (e.g., writing/attributing the attacker's own store data — orders, customer records, GDPR/redact events — as belonging to another merchant). This crosses the tenant boundary this gem is responsible for enforcing via `Utils::HmacValidator`.

### Likelihood Explanation
Likelihood is realistic: obtaining one valid signed webhook requires no privileged credential — any developer/attacker can create their own free development store, install their own app, and Shopify will deliver real signed webhooks to it. Replaying that captured request with a substituted `shop-domain` header against the app's public webhook endpoint requires no knowledge of `api_secret_key`.

### Recommendation
Bind the shop identity into the signed material used for verification, e.g., include the `shopify-shop-domain` header (and ideally `topic`, `webhook-id`) in `to_signable_string` (mirroring how Shopify signs the full canonical request for other integrity checks), or independently verify that `request.shop` matches an expected/allow-listed shop for the given `topic`/subscription before dispatching to the handler, rather than trusting the header value.

### Proof of Concept
1. Attacker installs their own app instance on `attacker-shop.myshopify.com` (a shop they control) and lets Shopify deliver a normal webhook (e.g. `orders/create`) to the app's webhook endpoint, capturing the raw request: headers + body + valid `X-Shopify-Hmac-Sha256`.
2. Attacker resends this exact `raw_body` with the exact same `X-Shopify-Hmac-Sha256` value, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. In the app, `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)` [7](#0-6) ; since `to_signable_string` only returns `@raw_body`, which is unmodified, validation succeeds.
4. `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` [1](#0-0) , and the host app's handler processes the attacker's payload as if it originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
