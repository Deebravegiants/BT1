## Title
Webhook `shop` (and other Shopify headers) are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the shop-identifying header (`shop-domain`, plus `topic`, `webhook-id`, `api-version`) is read directly from unauthenticated HTTP headers and handed to the app's webhook handler as trusted tenant identity. This breaks the intended binding: `HMAC(body, client_secret) == received_hmac` should imply `shop header == the shop that produced this signed payload`, but the signature never covers the header, so the two are independently controllable.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight out of caller-supplied headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` only validates the HMAC over the body and then immediately trusts `request.shop` to build the tenant-scoped metadata passed to the app's handler: [3](#0-2) 

The `VerifiableQuery` interface used by `HmacValidator` confirms that only the value returned by `to_signable_string` is protected by the signature: [4](#0-3) 

Because Shopify signs `hmac = HMAC-SHA256(raw_body, client_secret)` and never includes the shop domain in that computation, any request with a *valid* `(raw_body, hmac)` pair — which an attacker who merely controls one connected/legitimate shop can obtain by triggering a real webhook for their own store — can be replayed with the `shop-domain` header rewritten to any other value. `HmacValidator.validate` will still return `true` because it only re-derives the HMAC from the (unchanged) body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged shop.

### Impact Explanation
This is a cross-tenant identity-binding break: an attacker who owns a real, installed instance of the app on their own shop can generate legitimate `(body, hmac)` pairs at will (by taking normal actions that fire webhooks), then replay them against the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header swapped to a victim shop. If the host application uses `WebhookMetadata#shop` to select which merchant's data/session the webhook body should be applied to (the documented and expected usage pattern), the attacker can inject attacker-controlled webhook content that gets attributed to another merchant's tenant — a cross-tenant access/data-integrity issue satisfying the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker needs a *valid* `client_secret`-signed `(body, hmac)` pair, which any merchant who has installed the app can produce simply by using their own shop normally (webhooks are delivered to the app's public endpoint, so the attacker can capture their own webhook's raw body + HMAC and replay it with a different `shop-domain` header). No access to the app's `client_secret`, another merchant's access token, or TLS interception is required — only network access to the public webhook endpoint and a legitimate (even free/trial) install of the target app.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) inside the signed material, or otherwise cryptographically bind the header-derived `shop` to the verified body — e.g., have `to_signable_string` incorporate the shop header, or require the caller to separately validate that `request.shop` matches an expected/registered shop for the session before trusting it. At minimum, document that `WebhookMetadata#shop` is not authenticated by the HMAC and must not be used as the sole tenant-selection key.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and performs an action that fires a real webhook (e.g., `orders/create`).
2. Attacker's endpoint (or a proxy) captures the raw body `B` and the valid header `x-shopify-hmac-sha256: H = HMAC-SHA256(B, client_secret)`.
3. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and same `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(B, client_secret)` (matches `H`, since body `B` is unchanged) and returns `true`: [5](#0-4) 
5. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim.myshopify.com"` and invokes the app's handler, which processes attacker-controlled body content as if it originated from the victim shop. [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
