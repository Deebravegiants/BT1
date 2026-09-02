### Title
Webhook `shop` identity field is excluded from HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the webhook's `hmac` and `shop` from separate, independent HTTP headers, but only the raw request body is covered by the HMAC signature used for verification. `Registry.process` trusts the unauthenticated `shop` field to build `WebhookMetadata`, which host applications use to attribute the webhook payload to a tenant.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, bytes-that-include-shop)`, so that the `shop` value handed to the app is cryptographically bound to the signature that authenticates the request as genuinely originating from Shopify for that shop.

In this gem, that binding is broken: [1](#0-0) 

- `hmac` is read from the `x-shopify-hmac-sha256` / `shopify-hmac-sha256` header.
- `shop` is read from the entirely separate `x-shopify-shop-domain` / `shopify-shop-domain` header.
- `to_signable_string` — the value that `HmacValidator` actually verifies against `hmac` — returns only `@raw_body`. It contains **no reference to `shop`, `topic`, `webhook_id`, or `api_version`.**

`HmacValidator.validate` calls `to_signable_string` and compares it against `hmac` using the shared `api_secret_key`: [2](#0-1) 

`Registry.process` then trusts the *unauthenticated* `shop` header directly, passing it into `WebhookMetadata`, which is delivered to the app's own webhook handler: [3](#0-2) [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that has installed the app (it is not per-shop), *any* raw body + valid HMAC pair that was legitimately produced for one tenant remains a valid HMAC pair for any other value of the `shop-domain` header. The signature says nothing about which shop the payload belongs to — only that the *body bytes* were signed with the app's secret at some point, for some shop.

Before vs. after the attack:
- Before: legitimate webhook for shop A → `headers = {shop-domain: "A.myshopify.com", hmac-sha256: HMAC(secret, body)}` → `HmacValidator.validate` = true, `WebhookMetadata.shop == "A.myshopify.com"`.
- After: attacker (an ordinary merchant who installed the app on shop A and can observe/replay webhooks legitimately delivered to their own endpoint) resends the identical `raw_body`/`hmac` pair but swaps the `x-shopify-shop-domain` header to `"B.myshopify.com"` (any victim tenant, real or fabricated) → `HmacValidator.validate` still returns true (it never inspected `shop`), and `WebhookMetadata.shop == "B.myshopify.com"` is handed to the host app's handler as if Shopify itself vouched for it.

This is a genuine identity-binding gap unique to this gem's `to_signable_string`/`shop` split, matching the report's flagged pattern of "a field acted on but not covered by the HMAC."

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` to route/attribute webhook effects per tenant (the exact pattern the gem's own docs and `WebhookHandler#handle(data:)` API encourage) can be made to process a forged event as belonging to a shop other than the one that actually produced/signed it. An attacker who is merely an installed, unprivileged merchant of their own shop — never obtaining any other tenant's access token, session, or the app's `client_secret` — can trigger cross-tenant state changes (e.g., replaying a captured `app/uninstalled`, `shop/redact`, or `customers/data_request` payload while spoofing another shop's domain) purely by controlling one HTTP header on the replayed request. This falls under the Critical category of "cross-tenant access" because the shop-tenant boundary is not actually enforced by the signature the gem asks callers to trust.

### Likelihood Explanation
Likelihood is limited to attackers who already have a legitimate app installation (so they can capture a genuinely-signed body/HMAC pair for at least one payload/topic), and requires that they can reach the app's public webhook endpoint with attacker-controlled headers (webhook endpoints are, by design, unauthenticated public HTTP endpoints that only rely on this HMAC check). No secret, token, or privileged account for the *victim* shop is required — only the ability to send an HTTP request with a spoofed header, which any unprivileged internet user with a body/HMAC pair from their own installation can do. This is a realistic, low-effort replay, not a theoretical concern.

### Recommendation
Include the shop-identifying headers (at minimum `shop-domain`, and ideally `topic` and `webhook_id`) inside the bytes covered by `to_signable_string`, or independently bind/verify the `shop` header against an out-of-band trusted source (e.g., cross-check against the set of shops currently authorized/installed, or use a per-shop signing/verification path) before handing `WebhookMetadata` to a handler. At minimum, document loudly that `request.shop` is *not* authenticated by the HMAC and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
```ruby
require "shopify_api"
require "openssl"
require "base64"

ShopifyAPI::Context.setup(
  api_key: "key", api_secret_key: "secret", host: "example.com",
  scope: "read_products", is_embedded: false, is_private: false,
  api_version: "2024-01"
)

body = '{"id":123,"event":"legit"}'
hmac = Base64.encode64(
  OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), "secret", body)
)

# Legit webhook, captured by the attacker for THEIR OWN shop "attacker-shop.myshopify.com"
legit_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac,
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
}

# Replay with a spoofed shop-domain header, same body + same hmac
spoofed_headers = legit_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

req = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: spoofed_headers)

# Still validates successfully because `to_signable_string` never included shop-domain
ShopifyAPI::Utils::HmacValidator.validate(req) # => true

# Registry.process will call the handler with data.shop == "victim-shop.myshopify.com"
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
