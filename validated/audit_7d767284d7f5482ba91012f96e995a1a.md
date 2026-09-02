### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives its `shop` accessor from the `X-Shopify-Shop-Domain` header, but the HMAC signature computed and verified by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body via `to_signable_string`. The `shop` field is passed unverified into `WebhookMetadata` and handed to the application's `WebhookHandler#handle`, breaking the intended binding: `hmac(secret, raw_body) == valid` should imply `(raw_body, shop) belongs together`, but the shop identity is never part of the signed material.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read straight from an attacker-controllable header with no cross-check: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate`, which computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the supplied header value: [3](#0-2) [4](#0-3) 

Since the signable string is exactly the raw body (independent of `shop`), and the `api_secret_key` used to sign/verify is a single per-app secret shared across every shop that has installed the app, a valid HMAC computed for one shop's webhook payload remains valid for any other shop's request headers with the same body. The `shop` claim that ends up in `WebhookMetadata` — which host applications rely on to know which tenant the payload is for — is asserted by the equality `hmac_valid == true` even though `hmac_valid` says nothing about `shop`. The binding that should hold, `verified(shop, body) == (hmac over shop||body)`, does not hold; only `verified(body)` holds.

### Impact Explanation
An attacker who is a legitimate, unprivileged merchant/user of the app (Shop A) can capture one of their own genuine webhook deliveries (topic + body + valid HMAC, all computed with the same app-wide `api_secret_key`) and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header changed to a victim shop (Shop B). `HmacValidator.validate` will still succeed because it never inspects `shop`, and `Registry.process` will call the handler with `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: <shop-A's data>, ...)`. Any host application that uses `data.shop` to look up per-tenant records, sessions, inventory, or to trigger tenant-scoped side effects (typical usage pattern documented for this gem) can be made to associate Shop A's data with Shop B's tenant, or process controlled/forged data as if it originated from a shop the attacker does not control — a cross-tenant data-integrity/isolation break in the trust boundary this gem provides. This matches the Critical "cross-tenant access" impact category, since the gem's core promise for webhook processing is authenticating both content and origin (shop) together.

### Likelihood Explanation
The prerequisite is only that the attacker installs the app on a shop they control (an unprivileged position any Shopify merchant can obtain), triggers a webhook for a topic that is registered, captures the raw body + valid `hmac-sha256` header from their own delivery, and resends it to the app's public webhook endpoint with a modified `shop-domain` header. No secrets, TLS interception, or privileged access are required, and no host-application misconfiguration beyond normal, documented use of `WebhookMetadata#shop` for tenant scoping is needed. Likelihood is high for apps with a publicly reachable webhook endpoint (the standard deployment model).

### Recommendation
Include the shop domain (and ideally topic/api-version) in the signed material, or otherwise cryptographically bind the identity fields to the HMAC before trusting them:
- Have `Webhooks::Request#to_signable_string` return a value that folds the `shop-domain` header (and topic) together with the raw body, e.g. `"#{shop}\n#{topic}\n#{@raw_body}"`, and validate that same construction on the Shopify side is unaffected (Shopify signs only the raw body by protocol, so this requires the gem to independently corroborate `shop` via a source that isn't attacker-controlled, e.g. cross-checking against a shop registered/stored per matching webhook subscription, or documenting to consumers that `shop` in `WebhookMetadata` is NOT covered by HMAC and must not be trusted without additional verification).
- At minimum, update documentation and `WebhookMetadata` to explicitly flag that `shop` is unauthenticated, and provide/require an app-side mechanism (e.g., correlating webhook IDs registered per shop) before using `data.shop` for tenant-sensitive decisions.

### Proof of Concept
```ruby
require "shopify_api"
require "openssl"
require "base64"

ShopifyAPI::Context.setup(
  api_key: "key", api_secret_key: "shared_app_secret",
  host: "example.com", scope: [], is_embedded: true,
  api_version: "2024-01", is_private: false
)

raw_body = '{"id":1,"note":"legit order from shop A"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "shared_app_secret", raw_body)

# Attacker captured this valid signature from their own shop (shop-a), then
# resends the same body/signature claiming it's from the victim (shop-b).
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "shop-b.myshopify.com", # victim, not the shop that actually sent it
  "x-shopify-webhook-id" => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# This succeeds: HMAC only covers raw_body, not shop-domain.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata(shop: "shop-b.myshopify.com", body: {...}, ...))
```
The handler receives data claiming to be from `shop-b.myshopify.com` despite never having been sent by that shop, purely because the HMAC validation in `Utils::HmacValidator` and `Webhooks::Request#to_signable_string` never bind the `shop` field into the signed content.

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
