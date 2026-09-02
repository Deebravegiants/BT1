### Title
Webhook `shop`, `topic`, `webhook-id`, and `api-version` are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies the webhook's authenticity by computing an HMAC over the raw body only, but it dispatches the `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — to the registered handler as trusted metadata. This breaks the identity binding: `shop` acted on ≠ `shop` covered by the HMAC.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Utils::HmacValidator.validate` calls `validate_signature`, which computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC — i.e., it only proves the body is untampered and came from a holder of `Context.api_secret_key`; it says nothing about which shop or topic the body belongs to: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then forwards the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to the handler as if they were verified: [4](#0-3) 

Contrast this with the OAuth callback query object, `AuthQuery`, where `shop` is explicitly included inside `to_signable_string` and is therefore bound by the HMAC: [5](#0-4) 

The `api_secret_key` used to sign webhooks is the app's single `client_secret`, shared across every shop that has the app installed — it is not shop-specific. Consequently, any merchant who has installed the app receives, for their own shop, authentic `(raw_body, hmac)` pairs signed with that shared secret. Because `shop` (and `topic`/`webhook_id`) live outside the signed payload, a merchant can capture a legitimately-signed webhook delivered to their own endpoint and replay the identical `raw_body`/`x-shopify-hmac-sha256` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic`) with a different, victim shop's domain. `HmacValidator.validate` will still return `true`, because it only checks the body against the shared secret. `Registry.process` will then invoke the handler with `WebhookMetadata` claiming the data belongs to the victim shop: [6](#0-5) 

The equality that should hold — `shop bound by HMAC == shop the handler acts on` — is violated: the handler acts on `request.shop` (header), while the HMAC only binds `request.to_signable_string` (body).

### Impact Explanation
This is a cross-tenant identity binding failure: an attacker who legitimately controls one shop's installation can forge webhook deliveries that are validly signed (per this gem's `HmacValidator`) yet falsely attributed to a different shop. Any host application that uses the `shop` field returned in `WebhookMetadata` to select which tenant's records to update (a documented, expected usage pattern of this gem) will process data under the wrong shop context, i.e. cross-tenant access/data corruption.

### Likelihood Explanation
Medium-to-High for accounts already possessing an app installation: no special access is required beyond installing the app (which the report's threat model already allows, since the merchant/webhook-recipient is treated as an "unprivileged internet user" relative to other tenants of the same app). Capturing one's own webhook `raw_body` + `hmac` and replaying it with a different `shop-domain`/`topic` header is trivial once observed (e.g. via any endpoint logging, browser devtools if forwarded to a client-visible service, or simply by controlling the receiving server for the merchant's own shop).

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` inside the signed payload used for HMAC verification (mirroring how `AuthQuery#to_signable_string` binds `shop`), or otherwise cryptographically bind the header values to the request before trusting them in `WebhookMetadata`. At minimum, document that `WebhookMetadata#shop`/`#topic` are not authenticated and must not be used to select tenant scope without additional verification (e.g., cross-checking against a shop/session store keyed by data actually present in the signed body).

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-victim.myshopify.com`, both using the same app `client_secret`.
2. Attacker controls the webhook receiver for `shop-a.myshopify.com` and captures a legitimate delivery:
   - Headers: `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac>`
   - Body: `{"id": 123, ...}` (any body not containing an authenticated shop identifier is sufficient; many webhook topics' bodies do not restate the shop domain).
3. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` value to the same endpoint, but sets `x-shopify-shop-domain: shop-victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `raw_body`: [7](#0-6) 
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "shop-victim.myshopify.com", body: {...}, ...)`, causing the host application to act on `shop-victim`'s tenant context using attacker-supplied data — a cross-tenant write/read depending on the handler's implementation.

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
