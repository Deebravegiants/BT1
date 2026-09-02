## Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are taken from unsigned HTTP headers. `Webhooks::Registry.process` validates the HMAC and then dispatches the (unsigned) `shop`/`topic` values straight to the app's handler as trusted identity data, letting any holder of a single valid `(body, hmac)` pair relabel it as belonging to a different shop or topic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from HTTP headers that are never part of the signed data: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the signature over `to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` accepts the request as authentic once the body HMAC checks out, and then forwards the unsigned `shop`/`topic`/`webhook_id`/`api_version` header values straight into the handler's trusted metadata: [4](#0-3) 

The identity binding the app relies on is: **the shop/topic the handler trusts == the shop/topic that Shopify actually signed for**. Because the signature only covers the body, this equality does not hold — the header values can be swapped freely by anyone who possesses one valid `(body, hmac)` pair signed with the app's `api_secret_key`, since the HMAC recomputation is indifferent to whatever headers accompany that body.

### Impact Explanation
An unprivileged internet user who has legitimate access to trigger at least one webhook delivery from their own installed store (e.g. `orders/create`, or any topic with a predictable/empty body) can capture the resulting `(raw_body, x-shopify-hmac-sha256)` pair. They can then send that identical body+HMAC directly to the app's public webhook endpoint while substituting `x-shopify-shop-domain` with a victim shop's domain and/or `x-shopify-topic` with a sensitive topic (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`). `HmacValidator.validate` still succeeds because it only checks the body, so `Registry.process` dispatches the forged event as if it genuinely originated from the victim shop/topic — a cross-tenant identity break entirely inside this gem's webhook-processing code path.

### Likelihood Explanation
Webhook endpoints are, by design, unauthenticated HTTP endpoints reachable by anyone; the only gate is this library's HMAC check. Obtaining one legitimate `(body, hmac)` pair requires nothing more than installing the app on any store (or on a free/dev store) and letting it receive any webhook, which is trivial for any Shopify developer account holder. No credentials beyond that are needed.

### Recommendation
Include the identity-relevant header values (`shop`, `topic`, `webhook_id`, `api_version`) in the signed/verified payload, or otherwise validate `request.shop` against a known/installed shop and `request.topic` against the topic the webhook subscription was registered for before trusting them in `Registry.process` and `WebhookMetadata`. At minimum, document that consumers must not treat header-derived `shop`/`topic` as authenticated unless independently cross-checked, since the gem's own HMAC check does not cover them.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger any webhook topic (e.g. `orders/create`) and capture the raw request body `B` and the `x-shopify-hmac-sha256` header value `H` sent by Shopify (valid because it is HMAC-SHA256(`api_secret_key`, `B`)).
2. Send a new HTTP POST directly to the app's public webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com` and `x-shopify-topic: app/uninstalled` (or any other registered topic).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `H` against `HMAC(api_secret_key, B)` — this still passes.
4. The registered handler for `app/uninstalled` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "app/uninstalled", body: JSON.parse(B), ...)`, causing the app to perform victim-shop-attributed actions (e.g. data cleanup, redaction, or uninstall bookkeeping) that never actually happened for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
