## Title
Webhook `shop` (and `topic`/`webhook_id`) identity is trusted from unsigned headers while only the body is HMAC-verified, enabling cross-tenant webhook misattribution - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signature from the raw request body only, but the `shop`, `topic`, and `webhook_id` fields that the app actually acts on are read from HTTP headers that are never covered by that signature. Any webhook consumer that authenticates a request via `Utils::HmacValidator.validate(request)` and then trusts `request.shop`/`request.topic` for tenant routing is relying on an identity binding that the HMAC does not actually enforce.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, and `webhook_id` are pulled straight from headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry#process` validates only that the body's HMAC is correct, then immediately trusts `request.shop`/`request.topic` (derived from unsigned headers) to route the payload to a handler and construct `WebhookMetadata`: [3](#0-2) 

The identity binding that should hold is:
`shop_that_signed_the_body == shop_the_app_attributes_the_event_to`

But the actual binding enforced by this gem is only:
`hmac(raw_body, api_secret_key) == received_hmac`

The `shop-domain` header (and `topic`/`webhook-id`) are outside that equality. Because a single app-level `client_secret`/`api_secret_key` is shared across every shop that installs the app, an HMAC that is valid for a body originating from Shop A's webhook delivery is equally "valid" if replayed with the `x-shopify-shop-domain` header changed to Shop B — the gem's `HmacValidator.validate(request)` will still return `true`, since the signature never covered the shop header in the first place.

### Impact Explanation
This breaks tenant isolation at the identity-binding layer this gem is responsible for: an app's webhook handler receives `WebhookMetadata#shop` as an authenticated fact when it is not authenticated at all. A multi-tenant app using this gem's `Registry.process` to dispatch/store webhook data keyed by `shop` can be made to attribute another merchant's data/event to an attacker-chosen shop identifier, i.e. cross-tenant data confusion, without the attacker needing the app's `client_secret`, an access token, or any privileged account — they only need one legitimately-signed webhook body (which they can capture as a normal merchant of the app) and the ability to resend it with a modified `shop-domain` header to the app's public webhook endpoint.

### Likelihood Explanation
Any merchant who installs the app is an "unprivileged internet user" relative to other tenants, and can capture at least one authentic webhook delivery for their own shop (bodies are frequently near-identical across shops for many topics, e.g. `app/uninstalled`, `shop/update`). Because the header is never checked against the signed content, replaying that captured request with a different `shop-domain` header is a purely mechanical exercise, and `Utils::HmacValidator.validate` provides no defense against it.

### Recommendation
Bind the tenant identity into the verified signable content, or otherwise verify it independently before trusting it:
- Include the `shop-domain` (and ideally `topic`/`webhook-id`) header in the value that is HMAC-verified, e.g. by having `to_signable_string` incorporate these header values, not just `@raw_body`.
- Alternatively, require callers to independently confirm that `request.shop` corresponds to a shop with a currently valid session before dispatching to handlers, rather than treating the header as trusted metadata once `HmacValidator.validate` passes.
- Document clearly in `docs/` that `Request#shop`/`#topic`/`#webhook_id` are NOT covered by the HMAC and must not be treated as authenticated by consumers of `ShopifyAPI::Webhooks::Registry`.

### Proof of Concept
1. App `X` is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`, both sharing the same `Context.api_secret_key`.
2. Attacker (a normal merchant on `shop-a.myshopify.com`) captures a legitimate webhook delivery, including its valid `x-shopify-hmac-sha256` header computed over the body.
3. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses `shop` as `shop-b.myshopify.com` from the header [4](#0-3) .
5. `Registry#process` calls `Utils::HmacValidator.validate(request)`, which passes because it only re-hashes `@raw_body` [5](#0-4) .
6. The handler receives `WebhookMetadata.new(topic:, shop: "shop-b.myshopify.com", body:, ...)` [6](#0-5)  and the app processes shop-a's payload as if it belonged to shop-b, breaking the shop-to-payload identity binding without ever needing shop-b's or the app's secret.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
