### Title
Webhook `X-Shopify-Shop-Domain` header is trusted for tenant identification without HMAC coverage - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` computes the HMAC only over the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then passes the header-derived `shop` value straight into the handler as the tenant identity, without any binding between that value and the signed bytes.

### Finding Description
The gem's webhook signature check is: [1](#0-0) 

only the raw body is fed into `Utils::HmacValidator.validate`: [2](#0-1) 

but `shop` is read from the `x-shopify-shop-domain` header, which is completely outside the signed bytes: [3](#0-2) 

`Registry.process` then trusts this unauthenticated header value as the tenant identifier and forwards it to the app's handler as the authoritative shop for the event: [4](#0-3) 

This is the same bug class as the report's "field acted on but not covered by the HMAC" binding break: the equality the code implicitly assumes is `hmac_verified_bytes == identity_used_downstream`, but in reality `hmac_verified_bytes` (the raw body) and `identity_used_downstream` (`request.shop`, from a header) are disjoint. Any party that can obtain one genuinely-signed webhook body/HMAC pair — trivially available to any developer who installs their own public app on their own dev/test store and receives a real webhook from Shopify — possesses a `(raw_body, hmac)` pair that stays valid forever for that body, independent of which `shop-domain` header value accompanies it. They can then replay the same body+hmac while substituting an arbitrary victim shop domain in the `X-Shopify-Shop-Domain` header (this is a header on a request the attacker sends to their own app's webhook endpoint, an unprivileged action requiring no Shopify credentials, access token, or `client_secret`), and `Utils::HmacValidator.validate` will still return `true` because it never inspects headers.

### Impact Explanation
If the host application (as instructed by the library's own `WebhookMetadata`) uses `data.shop` to select which merchant's session/config/database record to act on — the documented and expected usage pattern — an attacker can make the app process attacker-chosen body content under an arbitrary victim shop's identity, i.e., a cross-tenant data injection through this gem's own webhook-verification API. This maps to the Critical "cross-tenant access" category in scope, since the identity boundary that separates tenants (`shop`) is not actually authenticated by the mechanism the library exposes as its authentication primitive (`Utils::HmacValidator.validate`).

### Likelihood Explanation
Low-to-moderate: exploitation requires the attacker to have registered a webhook subscription on their own store (any developer/merchant can do this for free with a public or custom app) to obtain one valid `(body, hmac)` pair, and requires the host application to trust `shop` from `WebhookMetadata` for tenant selection without additional out-of-band verification (e.g., cross-checking against known subscribed shops) — a very common, and the library-documented, pattern (`handler.handle(data: WebhookMetadata.new(... shop: request.shop ...))`).

### Recommendation
Include the tenant-identifying header(s) (`shop-domain`, and ideally `topic`/`webhook-id`) in the signable string used for HMAC verification, or otherwise cryptographically bind the reported `shop` to the verified body (e.g., require the body to embed and cross-check the shop, or maintain a registry of `(shop, webhook_id)` pairs from Shopify's registration API and reject events whose header shop was never subscribed to that specific `webhook_id`).

### Proof of Concept
```ruby
# 1. Attacker installs their own public/custom app instance on "attacker.myshopify.com"
#    and receives a genuine webhook from Shopify:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => real_signature_from_shopify, # valid HMAC over raw_body
  "x-shopify-shop-domain" => "attacker.myshopify.com",
  "x-shopify-webhook-id" => "wh_123",
  "x-shopify-api-version" => "2024-01",
}
raw_body = captured_real_body

# 2. Attacker replays the exact same body+hmac to the app's webhook endpoint,
#    only swapping the shop-domain header to a victim shop they were never granted access to:
forged_headers = headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# 3. HMAC validation still passes because it only checks raw_body, not headers:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# the app now processes attacker-controlled data as if it came from victim-shop.myshopify.com
``` [5](#0-4)

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
