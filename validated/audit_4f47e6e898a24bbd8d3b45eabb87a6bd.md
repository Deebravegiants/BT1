### Title
Webhook shop/topic identity is trusted from unauthenticated HTTP headers while the HMAC only signs the raw body, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` and `topic` fields directly from HTTP headers, but the HMAC verification performed by `Utils::HmacValidator` only covers the raw request body. This breaks the binding: `hmac_verified_bytes (raw_body) != identity_bytes (shop-domain / topic headers)`. `Registry.process` trusts these unauthenticated header values to build the `WebhookMetadata` that is handed to the app's handler as the source of tenant truth.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to that body: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e., the body) and compares it to the `hmac-sha256` header value — it never incorporates `shop`, `topic`, or `webhook_id`: [3](#0-2) 

`Registry.process` validates only this body-HMAC, then immediately trusts `request.topic` and `request.shop` (unauthenticated header values) to route to a handler and construct the `WebhookMetadata` that becomes the app's source of truth for "which shop this event belongs to": [4](#0-3) [5](#0-4) 

As a result, an attacker who possesses one legitimate `(raw_body, hmac)` pair — trivially obtainable by installing/operating their own store as an app tenant and capturing a webhook Shopify sent them — can replay that exact body to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`) header with a different tenant's shop domain (or another registered topic). The HMAC check still passes because it only re-derives the signature from the untouched body, while the `shop`/`topic` used by the handler are the attacker-supplied header values.

### Impact Explanation
This crosses a tenant boundary: a multi-tenant app that keys business logic (e.g., "update shop X's data", audit logging, entitlement checks, mandatory `shop/redact` / `customers/redact` handling) off `WebhookMetadata#shop` can be made to process another merchant's data or apply actions to the wrong `shop`, purely by forging headers with a body the attacker legitimately obtained for their own tenant. This matches the "cross-tenant access" High-impact category, since it lets one merchant/attacker inject events that the app attributes to an arbitrary other shop without ever needing the app's `client_secret` or an access token.

### Likelihood Explanation
Likelihood is moderate-to-low in practice but reachable without any privileged access: the attacker needs (1) the ability to send arbitrary HTTP requests to the app's already-public webhook receiving endpoint, and (2) one valid `(body, hmac)` pair, which any installed merchant/tenant of the app can capture for their own shop through ordinary use. No TLS interception, leaked secret, or admin access is required — only normal use of the app as any tenant plus a forged HTTP request to the app's own endpoint.

### Recommendation
Bind the tenant-identifying fields into the signed material, or otherwise verify them independently of headers:
- Prefer deriving `shop`/`topic` from data embedded and covered by the signature (e.g., include them in the signable string alongside the body, mirroring the OAuth `AuthQuery#to_signable_string` approach that binds `shop`/`host`/etc.), or
- Cross-check the header-derived `shop` against a shop identity obtained from a source that is itself bound to the HMAC (e.g., look up the webhook by `webhook_id` from Shopify and confirm the topic/shop match before dispatching), or
- At minimum, document prominently that `shop`/`topic` headers are unauthenticated and instruct integrators to independently corroborate `WebhookMetadata#shop` against their own record of shops that have valid registrations for the delivered `webhook_id`/topic before trusting it for tenant-scoped actions.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` (no elevated privileges needed — this is normal app installation).
2. Shopify sends a legitimate webhook to the app's public endpoint for a topic the app is registered for, e.g.:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: wh_123
   Body: {"id": 1, "note": "attacker-controlled order payload"}
   ```
3. Attacker captures this exact `(body, hmac)` pair (they can see it because it's their own webhook, e.g., via a proxy/logging on their own infrastructure receiving the callback).
4. Attacker replays the identical body and `hmac` header to the same public endpoint, but swaps:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — unchanged — so validation succeeds.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker-controlled JSON>, ...)`, and any app logic keyed on `data.shop` now processes attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

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
