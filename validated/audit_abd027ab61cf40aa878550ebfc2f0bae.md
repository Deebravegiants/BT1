I found a concrete identity-binding break in the webhook path that matches the reported bug class (a trusted action taken based on data not covered by the cryptographic check).

### Title
Webhook `shop` (tenant identifier) is trusted from an HTTP header not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop`, `topic`, `api-version`, and `webhook-id` values used to dispatch a webhook entirely from HTTP headers, while `Utils::HmacValidator` only verifies the raw request body against the HMAC. An unauthenticated caller who submits a POST with a stolen/replayed (or reused) valid body+HMAC pair can freely set the `X-Shopify-Shop-Domain` header to any value, and `Registry.process` will hand that attacker-controlled `shop` to the registered handler as if it were authentic.

### Finding Description
`Registry.process` validates the webhook solely via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` (the raw body only) and `request.hmac` (derived from the `hmac-sha256` header) against `Context.api_secret_key`. [1](#0-0) [2](#0-1) 

`Webhooks::Request#to_signable_string` returns only `@raw_body`, and none of `topic`, `shop`, `api_version`, or `webhook_id` — all sourced from headers via `shopify_header` — are part of the signed payload. [3](#0-2) 

`Registry.process` then builds `WebhookMetadata` directly from `request.shop` (the unauthenticated header) and hands it to the app's handler: [4](#0-3) 

This breaks the identity binding: `shop authenticated ≠ shop trusted by the handler`. The HMAC only proves "this body was signed with my secret for *some* valid Shopify webhook delivery" (or any prior legitimate webhook delivery with the exact same body, e.g. an empty-body/no-payload topic), not "this body was signed for *this* shop." Because many real Shopify webhook topics have identical or predictable bodies (e.g. `{}`  bodies, or bodies with no shop-identifying content), a body+HMAC pair captured from one shop's webhook delivery can be replayed with a different `Shop-Domain` header, and this gem will report it as valid and hand the forged shop value to the app.

### Impact Explanation
This is a cross-tenant data/authorization boundary crossing: an app that uses the `shop` field returned from `WebhookMetadata` (as the gem's own documentation and API design expects) to select which merchant's data to update/read will act on the wrong tenant. Since this gem is the trust boundary responsible for "verifying webhooks," and it explicitly authenticates the wrong thing (body, not the tenant claim used downstream), the finding fits the "cross-tenant access" impact bucket at the gem level, even though the ultimate blast radius depends on how a host app models per-shop authorization from `WebhookMetadata#shop`.

### Likelihood Explanation
Medium: the attacker needs a previously-valid `(raw_body, hmac)` pair — obtainable for any topic whose payload is shop-agnostic or identical across tenants (many topics have very small or templated JSON bodies), or simply captured from their own store's legitimate webhook deliveries (which they can trigger themselves) and replayed against the same app with a spoofed `Shop-Domain` header. No secret material is required; only network access to the app's public webhook endpoint.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the value that is cryptographically bound to the HMAC check (e.g., verify the raw body AND require the `shop` field to be independently validated against a known/registered shop domain via `ShopValidator`), or otherwise document/enforce that consumers must not trust `WebhookMetadata#shop` as an authenticated tenant identifier without additional binding.

### Proof of Concept
1. Obtain a valid `(raw_body, X-Shopify-Hmac-Sha256)` pair for any webhook topic with a static/shop-agnostic body (e.g., an app-uninstalled or shop-agnostic topic with `raw_body = "{}"`), signed by the target app's `api_secret_key` — this can be legitimately received by the attacker's own installed shop.
2. Replay the exact same `raw_body` and `hmac-sha256` header value to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and the desired `X-Shopify-Topic`.
3. `Utils::HmacValidator.validate` succeeds (body/HMAC match), and `Registry.process` dispatches `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` to the handler — the app now processes an event "for" a shop it did not actually originate from. [1](#0-0) [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
