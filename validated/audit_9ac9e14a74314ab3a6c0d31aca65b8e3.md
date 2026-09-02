### Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using an HMAC that signs only the raw request body, while the `shop` and `topic` values used to dispatch and identify the webhook are read directly from unauthenticated HTTP headers. This breaks the identity binding: `hmac == HMAC(raw_body, secret)` while `shop`/`topic` used downstream are never part of what the HMAC protects.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop` and `topic` are parsed straight from attacker-controllable HTTP headers with no cryptographic binding: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then uses the *unsigned* `topic` to select the handler and passes the *unsigned* `shop` into the metadata delivered to the app's handler: [3](#0-2) 

Because the HMAC only covers the raw body bytes, any request whose body+hmac pair is valid for *any* topic/shop (e.g., a webhook the attacker legitimately received for their own shop, or any topic that produces the same raw body such as `"{}"`) can be replayed with arbitrary `shopify-shop-domain` and `shopify-topic` header values without invalidating the HMAC check. This is precisely the "field acted on but not covered by the HMAC" class: the shop/topic identity used to route and label the webhook is not part of `to_signable_string`, so `Utils::HmacValidator.validate` verifying the body says nothing about which shop or topic the request is claiming to be.

### Impact Explanation
An external actor who can obtain (or brute-force, since bodies like `"{}"` are trivial and reused across topics in tests/real deliveries) one valid `(raw_body, hmac)` pair can invoke the app's registered webhook handler while asserting an arbitrary `shop` and `topic` of their choosing. If the app's webhook handler trusts `WebhookMetadata#shop` (as intended, since it's the only shop identifier provided) to look up or mutate per-tenant state, this allows cross-tenant impact — the core exploit class called out as Critical/High in the rules (cross-tenant access via an identity field that is checked/asserted but not actually bound by the cryptographic verification).

### Likelihood Explanation
Reaching this requires only an HTTP request to the app's webhook endpoint with a previously-observed or predictable `(body, hmac)` pair (no `api_secret_key` needed) — an unprivileged internet user or the operator of another shop that installed the same app can obtain one from their own legitimate webhook deliveries, then replay it with modified `shopify-shop-domain`/`shopify-topic` headers.

### Recommendation
Include `shop` and `topic` (and any other header-derived identity fields consumed later) in the signable string that the HMAC is computed over, or otherwise cryptographically bind them, so that `Utils::HmacValidator.validate` on a `Webhooks::Request` proves the shop/topic asserted in the headers, not just the body bytes.

### Proof of Concept
1. Register a webhook handler for topic `orders/create`.
2. Receive (or replay from your own shop) any legitimate webhook delivery, capturing `raw_body` and header `shopify-hmac-sha256`.
3. Re-send the same `raw_body`/`hmac` to the webhook endpoint, but set `shopify-shop-domain: victim-shop.myshopify.com` and `shopify-topic: orders/create`.
4. `Utils::HmacValidator.validate` (which only signs `@raw_body`) still returns `true`, and `Registry.process` invokes the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the request never proved it originated for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
