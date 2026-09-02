### Title
Webhook `shop-domain` header is trusted by `WebhookHandler` without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via `Utils::HmacValidator.validate(request)`, but the HMAC signable string is defined as only the raw request body [1](#0-0) . The `shop` accessor, which is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header [2](#0-1) , is never included in that signed string. `Registry.process` accepts any request whose body+HMAC pair validates and then forwards `request.shop` unchanged into the `WebhookMetadata` struct that is delivered to the app's handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `hmac == HMAC(api_secret_key, body ++ shop)`, i.e. the tenant identity (`shop`) that the app trusts for a webhook must be cryptographically bound to the same signature that authenticates the payload. Instead, the gem implements:

- Before: `to_signable_string == raw_body` only [1](#0-0) 
- `shop` is read from a plain, unsigned header [2](#0-1) 
- After validation, `Registry.process` builds `WebhookMetadata` using `request.shop` as the trusted tenant identifier passed to `handler.handle` [3](#0-2) 

Because `Context.api_secret_key` is one shared secret per app (not per merchant/tenant) [4](#0-3) , any merchant who has installed the app can obtain a body+HMAC pair that is valid under that same secret (e.g. by triggering a webhook to their own shop and capturing the delivery, or by controlling body content that Shopify signs for their own store). That captured `(body, hmac)` pair remains valid for **any** value of the `shop-domain` header, since the header plays no role in `to_signable_string`. The `Request` class itself only checks that the header is *present*, not that it is bound to the signature [5](#0-4) .

This is the direct analog of the Hats Protocol bug class: a value that is acted upon (`shop`, used as the tenant identity for the handler) is not covered by the integrity check (`hmac`) that is supposed to make the whole message trustworthy — exactly like a child hat's properties being mutable by an admin that was never checked to exist/match.

### Impact Explanation
An app built on this gem that dispatches per-tenant logic based on `WebhookMetadata#shop` (the documented/intended purpose of the field, per `docs/usage/webhooks.md` and the `WebhookHandler` interface [6](#0-5) ) can be tricked into applying attacker-supplied body content under a victim shop's identity. This crosses the tenant boundary: data or state changes intended to be scoped to the attacker's own store can instead be attributed to/applied against a different merchant's store, meeting the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only:
1. Being an unprivileged internet user who has installed the target app on their own store (no special privileges, no access token theft, no `client_secret` needed).
2. Capturing one legitimate `(body, hmac)` webhook delivery sent to their own endpoint by Shopify (normal app operation).
3. Replaying that exact body+HMAC pair to the app's webhook endpoint with the `shop-domain` header swapped to the victim's `myshopify.com` domain.

No cryptographic secret is needed by the attacker since the signature check never varies with the `shop` header value. This is a straightforward, repeatable HTTP replay requiring no privileged access.

### Recommendation
Bind the shop identity into the signed material, or otherwise ensure `shop` cannot be varied independent of the signature:
```ruby
sig { override.returns(String) }
def to_signable_string
  # include shop in the value that must match the HMAC, or otherwise
  # cross-check the header against a value obtained through an authenticated channel
  @raw_body
end
```
At minimum, document and enforce that consumers of `WebhookMetadata#shop` must independently verify the shop is one for which they have an active, previously-established session/installation record before trusting body content scoped to it, and consider having `Registry.process` reject requests where the `shop` header does not match a known-installed shop for this app.

### Proof of Concept
```ruby
# Attacker owns "attacker.myshopify.com" and has installed the app.
# Shopify sends a legitimate webhook to the attacker's own endpoint:
#   body = '{"id":1,"note":"hello"}'
#   headers = {
#     "x-shopify-topic" => "orders/create",
#     "x-shopify-hmac-sha256" => <valid HMAC over body only>,
#     "x-shopify-shop-domain" => "attacker.myshopify.com",
#   }
# Attacker captures this (body, hmac) pair, then replays it to the app's
# webhook endpoint with a different shop header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac,       # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # swapped
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) still returns true because
#    to_signable_string only hashes @raw_body; handler.handle receives
#    WebhookMetadata(shop: "victim-shop.myshopify.com", body: captured_body, ...)
``` [1](#0-0) [3](#0-2)

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
