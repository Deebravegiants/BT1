### Title
Webhook `shop`, `topic`, and `api-version` fields are unauthenticated and unbound to the HMAC signature, enabling cross-tenant impersonation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the shop domain, topic, and API version that the library uses to route and attribute the webhook are taken from unauthenticated HTTP headers. This breaks the intended binding `verified(shop, topic, body) == acted_on(shop, topic, body)`: only `body` is actually covered by the signature, while `shop` and `topic` are trusted verbatim from headers that carry no cryptographic protection.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.), which are not part of the signed payload: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC solely against `to_signable_string`, i.e. against `@raw_body`: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` performs the HMAC check and then dispatches the handler using the unauthenticated `request.topic`, and passes the unauthenticated `request.shop` straight into `WebhookMetadata` given to the app's handler code: [4](#0-3) 

The result: `Utils::HmacValidator.validate(request)` proves only "the bytes of `raw_body` were signed with `api_secret_key`" — it does not prove "this body was intended for `shop`" or "this body was intended for `topic`". Any request whose `raw_body` matches a body/signature pair the attacker has legitimately observed (e.g. from a webhook Shopify sent to the attacker's own shop/app installation) will pass `HmacValidator.validate` unchanged if replayed with a different `shopify-shop-domain` or `shopify-topic` header, because those header values are never part of `to_signable_string`.

### Impact Explanation
This is a High-severity issue matching "cross-tenant access": the shop identity that the app's webhook handler uses to attribute and act on data (`WebhookMetadata#shop`) is not the shop actually verified by the HMAC. An attacker who can capture one legitimately-signed `(raw_body, hmac)` pair — trivially achievable by installing the app on their own (attacker-controlled) shop and observing the webhooks Shopify delivers to their endpoint, since `raw_body` for many topics (e.g. minimal `app/uninstalled`, `shop/redact`) is small/predictable or fully attacker-influenced — can replay that exact body to the app's public webhook endpoint while forging the `shopify-shop-domain` and/or `shopify-topic` headers to claim the event belongs to a different merchant/tenant. `Utils::HmacValidator.validate` will still return `true` because it never inspects those headers, and the app's handler will process/act on the payload under the impersonated shop's identity — a cross-tenant identity-binding bypass structurally analogous to the reported bug, where the verified/signed target diverges from the target actually acted upon.

### Likelihood Explanation
Likely reachable by any unprivileged internet user: webhook endpoints are public HTTP(S) URLs (no OAuth/session required to POST to them), `api_secret_key` is not needed by the attacker since they only replay an already-validly-signed body they legitimately received, and the only requirement is installing the app once on a shop they control to harvest a valid `(body, hmac)` pair.

### Recommendation
Include the routing/identity fields (`shop`, `topic`, and ideally `api_version`/`webhook_id`) in the HMAC-signable string, or otherwise cryptographically bind them to the signed body (e.g., verify a canonicalized string of `topic + shop + raw_body` rather than `raw_body` alone) inside `ShopifyAPI::Webhooks::Request#to_signable_string`, so that `HmacValidator.validate` fails whenever any of those header values are altered from what Shopify originally signed for that specific delivery.

### Proof of Concept
1. Register/install the app on attacker-controlled shop `attacker.myshopify.com` and receive a legitimate webhook, e.g. `shop/redact` with body `{}` and header `x-shopify-hmac-sha256: <valid-hmac-of-{}>`.
2. Send a forged HTTP POST to the app's public webhook endpoint with the same body `{}` and the same valid `x-shopify-hmac-sha256`, but change:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic: customers/redact` (any topic whose signed body coincidentally matches, or one where body content is irrelevant to the handler logic)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — which passes because it only checks `raw_body` against the (unchanged, still-valid) signature — then invokes the handler with `shop: "victim.myshopify.com"`, causing the app to execute tenant-sensitive logic (e.g. GDPR redaction, uninstall cleanup) against a shop the attacker does not control.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
