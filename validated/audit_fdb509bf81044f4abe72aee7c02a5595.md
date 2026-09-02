Confirmed: `WebhookMetadata` (defined in `lib/shopify_api/webhooks/webhook_handler.rb`) blindly carries `shop: request.shop` into the app's handler with no cryptographic binding to that value.

### Title
Webhook shop identity is not covered by HMAC verification, allowing tenant spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the unauthenticated `X-Shopify-Shop-Domain` header, while `Utils::HmacValidator` only verifies the raw request body. The `shop` value is handed to the app's webhook handler as trusted, tenant-scoped metadata, even though it was never part of the signed content.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string and compares it to the `hmac-sha256` header: [2](#0-1) . Meanwhile, `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relation to the signature at all: [3](#0-2) .

`Registry.process` verifies the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) . `WebhookMetadata#shop` is a plain `String` const with no further validation or cross-check against the signed body: [5](#0-4) .

The broken equality: `shop bound by HMAC signature == shop trusted for tenant routing` does not hold. The signature only proves "this body was produced with the app's secret", it does not prove "for this particular shop". An unprivileged merchant who has legitimately installed the app on their own store (Shop A) will receive genuine, correctly-signed webhook deliveries. Because the header carrying the tenant identity is excluded from the signed payload, that same attacker can capture one legitimate `(raw_body, hmac)` pair from their own store and replay it directly to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header swapped to a victim shop (Shop B). `HmacValidator.validate` still succeeds because it never inspected the header, and `Registry.process` will label the resulting `WebhookMetadata` with `shop: "shopB.myshopify.com"`, causing the host application to attribute attacker-controlled payload/topic events to the victim tenant.

### Impact Explanation
This breaks the tenant boundary the HMAC check is meant to enforce: an attacker with only their own real, low-privileged store can forge a "verified" webhook that the app associates with an arbitrary victim shop domain. Any app logic that keys tenant-scoped behavior off `WebhookMetadata#shop` (e.g., looking up a session/access token for that shop, updating per-shop data, honoring mandatory compliance topics like `customers/redact` or `shop/redact`) can be triggered against a shop the attacker does not control, which is a cross-tenant access impact.

### Likelihood Explanation
Likelihood is limited by the need for the attacker to obtain at least one genuine `(raw_body, hmac)` pair, which any merchant with the app installed on their own store can trivially generate (e.g., by triggering an order/customer event on their own shop and capturing the resulting webhook POST before/at their own endpoint, or replaying it directly to the app's public webhook URL). No access token, `client_secret`, or privileged account is required — only a normal merchant account, which satisfies the "unprivileged internet user" bar for this scan.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the value that is HMAC-verified, or otherwise cryptographically bind `Request#shop` to the signed body before constructing `WebhookMetadata`. At minimum, `HmacValidator`/`Request#to_signable_string` should incorporate the `shopify-shop-domain` header into the signed string so a mismatch invalidates the signature, matching the same "bind the identity field into the signature" pattern already used correctly for `AuthQuery#to_signable_string` (which does include `shop`): [6](#0-5) .

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`, and configures/triggers a webhook (e.g. `customers/data_request`) so Shopify delivers a genuine POST to the app's webhook endpoint with a valid `X-Shopify-Hmac-Sha256` header computed over the raw body using the app's `api_secret_key`.
2. Attacker captures the exact `raw_body` and `X-Shopify-Hmac-Sha256` value from that legitimate delivery.
3. Attacker sends a new POST directly to the same public webhook endpoint, reusing the identical `raw_body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only checks the (unchanged) body against the (unchanged) HMAC — see `to_signable_string` at [1](#0-0) .
5. `Registry.process` builds `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` and invokes the app's handler as if the event genuinely originated from the victim shop: [4](#0-3) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
