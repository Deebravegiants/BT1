### Title
Webhook shop identity spoofing via unsigned `X-Shopify-Shop-Domain` header — cross-tenant webhook processing (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then hands the caller-supplied `shop-domain` header — a value that is never covered by that HMAC — to the application's handler as the trusted tenant identifier. Because the HMAC only binds the body bytes, an attacker who possesses one legitimately-signed webhook (trivially obtainable by installing the app on their own store) can replay that exact body+signature while substituting an arbitrary `X-Shopify-Shop-Domain` header, causing the app to process attacker-controlled data under a victim shop's identity.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding to the signed content: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which internally calls `request.to_signable_string` (i.e., body only) and `request.hmac`, and on success immediately trusts `request.shop` as the identity passed to the handler: [3](#0-2) 

`HmacValidator.validate_signature` computes the digest exclusively from `verifiable_query.to_signable_string`, so any header not included in that string — including `shop-domain` — can be altered post-signing without invalidating the check: [4](#0-3) 

**Binding broken (equality that should hold but doesn't):**
`shop` used to attribute the webhook to a tenant (`data.shop` passed to the handler) ≠ `shop` covered by the HMAC that authenticates the request. The gem authenticates "this body came from Shopify, signed with our secret" but then trusts an unauthenticated header for "which shop this event belongs to." These are two different pieces of information that the gem conflates.

Before attacker action: legitimate webhook for Shop A arrives with `X-Shopify-Shop-Domain: shop-a.myshopify.com`, `X-Shopify-Hmac-Sha256` = HMAC(raw_body, secret). `HmacValidator.validate` passes because it checks only the body.

After attacker action: attacker captures this exact `raw_body` + `hmac` pair from their own store (Shop A, which they legitimately control), and re-sends it to the same public webhook endpoint but with `X-Shopify-Shop-Domain: shop-victim.myshopify.com`. `HmacValidator.validate` still passes (body and hmac are unchanged, and this check never looks at the shop header), so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "shop-victim.myshopify.com", body: <attacker's captured body>, ...)`. [5](#0-4) 

The application-level handler, which trusts `data.shop` to scope database writes, billing, order processing, etc., now executes attacker-influenced business logic under the wrong tenant.

### Impact Explanation
This breaks the tenant boundary that the HMAC verification is supposed to enforce: the gem's own webhook-processing contract is "an HMAC-valid request is a genuine event for the shop it names," but the shop name is not part of what is verified. Any app relying on `ShopifyAPI::Webhooks::Registry` + `WebhookMetadata#shop` for per-shop authorization or data scoping is exposed to cross-tenant data corruption/impersonation, satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
The attacker only needs a single legitimately-signed webhook body from any shop they control (installing an app on a free development store is sufficient to receive one), plus the ability to POST to the app's public webhook endpoint with a modified header — no access token, `client_secret`, or privileged account is required. The replay works because the vulnerable code path (`HmacValidator.validate` called with only body-derived `to_signable_string`) is unconditional and shared by every consumer of `Webhooks::Registry.process`.

### Recommendation
- Do not treat `Request#shop` as an authenticated value based on HMAC success alone; if the header must be trusted, include it (and `topic`, `api_version`, `webhook_id`) in the signed payload used for verification, or cross-check it against the shop associated with the specific `webhook_id`/subscription registered via the Admin API.
- At minimum, document prominently that `HmacValidator.validate` only authenticates body integrity/origin-secret possession, not the `shop-domain` header, so host applications do not conflate the two, and consider exposing a stricter validation path that binds shop identity to the signature.

### Proof of Concept
```ruby
# Step 1: attacker installs the app on their own store "attacker-shop.myshopify.com"
# and receives a legitimate webhook with body B and header:
#   X-Shopify-Hmac-Sha256: H = HMAC-SHA256(secret, B)
#   X-Shopify-Shop-Domain: attacker-shop.myshopify.com

# Step 2: attacker replays the exact same body/hmac to the app's public
# webhook endpoint, only changing the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => H,                 # unchanged, still valid for body B
  "x-shopify-shop-domain" => "victim-shop.myshopify.com",  # attacker-controlled
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)

# HmacValidator.validate(request) returns true, because it only hashes B.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...))
```
`Registry.process` never rejects this because `Utils::HmacValidator.validate` is defined over `to_signable_string` (body only): [6](#0-5) [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
