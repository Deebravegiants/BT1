Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are read straight from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC and then dispatches `request.shop` (and `topic`/`webhook_id`) unchecked to the handler [3](#0-2) . This satisfies the rule's "field acted on but not covered by the HMAC" pattern.

### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates HMAC over the raw body only, but the `shop` (and `topic`/`webhook_id`) values used to route and process the webhook are taken from headers that are excluded from the signed payload.

### Finding Description
`HmacValidator.validate` calls `to_signable_string` on the `VerifiableQuery` implementation to compute the expected signature [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns just `@raw_body`; it never includes `shop`, `topic`, or `webhook_id` [1](#0-0) . Those three values are instead parsed directly from HTTP headers via `shopify_header` [2](#0-1) [5](#0-4) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching `request.shop` to the handler as the authoritative tenant identity: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [6](#0-5) .

The identity binding that should hold is: `shop authenticated by HMAC == shop delivered to handler`. Because the HMAC only signs `raw_body`, that equality does not hold — `shop` is a free-floating header that can be changed without invalidating the signature, as long as `raw_body` is unchanged. Any party that has captured (or otherwise gained, e.g. via logs, a proxy, or a shared/lower-privilege endpoint) one legitimately-HMAC'd webhook body/signature pair for a given topic can resend that exact body+HMAC pair with an arbitrary `X-Shopify-Shop-Domain` header. `Registry.process` will treat the HMAC as valid (since the body it signs is unchanged) and will call the app's handler believing the event belongs to the attacker-chosen shop, achieving cross-tenant confusion inside a multi-tenant app built on this gem, without ever knowing `api_secret_key`.

### Impact Explanation
This crosses the "cross-tenant access" bar in the Critical impact bucket: a value that determines which tenant's data/record a webhook handler updates (`data.shop`) can be forged independently of the cryptographic proof, letting one tenant's captured webhook traffic be replayed to make the host app believe it originates from a different tenant.

### Likelihood Explanation
The prerequisite is possession of a single valid `(raw_body, hmac)` pair for any shop/topic combination the attacker can produce or intercept (e.g., a webhook they receive for their own store, or one leaked via logging/network capture) — no `api_secret_key` is required. Given HMAC does not bind to `shop`, this is directly reachable through this gem's public `Webhooks::Registry.process`/`Webhooks::Request` API as documented.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) as part of the signed/verified payload used in `to_signable_string`, or otherwise require the handler-visible `shop` to be independently validated against a value bound to the signature (mirroring how `AuthQuery#to_signable_string` includes `shop` in the OAuth callback signature [7](#0-6) ).

### Proof of Concept
1. Attacker legitimately receives (or captures) a webhook for topic `orders/create` on `shop-a.myshopify.com` with raw body `B` and valid header `X-Shopify-Hmac-Sha256: H` (where `H = HMAC(api_secret_key, B)`).
2. Attacker resends the same `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `Webhooks::Request#hmac` still returns `H`; `to_signable_string` still returns `B`; `HmacValidator.validate` recomputes `HMAC(api_secret_key, B)` and it still equals `H`, so validation passes [8](#0-7) .
4. `Registry.process` invokes the handler with `shop: "shop-b.myshopify.com"` and the body originally destined for `shop-a`, even though `shop-b` never actually experienced that event [9](#0-8) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
