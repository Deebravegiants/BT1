### Title
Webhook `shop` (and `topic`/`webhook_id`) fields are trusted without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw HTTP body against the HMAC, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from unauthenticated HTTP headers and passed straight through to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — the JSON payload bytes: [3](#0-2) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are pulled from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are never included in the signable string and thus never covered by the HMAC: [4](#0-3) 

These unauthenticated header values are then forwarded verbatim into `WebhookMetadata` and delivered to the host application's handler: [5](#0-4) 

The identity binding that should hold is: `hmac == HMAC(secret, body ‖ shop ‖ topic ‖ webhook_id)`. In this implementation the equality actually enforced is only `hmac == HMAC(secret, body)`, i.e. `shop` (the field the handler acts on to determine tenant) is disjoint from the field set covered by the signature. This matches the report's bug class: "a field acted on but not covered by the HMAC."

### Impact Explanation
Any party who can obtain one legitimately-signed `(body, hmac)` pair for the app's `api_secret_key` — trivially, a merchant/developer who installs the app on their own store and receives real webhooks — can replay that exact body and HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header (and/or `shopify-topic`/`webhook-id`) with an arbitrary victim shop's domain. `HmacValidator.validate` will still return `true` because only the body bytes are checked, and `Registry.process` will hand the forged `shop` value to the handler as `WebhookMetadata#shop`. Any host app that uses `data.shop` to select which tenant's database record to look up/update/create (a documented and expected usage pattern per `docs/usage/webhooks.md`, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) will process the payload under the wrong shop, resulting in cross-tenant data confusion/corruption — the gem's own recommended usage directly propagates the unauthenticated header value as the tenant identifier.

### Likelihood Explanation
Exploitation only requires the ability to send an arbitrary HTTP request to the app's public webhook endpoint plus one previously-observed legitimate webhook for the same app (obtainable simply by installing the app on one's own free/dev store). No access to `api_secret_key`, tokens, or the merchant's credentials is required — this is a pure unprivileged-internet-user replay/header-forgery attack against the identity-binding gap in the gem's own validation logic.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string computed for HMAC verification (or otherwise cryptographically bind them, e.g. verify them against a registered webhook_id/shop pair looked up server-side) rather than trusting header values that fall outside the signed byte range. At minimum, document loudly that `data.shop` must never be trusted for tenant selection without independent server-side verification (e.g. cross-checking against the session/shop that originally registered the given `webhook_id`).

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; trigger a real webhook (e.g. `orders/create`) and capture the raw request: body `B`, and header `shopify-hmac-sha256: H` (valid because `H = HMAC(secret, B)`), along with `shopify-webhook-id`, `shopify-topic`.
2. Replay the identical body `B` and header `shopify-hmac-sha256: H` to the app's webhook endpoint, but replace `shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `Registry.process` calls `HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and matches `H` — validation passes.
4. `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` is delivered to the app's handler, which (per the gem's documented example) uses `data.shop` to route/store data as if it came from the victim's store. [6](#0-5) [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
