## Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook shop-domain spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` value from the `x-shopify-shop-domain` HTTP header, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates is computed **only** over the raw request body. The `shop` header is never part of the signed material, so the identity binding "authenticated shop == HMAC-verified shop" does not hold — any request with a validly-signed body is accepted regardless of which shop the `shop-domain` header claims.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `shop-domain`/`x-shopify-shop-domain` header, which is not part of the signable string at all: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC using `verifiable_query.to_signable_string` (i.e. only the body) and the app's single, shop-independent `api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.shop` directly, passing it into `WebhookMetadata` for the handler to act on: [4](#0-3) 

Because the same `api_secret_key` is used for every shop that has installed the app, and the HMAC covers only the body bytes, a valid `(raw_body, hmac)` pair generated for one shop's webhook delivery remains valid no matter what `shop-domain` header is attached. The equality the code implicitly assumes — *the shop that authenticated the payload (via HMAC) equals the shop claimed by `request.shop`* — does not hold, since `shop` is unauthenticated header data.

### Impact Explanation
An unprivileged internet user who has installed the app on their own shop (Shop A) receives legitimately signed webhook deliveries for Shop A. They can capture one `(raw_body, x-shopify-hmac-sha256)` pair and replay it to the app's webhook endpoint while substituting `x-shopify-shop-domain` with an arbitrary other tenant's domain (Shop B). `HmacValidator.validate` will still return `true` (it only checks the body signature against the app-wide secret), so `Registry.process` will invoke the handler with `WebhookMetadata#shop == "shop-b.myshopify.com"` and attacker-controlled body content. Any host application that uses the library's `shop` field as the tenant key when persisting/acting on webhook data (the pattern this gem's own docs and `WebhookMetadata` promote) will attribute attacker-chosen data to a shop the attacker does not control, i.e., cross-tenant data injection/corruption. This matches the Critical class "cross-tenant access" enabled purely through this gem's verification logic.

### Likelihood Explanation
Any merchant/installer of the app (a completely unprivileged actor with respect to other tenants) can trigger this by installing the app in their own shop to obtain one valid signed webhook, then re-sending it with a modified header — no access token, `client_secret`, or privileged access is required. The library performs no per-shop binding check between the verified bytes and the claimed shop, so exploitation only requires basic HTTP tooling.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-verified material, or otherwise cryptographically bind the `shop` value to the signed payload before exposing it via `WebhookMetadata`. At minimum, document/enforce that `Registry.process` should validate that `request.shop` corresponds to a shop session the app expects, and consider deriving the signable string from `shop + raw_body` so a signature is only valid for the specific shop it was issued for.

### Proof of Concept
1. Install the app on Shop A (`shop-a.myshopify.com`) and receive a genuine webhook delivery with headers:
   - `x-shopify-hmac-sha256: <valid-hmac-of-raw-body>`
   - `x-shopify-shop-domain: shop-a.myshopify.com`
   - raw body `{"id":123,...}`
2. Resend the exact same raw body and HMAC header to the app's webhook endpoint, but change:
   - `x-shopify-shop-domain: shop-b.myshopify.com`
3. `ShopifyAPI::Utils::HmacValidator.validate` (called from `Registry.process`) computes the HMAC purely over the raw body using the app's global `api_secret_key`, which still matches, so validation succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: <attacker-influenced-body>, ...)`, causing the app to process attacker data under Shop B's identity.

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
